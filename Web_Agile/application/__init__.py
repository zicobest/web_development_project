from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# database URI
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///FinancialReportDB.db' 

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['SECRET_KEY'] = '123456789' 

db = SQLAlchemy(app)

from application import routes
