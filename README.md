# MediNest 💊
### Patient Medication Reminder and Adherence Log

MediNest is a web-based patient medication management system developed using Python Flask and SQLite. It helps users organize prescriptions, generate medication schedules, receive timely reminders, and track medication adherence.

## Features

- **Patient Management:** Add, edit, view, and delete patient records.
- **Prescription Management:** Create, update, and delete medication prescriptions.
- **Automatic Scheduling:** Generate medication schedules for once-daily, twice-daily, and every-eight-hour prescriptions.
- **Medication Reminders:** Receive browser notifications and in-app reminder popups before scheduled doses.
- **Adherence Tracking:** Record doses as Taken or Missed.
- **Dashboard:** View medication statistics and quick-access features.
- **Weekly Reports:** Review medication adherence and progress.
- **Responsive Interface:** Mocha & Sage themed interface designed for different screen sizes.

## Technologies Used

| Technology | Purpose |
|---|---|
| Python 3.14.6 | Backend programming |
| Flask 3.1.3 | Web framework |
| SQLite | Database |
| HTML | Webpage structure |
| CSS | Styling and responsive design |
| JavaScript | Frontend interactions and notifications |
| Git and GitHub | Version control |

## Installation and Setup

**1. Clone the repository**

```bash
git clone https://github.com/Eswar020/Patient-Medication-Reminder.git
cd Patient-Medication-Reminder
```

**2. Create a virtual environment**

```bash
python -m venv venv
```

**3. Activate the virtual environment**

On Windows:

```powershell
venv\Scripts\activate
```

**4. Install dependencies**

```bash
python -m pip install -r requirements.txt
```

**5. Start the application**

```bash
python app.py
```

**6. Open the website**

Visit:

`http://127.0.0.1:5000`

The application uses a local SQLite database. Patient and prescription data are stored locally and are not included in the GitHub repository.

## Medication Scheduling

MediNest supports three scheduling frequencies:

| Frequency | Scheduling Logic |
|---|---|
| Once Daily | One dose every 24 hours |
| Twice Daily | Two doses per day, 12 hours apart |
| Every 8 Hours | One dose every 8 hours |

Reminder times are calculated based on the scheduled dose time and the configured reminder offset.

## Application Modules

1. Dashboard
2. Patients
3. Prescriptions
4. Medication Schedule
5. Medication Log
6. Weekly Reports

## Important Notes

Browser notifications require notification permission and an open MediNest browser page. The current version does not provide SMS notifications or background mobile push notifications.

## Future Enhancements

- Mobile push notifications
- SMS and email reminders
- Improved timezone support
- Enhanced reporting and analytics
- Multi-user authentication

## Project Information

**Project:** Patient Medication Reminder and Adherence Log  
**Application Name:** MediNest  
**Category:** Digital Health  
**Framework:** Flask  
**Database:** SQLite

## Disclaimer

MediNest is an academic prototype intended to support medication schedule organization and adherence tracking. It is not a substitute for professional medical advice or clinical medication management.