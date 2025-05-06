import pandas as pd
import requests
from datetime import datetime

EXCEL_PATH = "/Users/xavier/Desktop/UWMCAPSTONE/SRPCjudges.xlsx"
API_URL = "http://127.0.0.1:8000/api/signup/"
USE_PROD = False
TOKEN = "token_here"  

REGISTRATION_DEADLINE = datetime(2025, 4, 25, 11, 0)
if datetime.now() >= REGISTRATION_DEADLINE:
    print("Judge registration is disabled after the deadline.")
    exit()

df = pd.read_excel(EXCEL_PATH).fillna("")


def title_case(text):
    return text.title() if isinstance(text, str) else text

def lower_case(text):
    return text.lower() if isinstance(text, str) else text

for col in ["First Name", "Last Name"]:
    if col in df.columns:
        df[col] = df[col].apply(title_case)

if "email" in df.columns:
    df["email"] = df["email"].apply(lower_case)

headers = {"Content-Type": "application/json"}
if USE_PROD:
    API_URL = "https://api.uwmsrpc.com/api/signup/"
    headers["Authorization"] = f"Bearer {TOKEN}"


for index, row in df.iterrows():
    password = f"{row['Last Name'].strip().lower()}2025"
    email = row.get("email", "").strip().lower()
    payload = {
        "first_name": row.get("First Name", ""),
        "last_name": row.get("Last Name", ""),
        "title": row.get("Title", ""),
        "company": row.get("Organization", ""),
        "alumni": bool(row.get("alumni", False)),
        "year": row.get("year", ""),
        "degree": row.get("degree", ""),
        "email": row.get("email", ""),
        "password": password,
    }

    response = requests.post(API_URL, json=payload, headers=headers)
    if response.status_code == 400 and "User already exists" in response.text:
        print(f"⚠️ SKIPPED Row {index + 1}: {email} already exists.")
        continue
    if response.status_code != 201:
        print(f"❌ ERROR Row {index + 1}: {payload['email']} => {response.status_code}")
        print("    ↳", response.text)
    else:
        print(f"✅ Success Row {index + 1}: {payload['email']} registered.")
