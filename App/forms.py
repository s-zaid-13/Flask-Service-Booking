from flask_wtf import FlaskForm
from wtforms.validators import DataRequired, Length, Email, EqualTo,NumberRange
from wtforms import ValidationError,StringField,SubmitField,PasswordField,SelectField,IntegerField,SelectMultipleField,TextAreaField,FloatField
from App.models import User,Service
from wtforms.widgets import ListWidget, CheckboxInput


class RegistrationForm(FlaskForm):
    username=StringField('Username:',validators=[Length(min=2,max=30),DataRequired()])
    email_address=StringField('Email Address:',validators=[DataRequired(),Email()])
    role = SelectField('Sign up as:', choices=[('Customer', 'Customer'),('Service Provider', 'Service Provider')], validators=[DataRequired()])
    provided_services = SelectMultipleField(
        'Services You Provide',
        choices=[],
        coerce=str,
        option_widget=CheckboxInput(),
        widget=ListWidget(prefix_label=False)
    )

    password=PasswordField('Password:',validators=[DataRequired(),Length(min=6)])
    password2=PasswordField('Confirm Password:',validators=[DataRequired(),EqualTo('password')])
    submit=SubmitField('Sign Up')
    def validate_username(self,username):
        user=User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is taken. Please choose a different one.')
    def validate_email_address(self,email_address):
        user=User.query.filter_by(email_address=email_address.data).first()
        if user:
            raise ValidationError('That email address is taken. Please choose a different one.')

class LoginForm(FlaskForm):
    email_address=StringField('Email Address:',validators=[DataRequired(),Email()])
    password = PasswordField('Password:',validators=[DataRequired()])
    submit=SubmitField('Login')

class ResetRequestForm(FlaskForm):
    email_address=StringField('Email Address:',validators=[DataRequired(),Email()])
    submit=SubmitField('Send Password Reset Request')

class ResetPasswordForm(FlaskForm):
    password=PasswordField('New Password:',validators=[DataRequired(),Length(min=6)])
    password2=PasswordField('Confirm Password:',validators=[DataRequired(),EqualTo('password')])
    submit=SubmitField('Reset Password')

class BookingForm(FlaskForm):
    address=StringField('Enter your address where to provide service:',validators=[DataRequired()])
    submit=SubmitField('Book Service')

class CancelBookingForm(FlaskForm):
    submit=SubmitField('Cancel Booking')

class AcceptOrderForm(FlaskForm):
    submit=SubmitField('Accept Order')

class SentOrderForm(FlaskForm):
    submit=SubmitField('Send Order')

class CompleteOrderForm(FlaskForm):
    submit=SubmitField('Yes')

class AddServiceForm(FlaskForm):
    service_name=StringField('Service Name:',validators=[Length(max=30), DataRequired()])
    description=StringField('Service Description:',validators=[DataRequired()])
    category=StringField('Service Category:',validators=[Length(max=30)])
    price=IntegerField('Service Price:',validators=[DataRequired()])
    submit=SubmitField('Add Service')
    def validate_service_name(self,service_name):
        service=Service.query.filter_by(service_name=service_name.data).first()
        if  service:
            raise ValidationError('That service name is taken. Please choose a different one.')


class ReviewForm(FlaskForm):
    rating = FloatField('Rating', validators=[DataRequired(), NumberRange(min=1.0, max=5.0)], render_kw={'placeholder': '1 to 5'})
    review_text = TextAreaField('Review Text', validators=[DataRequired()], render_kw={'placeholder': 'Write your review here...'})
    submit = SubmitField('Submit Review')