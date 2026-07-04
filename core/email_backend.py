from django.core.mail.backends.base import BaseEmailBackend
from django.conf import settings
import urllib.request
import urllib.error
import json

class BrevoEmailBackend(BaseEmailBackend):
    def send_messages(self, email_messages):
        if not email_messages:
            return 0
            
        api_key = getattr(settings, 'BREVO_API_KEY', '')
        if not api_key:
            print("BREVO_API_KEY is not set. Cannot send emails.")
            return 0
            
        num_sent = 0
        url = "https://api.brevo.com/v3/smtp/email"
        headers = {
            "accept": "application/json",
            "api-key": api_key,
            "content-type": "application/json"
        }
        
        for message in email_messages:
            sender = message.from_email or getattr(settings, 'DEFAULT_FROM_EMAIL', 'bobby@bobbythecoder.in')
            # Extract name and email if formatted like "Name <email@domain.com>"
            if '<' in sender and '>' in sender:
                sender_name, sender_email = sender.split('<')
                sender_name = sender_name.strip()
                sender_email = sender_email.replace('>', '').strip()
            else:
                sender_name = "BobbyTheCoder"
                sender_email = sender
                
            # Build recipients list
            to_list = [{"email": recipient} for recipient in message.to]
            
            data = {
                "sender": {
                    "name": sender_name,
                    "email": sender_email
                },
                "to": to_list,
                "subject": message.subject,
            }
            
            # Text content
            if message.body:
                data["textContent"] = message.body
                
            # HTML content
            if hasattr(message, 'alternatives') and message.alternatives:
                for alt_content, alt_type in message.alternatives:
                    if alt_type == 'text/html':
                        data["htmlContent"] = alt_content
                        break
            
            if "htmlContent" not in data and message.body:
                data["htmlContent"] = f"<html><body><p>{message.body.replace(chr(10), '<br>')}</p></body></html>"
                
            req = urllib.request.Request(
                url,
                data=json.dumps(data).encode('utf-8'),
                headers=headers,
                method='POST'
            )
            try:
                with urllib.request.urlopen(req) as response:
                    response.read().decode('utf-8')
                    num_sent += 1
            except urllib.error.HTTPError as e:
                error_body = e.read().decode('utf-8')
                print(f"Failed to send email via Brevo API (HTTPError {e.code}): {error_body}")
            except Exception as e:
                print(f"Failed to send email via Brevo API: {e}")
                
        return num_sent
