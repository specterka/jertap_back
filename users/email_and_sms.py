from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from jertap_backend.settings import SES_SENDER_EMAIL, SEND_EMAIL, SEND_SMS
from django.utils.safestring import mark_safe
import re

from users.smsc_api import SMSC


# For testing use this in shell
# from django.core.mail import send_mail
# from jertap_backend.settings import SES_SENDER_EMAIL
# send_mail('Test SES', 'This is test email', SES_SENDER_EMAIL, ['riddhish@logisticinfotech.co.in',])

def send_email(subject, message, recipient_list):
    if SEND_EMAIL:
        message = mark_safe(message)
        html_message = render_to_string('email.html', {'message': message}, )
        plain_message = strip_tags(html_message)
        try:
            send_mail(
                subject=subject,
                message=plain_message,
                from_email=SES_SENDER_EMAIL,
                recipient_list=recipient_list,
                html_message=html_message,
            )
        except Exception as e:
            print(e)


def is_valid_kazakhstan_mobile_number(number):
    # Define the regular expression for Kazakhstan mobile numbers
    # The format may vary, so adjust the regex as needed
    # In this example, it's assumed that Kazakhstan mobile numbers start with +7 followed by 9 digits.
    kazakhstan_mobile_regex = re.compile(r'^\+7\d+$')

    # Check if the number matches the regex
    return bool(kazakhstan_mobile_regex.match(number))


def send_message(phones, message):

    try:
        if is_valid_kazakhstan_mobile_number(phones):
            smsc = SMSC()
            smsc.send_sms(phones=phones, message=message, sender="sms")
        else:
            print("Not Kazakhstan number")

    except Exception as e:
        print(e)