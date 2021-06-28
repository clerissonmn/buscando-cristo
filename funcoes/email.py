import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

def envia_email(destinatario=None, mensagem=None, remetente=None, senha=None, assunto=None):
    # https://realpython.com/python-send-email/
    
    message = MIMEMultipart("alternative")
    message["Subject"] = f"[buscandocristo]: {assunto}"
    message["From"] = remetente
    message["To"] = destinatario

    # Create the plain-text and HTML version of your message
    text = mensagem
    html = f"""
    <html>
    <body>
        <p>{mensagem}</p>
    </body>
    </html>
    """

    # Turn these into plain/html MIMEText objects
    part1 = MIMEText(text, "plain")
    part2 = MIMEText(html, "html")

    # Add HTML/plain-text parts to MIMEMultipart message
    # The email client will try to render the last part first
    message.attach(part1)
    message.attach(part2)

    # Create secure connection with server and send email
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(remetente, senha)
        server.sendmail(
            remetente, destinatario, message.as_string()
        )