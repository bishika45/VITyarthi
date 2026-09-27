# QR Attendance System

## Project Overview

QR Attendance System is a lightweight web-based attendance application built with Python and FastAPI. It allows a laptop or projector to display a QR code that changes every 60 seconds. Students scan the current QR code using their phone, enter their name and roll number, and submit their attendance.

The system verifies the QR code, generates a one-time submission pass, prevents duplicate attendance for the same roll number on the same day, and displays a live list of students who are marked present.

## Features

- QR code automatically changes every 60 seconds
- Only the currently displayed QR code is accepted
- Students can scan the QR directly from their phone
- Simple form for name and roll number
- One-time pass after a valid QR scan
- 2-minute submission window after scanning
- Prevents the same roll number from being marked twice on the same day
- Live attendance list on the display screen
- Attendance is stored in `attendance.json`
- Works across devices connected to the same Wi-Fi network

## Technology Stack

- **Python 3.10+** – Backend programming
- **FastAPI** – Web framework and API handling
- **Uvicorn** – ASGI server
- **QRCode** – QR code generation
- **HTML** – Web page structure
- **CSS** – Styling
- **JavaScript** – API requests, countdown, and live updates
- **JSON** – Simple attendance data storage

## Project Structure

```text
qr-attendance/
│
├── app.py
├── requirements.txt
├── README.md
├── attendance.json              # Created automatically
│
├── public/
│   ├── display.html             # QR display + live attendance list
│   ├── mark.html                # Student attendance form
│   └── style.css                # Page styling
│
└── docs/
    └── LEARNING.md              # Beginner-friendly explanation
```

## How It Works

### 1. QR Code Generation

When the application starts, the server creates a random 6-character token. A new token is generated every 60 seconds.

The current token is converted into a QR code containing the attendance link.

### 2. Student Scans the QR

When a student scans the QR code, `mark.html` sends the token to the server.

The server checks whether the token matches the QR code currently displayed on the screen.

If the QR has expired, the student is asked to scan the latest QR code.

### 3. One-Time Pass

After a valid scan, the server generates a temporary pass code.

The student gets 2 minutes to enter their name and roll number and submit the form.

The pass is deleted after successful attendance, so it cannot be reused.

### 4. Attendance Validation

Before saving attendance, the server checks:

- Name and roll number are filled in
- The temporary pass is valid
- The same roll number has not already been marked today

### 5. Live Attendance List

The display page requests the current attendance list from the server every 3 seconds, so newly marked students appear automatically.

## Main Pages

### `display.html`

Used on the classroom display device.

It shows:

- Current QR code
- Countdown timer
- Number of students present
- Live attendance table

### `mark.html`

Opened on the student's phone after scanning the QR code.

It provides:

- Name input
- Roll number input
- Submit button
- Attendance status message

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Opens the display page |
| GET | `/api/qr` | Returns the current QR image, link, and remaining time |
| GET | `/api/scan?token=...` | Validates a QR token and creates a one-time pass |
| POST | `/api/mark` | Marks a student present |
| GET | `/api/list` | Returns today's attendance list |

FastAPI also provides interactive API documentation at:

```text
http://localhost:8000/docs
```

## Installation

Make sure Python 3.10 or newer is installed.


Install the required packages:

```bash
pip install -r requirements.txt
```

## Running the Project

Start the server:

```bash
python app.py
```

The terminal will display an address similar to:

```text
===========================================
 Attendance app is running!
 Open this on the display device:
 http://192.168.1.9:8000
===========================================
```

Open the displayed address in a browser on the laptop/projector.

Students can then scan the QR code using their phone camera.

> **Important:** The display computer and student phones should be connected to the same Wi-Fi network.

### Windows Firewall

The first time you run the application, Windows may ask whether Python should be allowed through the firewall. Allow access so other devices on the same network can connect to the server.

## Configuration

The main settings can be changed at the top of `app.py`:

| Setting | Default | Purpose |
|---------|---------|---------|
| `PORT` | `8000` | Port used by the server |
| `QR_SECONDS` | `60` | QR validity period |
| `FORM_SECONDS` | `120` | Student submission time |
| `DATA_FILE` | `attendance.json` | Attendance storage file |

## Data Storage

Attendance records are stored locally in:

```text
attendance.json
```

Each record contains:

```json
{
  "name": "Student Name",
  "roll": "12345",
  "date": "2026-09-27",
  "time": "04:30:15 PM"
}
```

## Known Limitations

- A screenshot or photo of the current QR can still be shared while that QR is valid.
- Temporary scan passes are stored in memory and are cleared when the server restarts.
- There is currently no teacher/admin login system.
- Attendance data is stored in a local JSON file rather than a database.
- The application is intended for use on a trusted local network.

## Future Improvements

- Teacher/admin login
- Database support with SQLite or MySQL
- Attendance reports and analytics
- Export attendance to CSV/Excel
- Search and filter attendance records
- Student registration and class management
- Stronger authentication and session management
- Cloud deployment for access from outside the local network

## Learning Resources

For a step-by-step explanation of how the project works, see:

```text
docs/LEARNING.md
```

## Author

**Bhoomi Singh**

---

If you find this project useful, consider giving the repository a star.