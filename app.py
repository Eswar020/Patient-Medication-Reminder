from flask import Flask, render_template, request, redirect, url_for, jsonify
from datetime import datetime, timedelta


import database
import scheduler








app = Flask(__name__)

# Create database tables when application starts
database.create_tables()



@app.route("/")
def home():

    # Retrieve dashboard statistics from SQLite
    stats = database.get_dashboard_stats()

    return render_template(
        "index.html",
        stats=stats
    )



@app.route("/patients")
def patients():
    patient_list = database.get_all_patients()

    return render_template(
        "patients.html",
        patients=patient_list
    )


@app.route("/patients/add", methods=["POST"])
def add_patient():

    name = request.form.get("name")
    age = request.form.get("age")
    contact = request.form.get("contact")
    timezone = request.form.get("timezone")

    if not name:
        return "Patient name is required.", 400

    database.add_patient(
        name,
        age,
        contact,
        timezone
    )

    return redirect(url_for("patients"))

@app.route("/prescriptions")
def prescriptions():

    patient_list = database.get_all_patients()
    prescription_list = database.get_all_prescriptions()

    return render_template(
        "prescriptions.html",
        patients=patient_list,
        prescriptions=prescription_list
    )


@app.route("/prescriptions/add", methods=["POST"])
def add_prescription():

    patient_id = request.form.get("patient_id")
    medicine_name = request.form.get("medicine_name")
    dosage = request.form.get("dosage")
    frequency = request.form.get("frequency")
    start_date = request.form.get("start_date")
    end_date = request.form.get("end_date")
    start_time = request.form.get("start_time")
    reminder_minutes = request.form.get("reminder_minutes")

    if not all([
        patient_id,
        medicine_name,
        dosage,
        frequency,
        start_date,
        end_date,
        start_time,
        reminder_minutes
    ]):
        return "All prescription fields are required.", 400

    if end_date < start_date:
        return "End date cannot be before start date.", 400

    prescription_id = database.add_prescription(
        patient_id,
        medicine_name,
        dosage,
        frequency,
        start_date,
        end_date,
        start_time,
        reminder_minutes
    )

    dose_schedule = scheduler.generate_schedule(
        start_date,
        end_date,
        start_time,
        frequency
    )

    for dose in dose_schedule:

        reminder_time = dose - timedelta(
            minutes=int(reminder_minutes)
        )

        database.add_schedule_dose(
            prescription_id,
            dose.strftime("%Y-%m-%d %H:%M"),
            reminder_time.strftime("%Y-%m-%d %H:%M")
        )



    return redirect(url_for("prescriptions"))


@app.route("/schedule")
def medication_schedule():

    schedule = database.get_all_schedule()

    return render_template(
        "schedule.html",
        schedule=schedule
    )



@app.route("/schedule/<int:schedule_id>/taken", methods=["POST"])
def mark_taken(schedule_id):

    taken_time = datetime.now().strftime("%Y-%m-%d %H:%M")

    database.update_dose_status(
        schedule_id,
        "Taken",
        taken_time
    )

    return redirect(url_for("medication_schedule"))


@app.route("/schedule/<int:schedule_id>/missed", methods=["POST"])
def mark_missed(schedule_id):

    database.update_dose_status(
        schedule_id,
        "Missed"
    )

    return redirect(url_for("medication_schedule"))


@app.route("/medication-log")
def medication_log():

    logs = database.get_medication_log()

    return render_template(
        "medication_log.html",
        logs=logs
    )



@app.route("/reports")
def reports():

    report_data = database.get_weekly_report()

    weekly_reports = []

    for report in report_data:

        total = report["total_doses"]
        taken = report["taken_doses"]
        missed = report["missed_doses"]

        if total > 0:
            adherence = (taken / total) * 100
        else:
            adherence = 0

        weekly_reports.append({
            "patient_id": report["patient_id"],
            "patient_name": report["patient_name"],
            "total_doses": total,
            "taken_doses": taken,
            "missed_doses": missed,
            "adherence": round(adherence, 1)
        })

    return render_template(
        "reports.html",
        reports=weekly_reports
    )



