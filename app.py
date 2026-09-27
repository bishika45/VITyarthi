# ===============================================
#  QR Code Attendance App - app.py  (FastAPI)
#  Install:  pip install -r requirements.txt
#  Run:      python app.py
# ===============================================

import base64
import io
import json
import os
import random
import socket
import string
import time
from datetime import datetime

import qrcode
import uvicorn
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

app = FastAPI()
PORT = 8000
DATA_FILE = "attendance.json"  # attendance is saved here
QR_SECONDS = 60     # a new QR every 60 seconds
FORM_SECONDS = 120  # after a good scan, student has 2 minutes to submit


# -----------------------------------------------
# 1. The secret code (token) that changes every minute
# -----------------------------------------------
def make_code():
    # random text like "k3j9x2"
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=6))


current_token = make_code()
token_made_at = time.time()


def get_current_token():
    # If the token is older than 60 seconds, throw it away and make a new one.
    # The old token is NOT kept, so a photo of an old QR stops working.
    global current_token, token_made_at
    if time.time() - token_made_at >= QR_SECONDS:
        current_token = make_code()
        token_made_at = time.time()
        print("New QR token:", current_token)
    return current_token


def seconds_left():
    return int(QR_SECONDS - (time.time() - token_made_at))


# When a student scans a fresh QR, we give them a one-time "pass"
# so they have time to type their name. { pass: expiry_time }
passes = {}


# -----------------------------------------------
# 2. Helpers to load / save attendance
# -----------------------------------------------
def load_attendance():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r") as f:
        return json.load(f)


def save_attendance(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)


def today():
    return datetime.now().strftime("%Y-%m-%d")  # "2026-09-25"


def get_local_ip():
    # Finds this computer's Wi-Fi IP (e.g. 192.168.1.5) so phones can reach it
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    except OSError:
        return "localhost"
    finally:
        s.close()


BASE_URL = f"http://{get_local_ip()}:{PORT}"


# What the student form sends to us
class Student(BaseModel):
    name: str
    roll: str
    pass_code: str = ""


# -----------------------------------------------
# 3. Routes (URLs)
# -----------------------------------------------
@app.get("/")
def home():
    return FileResponse("public/display.html")


# The display page asks for this to get the QR image
@app.get("/api/qr")
def get_qr():
    token = get_current_token()
    link = f"{BASE_URL}/mark.html?token={token}"

    # make QR image and turn it into text the browser can show
    img = qrcode.make(link)
    buffer = io.BytesIO()
    img.save(buffer, format="PNG") # type: ignore
    image = "data:image/png;base64," + base64.b64encode(buffer.getvalue()).decode()

    return {"image": image, "link": link, "seconds_left": seconds_left()}


# The form page calls this right after the student scans.
# Only the QR on the screen RIGHT NOW is accepted.
@app.get("/api/scan")
def scan(token: str):
    if token != get_current_token():
        return {"ok": False, "message": "This QR code has expired. Scan the one on the screen."}

    pass_code = make_code() + make_code()
    passes[pass_code] = time.time() + FORM_SECONDS
    return {"ok": True, "pass_code": pass_code}


# The student's form sends name + roll no + pass here
@app.post("/api/mark")
def mark(student: Student):
    name = student.name.strip()
    roll = student.roll.strip()

    # Check 1: all fields filled
    if not name or not roll:
        return {"ok": False, "message": "Please fill name and roll no."}

    # Check 2: pass is real and not too old
    expiry = passes.get(student.pass_code)
    if expiry is None or time.time() > expiry:
        return {"ok": False, "message": "Time over. Please scan the QR again."}

    # Check 3: not already marked today
    records = load_attendance()
    for s in records:
        if s["roll"] == roll and s["date"] == today():
            return {"ok": False, "message": f"Roll no {roll} is already marked today."}

    # All good - save it
    records.append({
        "name": name,
        "roll": roll,
        "date": today(),
        "time": datetime.now().strftime("%I:%M:%S %p"),
    })
    save_attendance(records)
    del passes[student.pass_code]  # a pass can be used only once

    return {"ok": True, "message": f"Present marked for {name}!"}


# Display page reads today's list from here
@app.get("/api/list")
def get_list():
    return [s for s in load_attendance() if s["date"] == today()]


# Serve the HTML/CSS files in the "public" folder (keep this after the routes)
app.mount("/", StaticFiles(directory="public"), name="public")


# -----------------------------------------------
# 4. Start the server
# -----------------------------------------------
if __name__ == "__main__":
    print("===========================================")
    print(" Attendance app is running!")
    print(" Open this on the display device:")
    print(" " + BASE_URL)
    print("===========================================")

    # host="0.0.0.0" lets phones on the same Wi-Fi connect
    uvicorn.run(app, host="0.0.0.0", port=PORT)
