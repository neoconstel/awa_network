'''
At the moment, this script is configured to use a personal email and so has
few limitations:
    - you can't set a sender email. It uses the email of the API key owner
    - you can only send to a single recipient at once, not multiple recipients
'''
import requests
import os
from dotenv import load_dotenv
load_dotenv()

def send_email(subject, message, recipient):

    EMAILJS_PUBLIC_KEY = os.environ.get('EMAILJS_PUBLIC_KEY')

    url = "https://api.emailjs.com/api/v1.0/email/send"

    data = {
        'service_id': 'gmail_service',
        'template_id': 'gmail_sender',
        'user_id': EMAILJS_PUBLIC_KEY,
        'template_params': {
            'subject': subject,
            'message': message,
            'recipient': recipient
        }
    }
    
    try:
        response = requests.post(url, 
            json=data,
            headers={"Content-Type": "application/json"},
        )
    except:
        print("Failed to send email, due to connection error or API denial.")
    else:
        print(response.text)
        print(f"SENT EMAIL to {recipient}")


if __name__ == '__main__':
    send_email('Subject', 'Body of email', 'recipient@gmail.com')
