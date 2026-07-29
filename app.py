from extensions import db, login_manager
import auth
from routes import configure_routes
from helpers import datetimeformat
from flask import Flask
from flask_bootstrap import Bootstrap5
from flask_ckeditor import CKEditor
from flask_migrate import Migrate
import os




# TODO user activation
# TODO forgotten password
# TODO password obfuscation on create and update

# secret key for create form
SECRET_KEY = os.environ.get('SECRET_KEY')


#TODO
'''def create_app():
    app = Flask(__name__)

    db.init_app(app)
    login_manager.init_app(app)
    ckeditor.init_app(app)

    return app'''




app = Flask(__name__)


app.config['SECRET_KEY'] = SECRET_KEY
app.config['SQLALCHEMY_DATABASE_URI'] = ('postgresql://postgres:Jester10qrz@localhost:5432/posts_db')
app.config['UPLOAD_FOLDER'] = 'static/uploads'


db.init_app(app)
login_manager.init_app(app)


app.add_template_filter(
    datetimeformat,
    'datetimeformat'
)

configure_routes(app)


migrate = Migrate(app, db)




ckeditor = CKEditor(app)
bootstrap = Bootstrap5(app)











if __name__ == '__main__':
    app.run(debug=True)




