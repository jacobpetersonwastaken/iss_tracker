import os
from dotenv import load_dotenv
import smtplib
import pandas as pd

load_dotenv('.env')
email_df = pd.read_json('emails.json', typ='series')
email_list = email_df.tolist()
MY_EMAIL = os.getenv('MY_EMAIL')


def send_email(sending_from, to, msg, sub):
    PASSWORD = os.getenv('PASSWORD')
    with smtplib.SMTP('smtp.gmail.com', 587, timeout=120) as connection:
        """Sends email without attachment."""
        connection.starttls()
        connection.login(user=MY_EMAIL, password=PASSWORD)
        connection.sendmail(from_addr=sending_from, to_addrs=to, msg=f'Subject:{sub}\n\n{msg}')


def send_iss_notification(iss_lat, iss_long):
    message = f'The International space station is currently above your head at Latitude:{iss_lat} and ' \
              f'Longitude{iss_long}.'
    subject = 'ISS above your head!'
    send_email(sending_from=MY_EMAIL, to=email_list, msg=message, sub=subject)
