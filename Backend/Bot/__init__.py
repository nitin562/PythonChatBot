from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
  pass

db = SQLAlchemy(model_class=Base)
app=Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///bot.db"
db.init_app(app)
# Alwats init_app before models
import Bot.models

# Create tables inside an application context
with app.app_context():
    db.create_all()

from .routes import *