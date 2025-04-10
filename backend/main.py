from fastapi import FastAPI
import google.auth
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from fastapi.middleware.cors import CORSMiddleware

# FastAPI app
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or restrict to your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Google Sheets API authentication
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
SHEET_ID = '1ylZxBM7yyCzBeP7Hu-MfD88tE0QSKlkYibf58PQLWbc'  # Your Google Sheet ID
RANGE_NAME = 'Sheet2!B87:E92'  # The range you want to fetch

# Authenticate and build the service
def get_sheets_service():
    creds, _ = google.auth.load_credentials_from_file('credentials2.json', SCOPES)
    service = build('sheets', 'v4', credentials=creds)
    return service

@app.get("/google-sheets-data")
async def get_google_sheets_data():
    service = get_sheets_service()

    try:
        # Fetch data from Google Sheets API
        sheet = service.spreadsheets()
        result = sheet.values().get(spreadsheetId=SHEET_ID, range=RANGE_NAME).execute()
        values = result.get('values', [])

        # Format the data into rows
        rows = []
        for row in values:
            rows.append({"data": row})  # Adjust the structure as needed

        return {"rows": rows}
    except HttpError as err:
        return {"error": f"An error occurred: {err}"}
