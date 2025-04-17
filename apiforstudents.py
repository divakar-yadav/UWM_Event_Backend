import pandas as pd
import requests
from datetime import date,datetime

EVENT_DATETIME = datetime(2025, 4, 16, 11, 0) # 11:00 AM CST on April 16, 2025
if datetime.now() >= EVENT_DATETIME:
    print("Student ingestion is disabled after the event starts.")
    exit()

EXCEL_PATH = "/Users/xavier/Desktop/UWMCAPSTONE/2025rpc.xlsx"
API_URL = "http://127.0.0.1:8000/api/home/students/create/"
USE_PROD = False
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzQ0ODQ4OTU5LCJpYXQiOjE3NDQ4MzA5NTksImp0aSI6IjM3NjNkMGFlOTdhYzQ1NzJhMjk0YTMxYmMzY2VjNDc4IiwidXNlcl9pZCI6NX0.2ObkTHG1CLIyoebb_26FStb1CbRDqh_Ns9TSHIJhoIg"

df = pd.read_excel(EXCEL_PATH).fillna("")

def smart_title(text):
    if not isinstance(text, str):
        return text
    words = text.split()
    result = []
    for w in words:
        if w.isupper():
            result.append(w) 
        else:
            result.append(w.capitalize())  
    return " ".join(result)

def title_case(text):
    #  "jOHN doe" -> "John Doe"
    return text.title() if isinstance(text, str) else text

def lower_case(text):
    # "JOHN.DOE@UWM.EDU" -> "john.doe@uwm.edu"
    return text.lower() if isinstance(text, str) else text
for col in ["First Name", "Last Name", "Phonetic spelling", "Research adviser first name", "Research adviser last name"]:
    if col in df.columns:
        df[col] = df[col].apply(title_case)  # E.g. "aLIce" -> "Alice"

if "Title" in df.columns:
    df["Title"] = df["Title"].apply(smart_title)  #  "QUANTUM CIRCUIT DESIGN" -> "Quantum circuit design"

if "email" in df.columns:
    df["email"] = df["email"].apply(lower_case)

if "Research adviser email" in df.columns:
    df["Research adviser email"] = df["Research adviser email"].apply(lower_case)



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
