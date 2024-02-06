# importing libraries
import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formataddr

employee_email_IDs = {                              # Add email ID's of employees in
    "app1357":"aparajeeth02@gmail.com",             # your organization here
    "Shrish236":"shrishrajamohan@gmail.com"
}

def callemail(name, message_text, message_html, subject):
    port = 465                                      # For SSL
    smtp_server = "smtp.gmail.com"                  # SMTP server to send email
    sender_email = "YOUR_ORG_EMAIL"                 # Sender email address
    receiver_email = employee_email_IDs.get(name)   # Receiver email address
    password = "YOUR_GOOGLE_APP_PASSWORD"           # App password created through google account

    # Add details of the email here
    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = formataddr(('Mindgrove Technologies', sender_email))
    message["To"] = receiver_email

    # Turn these into plain/html MIMEText objects
    part1 = MIMEText(message_text, "plain")
    part2 = MIMEText(message_html, "html")

    # Add HTML/plain-text parts to MIMEMultipart message
    # The email client will try to render the last part first
    message.attach(part1)
    message.attach(part2)

    # Sending email
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message.as_string())
        print("Email sent! to " + name)

