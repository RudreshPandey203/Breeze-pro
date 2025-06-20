import imaplib
import email
from email.header import decode_header

# Function to decode email headers
def mail_fetch(input):
    def decode_subject(subject):
        decoded = decode_header(subject)[0][0]
        if isinstance(decoded, bytes):
            return decoded.decode('utf-8')
        else:
            return decoded

    # IMAP server configuration
    IMAP_SERVER = 'imap.gmail.com'
    IMAP_PORT = 993
    EMAIL_ADDRESS = 'shraddha.mahapatra198@gmail.com'
    PASSWORD = 'oyei zprw fzxu ffaj'
    SEARCH_TEXT = input  # Text to search for in subject or sender

    # Connect to the IMAP server
    mail = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT)

    # Login to the server
    mail.login(EMAIL_ADDRESS, PASSWORD)

    # Select the inbox
    mail.select('inbox')

    # Search for emails containing the keyword "exciting" in the body, name, or subject
    status, email_ids = mail.search(None, f'(OR BODY "{SEARCH_TEXT}" FROM "{SEARCH_TEXT}" SUBJECT "{SEARCH_TEXT}")')

    if status == 'OK':
        email_ids = email_ids[0].split()
        print("Number of Emails Found:", len(email_ids))  # Debugging statement

        for email_id in email_ids:
            # Fetch the email
            status, email_data = mail.fetch(email_id, '(RFC822)')
            print("Fetch Status:", status)  # Debugging statement
            
            if status == 'OK':
                raw_email = email_data[0][1]

                # Ensure raw_email is bytes
                if isinstance(raw_email, bytes):
                    # Parse the raw email
                    msg = email.message_from_bytes(raw_email)
                else:
                    # Parse the raw email by encoding it to bytes
                    msg = email.message_from_bytes(raw_email.encode('utf-8'))

                # Extract email headers
                subject = decode_subject(msg['subject'])
                sender = decode_header(msg['from'])[0][0]
                date = msg['date']
                
                # Print email details
                print(f"Subject: {subject}")
                print(f"From: {sender}")
                print(f"Date: {date}")
                print()

    # Logout from the server
    mail.logout()

mail_fetch("exciting")