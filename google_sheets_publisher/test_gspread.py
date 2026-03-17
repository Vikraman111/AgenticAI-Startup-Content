import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
import traceback
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Spreadsheet details
SHEET_ID = os.environ.get("GOOGLE_SHEET_ID")
CREDS_FILE = "google_sheets_credentials.json"

scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']

try:
    print(f"Connecting with {CREDS_FILE}...")
    creds = ServiceAccountCredentials.from_json_keyfile_name(CREDS_FILE, scope)
    client = gspread.authorize(creds)
    
    print(f"Attempting to open spreadsheet: {SHEET_ID}")
    spreadsheet = client.open_by_key(SHEET_ID)
    print(f"✅ Success! Connected to: {spreadsheet.title}")
    
    sheet = spreadsheet.sheet1
    print(f"✅ Sheet1 is accessible. Current row count: {len(sheet.get_all_values())}")

except Exception as e:
    print(f"❌ ERROR: {e}")
    traceback.print_exc()
    if "403" in str(e):
        print("\nDIAGNOSIS:")
        print("This is definitely a permission error. Double-check:")
        print(f"1. Did you share the sheet with precisely this email?: agentic-publisher@agentic-content.iam.gserviceaccount.com")
        print("2. Is the 'Google Drive API' enabled in your Google Cloud console?")
        print("3. Is the 'Google Sheets API' enabled in your Google Cloud console?")
