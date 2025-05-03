import os
from mcp.server.fastmcp import FastMCP
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - [%(name)s] - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('email_mcp_server.log')
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Email configuration
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = os.getenv('GMAIL_ADDRESS')
SENDER_PASSWORD = os.getenv('GMAIL_APP_PASSWORD')

# Validate email credentials
if not SENDER_EMAIL or not SENDER_PASSWORD:
    raise ValueError("Email credentials not found in environment variables!")

# Create an MCP server
mcp = FastMCP("EmailMCP", host="0.0.0.0", port=8052)

@mcp.tool()
async def send_email(recipient_email: str, subject: str = "AI Assistant Results", content: dict = None) -> dict:
    """Send email with the Google Sheets result
    
    Args:
        recipient_email: Email address of the recipient
        subject: Email subject line (optional)
        content: Dictionary containing email content (optional)
    
    Returns:
        Dictionary containing status and message
    """
    try:
        if not recipient_email:
            raise ValueError("Recipient email is required")
            
        if content is None:
            content = {}

        # Create message
        message = MIMEMultipart()
        message["From"] = SENDER_EMAIL
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
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.send_message(message)

        success_msg = f"Email sent successfully to {recipient_email}"
        logger.info(success_msg)
        return {
            "status": "success",
            "message": success_msg
        }

    except Exception as e:
        error_msg = f"Failed to send email: {str(e)}"
        logger.error(error_msg)
        return {
            "status": "error",
            "message": error_msg
        }

if __name__ == "__main__":
    # Run with SSE transport
    mcp.run(transport="sse") 