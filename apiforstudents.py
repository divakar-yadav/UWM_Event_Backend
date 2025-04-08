import pandas as pd
import requests
from datetime import date

EXCEL_PATH = "/Users/xavier/Desktop/UWMCAPSTONE/2025rpc.xlsx"
API_URL = "http://127.0.0.1:8000/api/home/students/create/"
USE_PROD = False
TOKEN = "token"

df = pd.read_excel(EXCEL_PATH).fillna("")

headers = {"Content-Type": "application/json"}
if USE_PROD:
    API_URL = "https://api.uwmsrpc.com/api/home/students/create/"
    headers["Authorization"] = f"Bearer {TOKEN}"

for index, row in df.iterrows():
    payload = {
        "date": str(date.today()),
        "department": row.get("Department", ""),
        "academic_status": row.get("Category", ""),
        "first_name": row.get("First Name", ""),
        "last_name": row.get("Last Name", ""),
        "phonetic_spelling": row.get("Phonetic spelling", ""),
        "research_adviser_first_name": row.get("Research adviser first name", ""),
        "research_adviser_last_name": row.get("Research adviser last name", ""),
        "research_adviser_email": row.get("Research adviser email", ""),
        "poster_title": row.get("Title", ""), 
        "jacket_size": row.get("Jacket size", ""),
        "jacket_gender": row.get("Jacket gender", ""),
        "poster_ID": row.get("Poster ID"),
        "Name": f"{row.get('First Name', '')} {row.get('Last Name', '')}".strip(),
        "email": row.get("email", ""),
        "scored_By_Judges": None,
        "finalist": False
    }

    response = requests.post(API_URL, json=payload, headers=headers)

    if response.status_code != 201:
        print(f"ERROR Row {index + 1}: {payload['Name']} => {response.status_code}")
        print("     Error:", response.text)
    else:
        print(f"Success Row {index + 1}: {payload['Name']} inserted.")
