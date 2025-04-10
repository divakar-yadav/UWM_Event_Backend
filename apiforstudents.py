import pandas as pd
import requests
from datetime import date

EXCEL_PATH = "/Users/divakaryadav/Documents/SRPC_DATA/2025rpc.xlsx"
API_URL = "https://api.uwmsrpc.com/api/home/students/create"
USE_PROD = True
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzQ0MTA3MzI4LCJpYXQiOjE3NDQwODkzMjgsImp0aSI6IjcwMWViODc4ZDJhMDQ4NGJiNmMzODUzZjM4NTIyZDI5IiwidXNlcl9pZCI6M30.RV2laLadhmaosVQVMyPavcaKmHmw1K89ogmVhimO8mo"
def sentence_case(text):
    # "MY RESEARCH POSTER" -> "My research poster"
    return text.capitalize() if isinstance(text, str) else text

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
    df["Title"] = df["Title"].apply(sentence_case)  #  "QUANTUM CIRCUIT DESIGN" -> "Quantum circuit design"

if "email" in df.columns:
    df["email"] = df["email"].apply(lower_case)

if "Research adviser email" in df.columns:
    df["Research adviser email"] = df["Research adviser email"].apply(lower_case)

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
