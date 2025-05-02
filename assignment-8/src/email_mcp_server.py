import os
from mcp.server.fastmcp import FastMCP
from fastapi import FastAPI
import uvicorn
import logging
import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(levelname)s - [%(name)s] - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('email_mcp_server.log')
    ]
)
logger = logging.getLogger(__name__)

# Email configuration
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = os.getenv('GMAIL_ADDRESS')
SENDER_PASSWORD = os.getenv('GMAIL_APP_PASSWORD')  # Use App Password, not regular password

class EmailMCP:
    def __init__(self):
        if not SENDER_EMAIL or not SENDER_PASSWORD:
            raise ValueError("Email credentials not found in environment variables!")
        self.sender_email = SENDER_EMAIL
        self.sender_password = SENDER_PASSWORD
        
    async def send_email(self, recipient_email: str, subject: str, content: dict) -> dict:
        """Send email with the Google Sheets result"""
        try:
            # Create message
            message = MIMEMultipart()
            message["From"] = self.sender_email
            message["To"] = recipient_email
            message["Subject"] = subject

            # Create HTML body
            html_content = f"""
            <html>
                <body>
                    <h2>Query Results</h2>
                    <p><strong>Query:</strong> {content.get('query', 'N/A')}</p>
                    <p><strong>Answer:</strong> {content.get('answer', 'N/A')}</p>
                    <p><strong>Spreadsheet Link:</strong> <a href="{content.get('spreadsheet_link', '#')}">View Results</a></p>
                    <p><strong>Session ID:</strong> {content.get('session_id', 'N/A')}</p>
                    <p><strong>Timestamp:</strong> {content.get('timestamp', 'N/A')}</p>
                    <hr>
                    <p>This is an automated message from your AI Assistant.</p>
                </body>
            </html>
            """
            
            # Attach HTML content
            html_part = MIMEText(html_content, "html")
            message.attach(html_part)

            # Send email
            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.send_message(message)

            logger.info(f"Email sent successfully to {recipient_email}")
            return {
                "status": "success",
                "message": f"Email sent successfully to {recipient_email}"
            }

        except Exception as e:
            error_msg = f"Failed to send email: {str(e)}"
            logger.error(error_msg)
            return {
                "status": "error",
                "message": error_msg
            }

# Create FastAPI app
app = FastAPI()

# Create MCP server
mcp = FastMCP(
    name="EmailMCP",
    host="0.0.0.0",
    port=8052,  # Different port from SheetsMCP
    app=app
)

# Initialize EmailMCP
email_mcp = EmailMCP()

@app.post("/send_email")
async def send_email(data: dict):
    """Endpoint to send email notification"""
    recipient_email = data.get("recipient_email")
    if not recipient_email:
        return {"status": "error", "message": "Recipient email is required"}
    
    subject = data.get("subject", "AI Assistant Results")
    content = data.get("content", {})
    
    return await email_mcp.send_email(recipient_email, subject, content)

def run_server():
    """Run the MCP server"""
    try:
        logger.info("Starting Email MCP server on port 8052")
        uvicorn.run(app, host="0.0.0.0", port=8052)
    except Exception as e:
        logger.error(f"Error in Email MCP server: {str(e)}")

if __name__ == "__main__":
    run_server() 