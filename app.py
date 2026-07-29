from flask import Flask

from extensions import db, login_manager, migrate, ckeditor, bootstrap
from config import Config
from template_filters import datetimeformat
from routes import configure_routes

# Registers Flask-Login user loader
import auth


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'login'
    
    migrate.init_app(app, db)
    ckeditor.init_app(app)
    bootstrap.init_app(app)

    app.add_template_filter(datetimeformat, 'datetimeformat')

    configure_routes(app)

    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)