@app.route("/api/reminders")
def check_reminders():

    current_time = datetime.now().strftime("%Y-%m-%d %H:%M")

    database.mark_overdue_doses_as_missed(
        current_time
    )

    reminder_list = []


    # ==================================
    # 1. EARLY REMINDERS
    # ==================================

    early_reminders = database.get_due_reminders(
        current_time
    )

    for reminder in early_reminders:

        reminder_list.append({
            "schedule_id": reminder["schedule_id"],
            "reminder_type": "early",
            "patient_name": reminder["patient_name"],
            "medicine_name": reminder["medicine_name"],
            "dosage": reminder["dosage"],
            "scheduled_datetime": reminder["scheduled_datetime"],
            "reminder_minutes": reminder["reminder_minutes"]
        })

        database.mark_reminder_sent(
            reminder["schedule_id"]
        )


    # ==================================
    # 2. DOSE-TIME REMINDERS
    # ==================================

    dose_reminders = database.get_due_dose_reminders(
        current_time
    )

    for reminder in dose_reminders:

        reminder_list.append({
            "schedule_id": reminder["schedule_id"],
            "reminder_type": "dose_time",
            "patient_name": reminder["patient_name"],
            "medicine_name": reminder["medicine_name"],
            "dosage": reminder["dosage"],
            "scheduled_datetime": reminder["scheduled_datetime"]
        })

        database.mark_dose_reminder_sent(
            reminder["schedule_id"]
        )


    return jsonify(reminder_list)





@app.route("/prescriptions/<int:prescription_id>/edit")
def edit_prescription(prescription_id):

    prescription = database.get_prescription_by_id(
        prescription_id
    )

    if prescription is None:
        return "Prescription not found.", 404

    patients = database.get_all_patients()

    return render_template(
        "edit_prescription.html",
        prescription=prescription,
        patients=patients
    )






@app.route("/prescriptions/<int:prescription_id>/update", methods=["POST"])
def update_prescription(prescription_id):

    prescription = database.get_prescription_by_id(prescription_id)

    if prescription is None:
        return "Prescription not found.", 404

    # Keep patient unchanged to protect patient history.
    patient_id = prescription["patient_id"]

    medicine_name = request.form.get("medicine_name", "").strip()
    dosage = request.form.get("dosage", "").strip()
    frequency = request.form.get("frequency", "").strip()
    start_date = request.form.get("start_date", "").strip()
    end_date = request.form.get("end_date", "").strip()
    start_time = request.form.get("start_time", "").strip()
    reminder_minutes = request.form.get("reminder_minutes", "").strip()

    if not all([
        medicine_name, dosage, frequency,
        start_date, end_date, start_time, reminder_minutes
    ]):
        return "All prescription fields are required.", 400

    if frequency not in ("once_daily", "twice_daily", "every_8_hours"):
        return "Invalid frequency.", 400

    if reminder_minutes not in ("5", "10", "15"):
        return "Invalid reminder interval.", 400

    try:
        start = datetime.strptime(start_date, "%Y-%m-%d").date()
        end = datetime.strptime(end_date, "%Y-%m-%d").date()
        datetime.strptime(start_time, "%H:%M")
    except ValueError:
        return "Invalid date or time.", 400

    if end < start:
        return "End date cannot be before start date.", 400

    # Generate the updated schedule.
    generated_doses = scheduler.generate_schedule(
        start_date,
        end_date,
        start_time,
        frequency
    )

    now = datetime.now()
    new_doses = []

    for dose in generated_doses:
        # Only regenerate future doses.
        if dose <= now:
            continue

        reminder_time = dose - timedelta(
            minutes=int(reminder_minutes)
        )

        new_doses.append((
            dose.strftime("%Y-%m-%d %H:%M"),
            reminder_time.strftime("%Y-%m-%d %H:%M")
        ))

    database.update_prescription_and_schedule(
        prescription_id,
        patient_id,
        medicine_name,
        dosage,
        frequency,
        start_date,
        end_date,
        start_time,
        int(reminder_minutes),
        new_doses
    )

    return redirect(url_for("prescriptions"))



if __name__ == "__main__":
    app.run(debug=True)