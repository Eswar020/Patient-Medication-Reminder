from datetime import datetime, timedelta


def generate_schedule(start_date, end_date, start_time, frequency):

    start_datetime = datetime.strptime(
        f"{start_date} {start_time}",
        "%Y-%m-%d %H:%M"
    )

    end_datetime = datetime.strptime(
        f"{end_date} 23:59",
        "%Y-%m-%d %H:%M"
    )

    schedule = []

    # ONCE DAILY
    if frequency == "once_daily":

        current = start_datetime

        while current <= end_datetime:

            schedule.append(current)

            current += timedelta(days=1)

    # TWICE DAILY
    elif frequency == "twice_daily":

        current = start_datetime

        while current <= end_datetime:

            schedule.append(current)

            second_dose = current + timedelta(hours=12)

            if second_dose <= end_datetime:
                schedule.append(second_dose)

            current += timedelta(days=1)

    # EVERY 8 HOURS
    elif frequency == "every_8_hours":

        current = start_datetime

        while current <= end_datetime:

            schedule.append(current)

            current += timedelta(hours=8)

    return schedule