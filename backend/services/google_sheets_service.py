# services/google_sheets_service.py

import google.auth
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from typing import List, Dict

# Google Sheets API authentication
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
SHEET_ID = '1ylZxBM7yyCzBeP7Hu-MfD88tE0QSKlkYibf58PQLWbc'  # Your Google Sheet ID
RANGE_NAME = 'Sheet2!B87:E92'  # The range you want to fetch

# Authenticate and build the service
def get_sheets_service():
    creds, _ = google.auth.load_credentials_from_file('credentials.json', SCOPES)
    service = build('sheets', 'v4', credentials=creds)
    return service

# Function to retrieve data from Google Sheets
async def get_google_sheets_data() -> List[Dict[str, str]]:
    service = get_sheets_service()

    try:
        # Fetch data from Google Sheets API
        sheet = service.spreadsheets()
        result = sheet.values().get(spreadsheetId=SHEET_ID, range=RANGE_NAME).execute()
        values = result.get('values', [])

        # Format the data into rows
        rows = [{"data": row} for row in values]

        return rows
    except HttpError as err:
        raise Exception(f"An error occurred: {err}")
