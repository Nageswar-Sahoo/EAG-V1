import os
from mcp.server.fastmcp import FastMCP
from fastapi import FastAPI
import uvicorn
import logging
import datetime
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from dotenv import load_dotenv
import pandas as pd
import tempfile
import json

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(levelname)s - [%(name)s] - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('sheets_mcp_server.log')
    ]
)
logger = logging.getLogger(__name__)

# Google Sheets API configuration
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]

# Add test users who are allowed to access the application
AUTHORIZED_USERS = [
    'tech.nageswar@gmail.com'
]

def get_google_credentials():
    """Get or refresh Google API credentials"""
    creds = None
    token_path = 'token.json'
    
    try:
        if os.path.exists(token_path):
            creds = Credentials.from_authorized_user_file(token_path, SCOPES)
            logger.info("Found existing credentials")
        
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                logger.info("Refreshing expired credentials")
                creds.refresh(Request())
            else:
                logger.info("Initiating new OAuth flow")
                # Use a fixed port for consistency
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', 
                    SCOPES,
                    redirect_uri='http://localhost:64405'
                )
                
                # Configure the flow for testing
                flow.oauth2session.verify = False  # For testing only
                
                # Run the local server with the specific port
                creds = flow.run_local_server(
                    port=64405,
                    prompt='consent',
                    access_type='offline',
                    success_message='Authentication successful! You can close this window.',
                    authorization_prompt_message='Please login with an authorized test account.'
                )
                
                logger.info("New credentials obtained")
            
            # Save the credentials for the next run
            with open(token_path, 'w') as token:
                token.write(creds.to_json())
                logger.info("Credentials saved to token.json")
        
        # Verify the user is authorized
        if hasattr(creds, 'id_token') and creds.id_token:
            user_email = creds.id_token.get('email')
            if user_email not in AUTHORIZED_USERS:
                raise Exception(f"User {user_email} is not authorized to use this application")
            logger.info(f"Authorized user {user_email} authenticated successfully")
        
        return creds
        
    except Exception as e:
        logger.error(f"Error in authentication: {str(e)}")
        if os.path.exists(token_path):
            logger.info("Removing invalid token.json")
            os.remove(token_path)
        raise Exception(f"Authentication failed: {str(e)}")

def create_spreadsheet(service, title):
    """Create a new Google Spreadsheet"""
    spreadsheet = {
        'properties': {
            'title': title
        }
    }
    spreadsheet = service.spreadsheets().create(body=spreadsheet).execute()
    return spreadsheet['spreadsheetId']

def update_spreadsheet(service, spreadsheet_id, data):
    """Update spreadsheet with data"""
    # Convert data to DataFrame if it's not already
    if not isinstance(data, pd.DataFrame):
        data = pd.DataFrame([data])
    
    # Convert DataFrame to list of lists
    values = [data.columns.tolist()] + data.values.tolist()
    
    body = {
        'values': values
    }
    
    service.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id,
        range='A1',
        valueInputOption='RAW',
        body=body
    ).execute()

def share_spreadsheet(service, spreadsheet_id, email):
    """Share spreadsheet with user"""
    permission = {
        'type': 'user',
        'role': 'reader',
        'emailAddress': email
    }
    
    service.permissions().create(
        fileId=spreadsheet_id,
        body=permission,
        fields='id'
    ).execute()

def get_shareable_link(service, spreadsheet_id):
    """Get shareable link for spreadsheet"""
    file = service.files().get(
        fileId=spreadsheet_id,
        fields='webViewLink'
    ).execute()
    
    return file.get('webViewLink')

class SheetsMCP:
    def __init__(self):
        try:
            logger.info("Initializing SheetsMCP...")
            self.credentials = get_google_credentials()
            self.sheets_service = build('sheets', 'v4', credentials=self.credentials)
            self.drive_service = build('drive', 'v3', credentials=self.credentials)
            logger.info("SheetsMCP initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize SheetsMCP: {str(e)}")
            raise
        
    async def process_result(self, result: dict):
        """Process result and store in Google Sheets"""
        try:
            # Create timestamp for spreadsheet title
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            title = f"Agent_Result_{timestamp}"
            
            # Create new spreadsheet
            spreadsheet_id = create_spreadsheet(self.sheets_service, title)
            
            # Update spreadsheet with result
            update_spreadsheet(self.sheets_service, spreadsheet_id, result)
            
            # Get shareable link
            link = get_shareable_link(self.drive_service, spreadsheet_id)
            
            return {
                "status": "success",
                "spreadsheet_link": link,
                "spreadsheet_id": spreadsheet_id
            }
            
        except Exception as e:
            logger.error(f"Error processing result: {str(e)}")
            return {
                "status": "error",
                "message": str(e)
            }

# Create FastAPI app
app = FastAPI()

# Create MCP server
mcp = FastMCP(
    name="SheetsMCP",
    host="0.0.0.0",
    port=8051,
    app=app
)

# Initialize SheetsMCP
sheets_mcp = SheetsMCP()

@app.post("/process_result")
async def process_result(result: dict):
    """Endpoint to process result and store in Google Sheets"""
    return await sheets_mcp.process_result(result)

def run_server():
    """Run the MCP server"""
    try:
        logger.info("Starting Sheets MCP server on port 8051")
        uvicorn.run(app, host="0.0.0.0", port=8051)
    except Exception as e:
        logger.error(f"Error in Sheets MCP server: {str(e)}")

if __name__ == "__main__":
    run_server() 