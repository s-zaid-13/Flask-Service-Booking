from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from dotenv import load_dotenv
import os



app = Flask(__name__)
load_dotenv()
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
SQLALCHEMY_TRACK_MODIFICATIONS = False

#Mail Configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME']=os.getenv('EMAIL')
app.config['MAIL_PASSWORD']=os.getenv('PASSWORD')
app.config['MAIL_DEFAULT_SENDER']=os.getenv('EMAIL')


db=SQLAlchemy(app)
migrate=Migrate(app,db)
login_manager = LoginManager(app)
login_manager.login_view='main.login_page'
login_manager.login_message_category='info'
bcrypt = Bcrypt(app)
from App.routes import main

# Register the blueprint
app.register_blueprint(main)
with app.app_context():
    from App import routes
    from App import models

