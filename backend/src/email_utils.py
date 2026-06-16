import os
import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from dotenv import load_dotenv
from backend.src.logger import logger

# ---------------------------------------------------------------------------
# Load env — search in CWD first, then relative to this file (works both
# when running from project root and from inside the backend folder)
# ---------------------------------------------------------------------------
def _load_env():
    candidates = [
        os.path.join(os.getcwd(), 'sendgrid.env'),
        os.path.join(os.getcwd(), '.env'),
        os.path.join(os.path.dirname(__file__), '..', '..', 'sendgrid.env'),
        os.path.join(os.path.dirname(__file__), '..', '..', '.env'),
    ]
    for path in candidates:
        if os.path.exists(path):
            load_dotenv(path, override=False)
            return
    logger.warning("No sendgrid.env / .env found. Expecting env vars to be set externally.")

_load_env()

# ---------------------------------------------------------------------------
# SMTP fallback — uses Gmail by default (configurable via env vars)
# ---------------------------------------------------------------------------
def _send_smtp_email(to_email: str, subject: str, body: str, user_name: str = "Student") -> bool:
    """
    Fallback delivery via SMTP (Gmail by default).

    Required env vars:
        SMTP_USER     — Gmail address, e.g. iheakanwa.tiffany@gmail.com
        SMTP_PASSWORD — Gmail App Password (16-char, no spaces)
                        Generate at: https://myaccount.google.com/apppasswords

    Optional env vars (defaults work for Gmail):
        SMTP_HOST     — default: smtp.gmail.com
        SMTP_PORT     — default: 587
    """
    smtp_user     = os.environ.get('SMTP_USER') or os.environ.get('SENDER_EMAIL', '')
    smtp_password = os.environ.get('SMTP_PASSWORD', '').replace(' ', '')  # Gmail shows password with spaces; strip them
    smtp_host     = os.environ.get('SMTP_HOST', 'smtp.gmail.com')
    smtp_port     = int(os.environ.get('SMTP_PORT', '587'))

    if not smtp_password:
        logger.warning(
            "SMTP_PASSWORD not set — cannot use SMTP fallback. "
            "Add SMTP_PASSWORD=<Gmail App Password> to sendgrid.env. "
            "Generate one at https://myaccount.google.com/apppasswords"
        )
        return False

    if not smtp_user:
        logger.warning("SMTP_USER / SENDER_EMAIL not set — cannot use SMTP fallback.")
        return False

    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From']    = f"Stick2It <{smtp_user}>"
        msg['To']      = to_email

        # Plain-text part
        plain_body = f"Hi {user_name},\n\n{body}\n\n— The Stick2It Team"
        msg.attach(MIMEText(plain_body, 'plain'))

        # HTML part — simple branded wrapper
        html_body = f"""
        <html><body style="font-family:sans-serif;max-width:600px;margin:auto;padding:20px">
            <div style="background:#6C63FF;padding:16px 24px;border-radius:8px 8px 0 0">
                <h2 style="color:white;margin:0">📌 Stick2It</h2>
            </div>
            <div style="border:1px solid #e0e0e0;border-top:none;padding:24px;border-radius:0 0 8px 8px">
                <p>Hi <strong>{user_name}</strong>,</p>
                <p style="font-size:15px;line-height:1.6">{body}</p>
                <hr style="border:none;border-top:1px solid #eee;margin:24px 0">
                <p style="color:#888;font-size:12px">
                    You're receiving this because you have an active commitment on Stick2It.<br>
                    To turn off nudges, update your preferences in the app.
                </p>
            </div>
        </body></html>
        """
        msg.attach(MIMEText(html_body, 'html'))

        context = ssl.create_default_context()
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.ehlo()
            server.starttls(context=context)
            server.login(smtp_user, smtp_password)
            server.sendmail(smtp_user, to_email, msg.as_string())

        logger.info(f"SMTP fallback: email sent to {to_email}")
        return True

    except smtplib.SMTPAuthenticationError:
        logger.error(
            "SMTP authentication failed. Make sure SMTP_PASSWORD is a Gmail App Password "
            "(not your regular Gmail password). "
            "Generate one at https://myaccount.google.com/apppasswords"
        )
        return False
    except Exception as e:
        logger.error(f"SMTP fallback error: {e}")
        return False


# ---------------------------------------------------------------------------
# Primary entry point — SendGrid with automatic SMTP fallback
# ---------------------------------------------------------------------------
def send_sendgrid_email(to_email: str, subject: str, body: str, user_name: str = "Student") -> bool:
    """
    Send an email via SendGrid.
    If SendGrid fails for any reason (quota, auth, network), automatically
    falls back to SMTP (Gmail App Password).
    """
    api_key     = os.environ.get('SENDGRID_API_KEY', '')
    sender      = os.environ.get('SENDER_EMAIL', '')

    # --- Attempt SendGrid ---
    if api_key:
        try:
            from sendgrid import SendGridAPIClient
            from sendgrid.helpers.mail import Mail

            sg_mail = Mail(
                from_email=sender or 'noreply@stick2it.app',
                to_emails=to_email,
                subject=subject,
                plain_text_content=body
            )
            sg = SendGridAPIClient(api_key)
            response = sg.send(sg_mail)

            if response.status_code in [200, 201, 202]:
                logger.info(f"SendGrid: email sent to {to_email} (status {response.status_code})")
                return True
            else:
                logger.warning(
                    f"SendGrid unexpected status {response.status_code} — "
                    f"falling back to SMTP."
                )
        except Exception as e:
            err_body = getattr(e, 'body', b'')
            if isinstance(err_body, bytes):
                err_body = err_body.decode('utf-8', errors='replace')

            logger.warning(
                f"SendGrid failed ({e}). "
                f"Details: {err_body}. "
                f"Falling back to SMTP."
            )
    else:
        logger.warning("SENDGRID_API_KEY not set — skipping SendGrid, trying SMTP.")

    # --- SMTP fallback ---
    return _send_smtp_email(to_email, subject, body, user_name)
