from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from flask_login import LoginManager


# database
class Base(DeclarativeBase):
    pass
db = SQLAlchemy(model_class=Base)


#login manager
login_manager = LoginManager()