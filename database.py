import sqlite3

DATABASE_NAME = "medication.db"


def get_connection():
    connection = sqlite3.connect(DATABASE_NAME)
    connection.row_factory = sqlite3.Row
    return connection


def create_tables():
    connection = get_connection()

    connection.execute("""
        CREATE TABLE IF NOT EXISTS patients (
            patient_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            age INTEGER,
            contact TEXT,
            timezone TEXT NOT NULL DEFAULT 'Asia/Kolkata'
        )
    """)

    connection.commit()
    connection.close()

    create_prescription_table()
    create_schedule_table()


def add_patient(name, age, contact, timezone):
    connection = get_connection()

    connection.execute("""
        INSERT INTO patients (name, age, contact, timezone)
        VALUES (?, ?, ?, ?)
    """, (name, age, contact, timezone))

    connection.commit()
    connection.close()


def get_all_patients():
    connection = get_connection()

    patients = connection.execute("""
        SELECT * FROM patients
        ORDER BY patient_id DESC
    """).fetchall()

    connection.close()

    return patients

def create_prescription_table():
    connection = get_connection()

    connection.execute("""
        CREATE TABLE IF NOT EXISTS prescriptions (
            prescription_id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER NOT NULL,
            medicine_name TEXT NOT NULL,
            dosage TEXT NOT NULL,
            frequency TEXT NOT NULL,
            start_date TEXT NOT NULL,
            end_date TEXT NOT NULL,
            start_time TEXT NOT NULL,

            FOREIGN KEY (patient_id)
                REFERENCES patients(patient_id)
        )
    """)

    connection.commit()
    connection.close()


def add_prescription(
        patient_id,
        medicine_name,
        dosage,
        frequency,
        start_date,
        end_date,
        start_time):

    connection = get_connection()

    cursor = connection.execute("""
        INSERT INTO prescriptions (
            patient_id,
            medicine_name,
            dosage,
            frequency,
            start_date,
            end_date,
            start_time
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        patient_id,
        medicine_name,
        dosage,
        frequency,
        start_date,
        end_date,
        start_time
    ))

    prescription_id = cursor.lastrowid

    connection.commit()
    connection.close()

    return prescription_id


def get_all_prescriptions():
    connection = get_connection()

    prescriptions = connection.execute("""
        SELECT
            prescriptions.*,
            patients.name AS patient_name
        FROM prescriptions

        JOIN patients
        ON prescriptions.patient_id = patients.patient_id

        ORDER BY prescription_id DESC
    """).fetchall()

    connection.close()

    return prescriptions 

# ================= Dose Schedule Table ==================

def create_schedule_table():

    connection = get_connection()

    connection.execute("""
        CREATE TABLE IF NOT EXISTS medication_schedule (

            schedule_id INTEGER PRIMARY KEY AUTOINCREMENT,

            prescription_id INTEGER NOT NULL,

            scheduled_datetime TEXT NOT NULL,

            status TEXT NOT NULL DEFAULT 'Pending',

            taken_datetime TEXT,

            FOREIGN KEY (prescription_id)
                REFERENCES prescriptions(prescription_id)
        )
    """)

    connection.commit()
    connection.close()


def add_schedule_dose(prescription_id, scheduled_datetime):

    connection = get_connection()

    connection.execute("""
        INSERT INTO medication_schedule (
            prescription_id,
            scheduled_datetime
        )
        VALUES (?, ?)
    """, (
        prescription_id,
        scheduled_datetime
    ))

    connection.commit()
    connection.close()



# ===================== Get Schedule From Database =====================

def get_all_schedule():

    connection = get_connection()

    schedule = connection.execute("""
        SELECT
            medication_schedule.schedule_id,
            medication_schedule.scheduled_datetime,
            medication_schedule.status,
            medication_schedule.taken_datetime,

            prescriptions.medicine_name,
            prescriptions.dosage,
            prescriptions.frequency,

            patients.name AS patient_name

        FROM medication_schedule

        JOIN prescriptions
        ON medication_schedule.prescription_id
            = prescriptions.prescription_id

        JOIN patients
        ON prescriptions.patient_id
            = patients.patient_id

        ORDER BY medication_schedule.scheduled_datetime ASC
    """).fetchall()

    connection.close()

    return schedule



# ============== 

def update_dose_status(schedule_id, status, taken_datetime=None):

    connection = get_connection()

    connection.execute("""
        UPDATE medication_schedule

        SET
            status = ?,
            taken_datetime = ?

        WHERE schedule_id = ?
    """, (
        status,
        taken_datetime,
        schedule_id
    ))

    connection.commit()
    connection.close()



# ===========

def get_medication_log():

    connection = get_connection()

    logs = connection.execute("""
        SELECT
            medication_schedule.schedule_id,
            medication_schedule.scheduled_datetime,
            medication_schedule.status,
            medication_schedule.taken_datetime,

            prescriptions.medicine_name,
            prescriptions.dosage,

            patients.name AS patient_name

        FROM medication_schedule

        JOIN prescriptions
        ON medication_schedule.prescription_id
            = prescriptions.prescription_id

        JOIN patients
        ON prescriptions.patient_id
            = patients.patient_id

        WHERE medication_schedule.status != 'Pending'

        ORDER BY medication_schedule.scheduled_datetime DESC
    """).fetchall()

    connection.close()

    return logs


def get_weekly_report():

    connection = get_connection()

    report = connection.execute("""
        SELECT
            patients.patient_id,
            patients.name AS patient_name,

            COUNT(medication_schedule.schedule_id) AS total_doses,

            SUM(
                CASE
                    WHEN medication_schedule.status = 'Taken'
                    THEN 1
                    ELSE 0
                END
            ) AS taken_doses,

            SUM(
                CASE
                    WHEN medication_schedule.status = 'Missed'
                    THEN 1
                    ELSE 0
                END
            ) AS missed_doses

        FROM patients

        JOIN prescriptions
        ON patients.patient_id = prescriptions.patient_id

        JOIN medication_schedule
        ON prescriptions.prescription_id =
           medication_schedule.prescription_id

        WHERE medication_schedule.status IN ('Taken', 'Missed')

        AND datetime(medication_schedule.scheduled_datetime)
            >= datetime('now', '-7 days')

        GROUP BY patients.patient_id, patients.name

        ORDER BY patients.name
    """).fetchall()

    connection.close()

    return report


