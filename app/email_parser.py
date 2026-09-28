# email_parser.py
"""email_parser.py
Utility to connect to an IMAP mailbox, fetch emails with subject
"CONTADORES Enterprise", parse printer counter data and store it in the SQLite DB.
"""

import imaplib
import email
import re
from datetime import datetime
from .db import insert_counter

# Configuration – adjust as needed
IMAP_HOST = "imap.example.com"
IMAP_USER = "your_email@example.com"
IMAP_PASS = "your_password"
MAILBOX = "INBOX"
SUBJECT_FILTER = "CONTADORES Enterprise"

# Regex patterns to extract data from email body (example format)
# Expected lines like: "ID: PRINTER123", "Data: 2025-08-15", "TotalPages: 12345"
ID_PATTERN = re.compile(r"ID[:\s]+([A-Za-z0-9_-]+)", re.IGNORECASE)
DATE_PATTERN = re.compile(r"Data[:\s]+([0-9]{4}-[0-9]{2}-[0-9]{2})", re.IGNORECASE)
PAGES_PATTERN = re.compile(r"TotalPages[:\s]+(\d+)", re.IGNORECASE)


def _extract_field(pattern: re.Pattern, text: str):
    match = pattern.search(text)
    return match.group(1).strip() if match else None


def _parse_email_body(body: str):
    """Extract printer_id, date and total_pages from the email body.
    Returns a tuple (printer_id, date_str, total_pages) or None if parsing fails.
    """
    printer_id = _extract_field(ID_PATTERN, body)
    date_str = _extract_field(DATE_PATTERN, body)
    pages_str = _extract_field(PAGES_PATTERN, body)
    if printer_id and date_str and pages_str:
        return printer_id, date_str, int(pages_str)
    return None


def process_emails(mark_as_seen: bool = False):
    """Connect to IMAP, fetch unread emails with the target subject,
    parse them and store the counters in the database.
    Args:
        mark_as_seen: If True, mark processed emails as \"SEEN\".
    """
    try:
        mail = imaplib.IMAP4_SSL(IMAP_HOST)
        mail.login(IMAP_USER, IMAP_PASS)
        mail.select(MAILBOX)
        # Search for UNSEEN emails with the subject
        status, data = mail.search(None, '(UNSEEN SUBJECT "%s")' % SUBJECT_FILTER)
        if status != "OK":
            print("[WARN] IMAP search failed")
            return
        email_ids = data[0].split()
        for eid in email_ids:
            status, msg_data = mail.fetch(eid, '(RFC822)')
            if status != "OK":
                continue
            raw_email = msg_data[0][1]
            msg = email.message_from_bytes(raw_email)
            # Get email body (prefer plain text)
            body = ""
            if msg.is_multipart():
                for part in msg.walk():
                    content_type = part.get_content_type()
                    if content_type == "text/plain" and not part.get('Content-Disposition'):
                        charset = part.get_content_charset() or "utf-8"
                        body = part.get_payload(decode=True).decode(charset, errors="ignore")
                        break
            else:
                charset = msg.get_content_charset() or "utf-8"
                body = msg.get_payload(decode=True).decode(charset, errors="ignore")
            parsed = _parse_email_body(body)
            if parsed:
                printer_id, date_str, total_pages = parsed
                # Convert date string to datetime object (assume UTC)
                ts = datetime.strptime(date_str, "%Y-%m-%d")
                insert_counter(printer_id, model="", total_pages=total_pages, ts=ts)
                print(f"[INFO] Stored counter for {printer_id} on {date_str}: {total_pages} pages")
                if mark_as_seen:
                    mail.store(eid, '+FLAGS', '\\Seen')
            else:
                print(f"[WARN] Could not parse email ID {eid.decode()}")
        mail.logout()
    except Exception as e:
        print(f"[ERROR] Email processing failed: {e}")

if __name__ == "__main__":
    # Simple CLI for manual execution
    process_emails(mark_as_seen=True)
