import smtplib
from email.message import EmailMessage

try:
    import keyring
except Exception:
    keyring = None


def _fetch_pass_from_keyring(user):
    if not keyring or not user:
        return None
    try:
        return keyring.get_password('contadores_smtp', user)
    except Exception:
        return None


def send_email(smtp_server, smtp_port, smtp_user, smtp_pass, to_addr, subject, body, use_ssl=True):
    # se senha não informada, tentar keyring
    if not smtp_pass:
        smtp_pass = _fetch_pass_from_keyring(smtp_user)

    if not smtp_pass:
        raise ValueError('SMTP password not provided and not found in keyring')

    msg = EmailMessage()
    msg['From'] = smtp_user
    msg['To'] = to_addr
    msg['Subject'] = subject
    msg.set_content(body)

    if use_ssl:
        with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
            server.login(smtp_user, smtp_pass)
            server.send_message(msg)
    else:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_pass)
            server.send_message(msg)
