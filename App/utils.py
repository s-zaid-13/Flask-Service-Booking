from flask_mail import Mail, Message
from flask import url_for
from App import app


mail = Mail(app)
#send Mail
def send_email(user):
    token=user.get_reset_token()
    msg=Message('Password Reset Request',recipients=[user.email_address])
    msg.body=f'''To reset your password, visit the following link:
    {url_for('main.reset_password', token=token, _external=True)}
    if you did not request this, simply ignore this email. 
'''
    mail.send(msg)






