from datetime import datetime, UTC
from App import db,bcrypt,login_manager
from flask_login import UserMixin
from itsdangerous.url_safe import URLSafeTimedSerializer as Serializer
from flask import current_app
import json



@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
class User(db.Model,UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), unique=True, nullable=False)
    email_address = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(), nullable=False)
    role = db.Column(db.String(30), nullable=False)
    date_created = db.Column(db.DateTime(), default=lambda: datetime.now(UTC))
    last_login = db.Column(db.DateTime(), default=lambda: datetime.now(UTC))
    rating=db.Column(db.Float,default=5.0)
    provided_services = db.Column(db.Text, nullable=True)



    # Relationships
    bookings = db.relationship('Booking', foreign_keys='Booking.user_id', backref='user', lazy=True)
    provider_bookings = db.relationship('Booking', foreign_keys='Booking.provider_id', backref='provider', lazy=True)
    reviews = db.relationship('Review', backref='user', lazy=True)

    def set_provided_services(self, services):
        self.provided_services = json.dumps(services)

    def get_provided_services(self):
        return json.loads(self.provided_services) if self.provided_services else []


    @property
    def password(self):
        return self.password_hash

    @password.setter
    def password(self, plain_text_password):
        self.password_hash=bcrypt.generate_password_hash(plain_text_password).decode('utf-8')

    def verify_password(self, plain_text_password):
        return bcrypt.check_password_hash(self.password_hash, plain_text_password)

    def __repr__(self):
        return self.username

    def get_reset_token(self):
        s = Serializer(current_app.config['SECRET_KEY'])
        return s.dumps({'user_id':self.id},salt='reset-password-salt')

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            user_data=s.loads(token,salt='reset-password-salt',max_age=120)
            user_id=user_data['user_id']
        except:
            return None
        return User.query.get(user_id)

class Service(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    service_name = db.Column(db.String(30), unique=True, nullable=False)
    description = db.Column(db.String(), nullable=False)
    category = db.Column(db.String(30), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    rating = db.Column(db.Float, default=5.0)

    # Relationships
    bookings = db.relationship('Booking', backref='service', lazy=True)
    reviews = db.relationship('Review', backref='service', lazy=True)

class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'), nullable=False)
    provider_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    status = db.Column(db.String(), nullable=False)
    booking_date = db.Column(db.DateTime(), default=lambda: datetime.now(UTC))
    order_completed_date = db.Column(db.DateTime())
    Booking_Accept_date = db.Column(db.DateTime())
    address = db.Column(db.String(), nullable=False)


class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    booking_id = db.Column(db.Integer, db.ForeignKey('booking.id'), nullable=False)
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'), nullable=False)
    rating = db.Column(db.Float, default=5.0)
    review_text = db.Column(db.String(), nullable=False)
    review_date = db.Column(db.DateTime(), default=lambda: datetime.now(UTC))

    __table_args__ = (db.UniqueConstraint('user_id', 'booking_id', name='_user_booking_uc'),)

