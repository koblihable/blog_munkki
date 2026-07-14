import smtplib
from flask import Flask, render_template, request, redirect, url_for, flash, abort
from functools import wraps
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm, csrf
from flask_ckeditor import CKEditor, CKEditorField
from flask_login import UserMixin, LoginManager, login_user, current_user, logout_user, login_required
from flask_migrate import Migrate
from wtforms import StringField, FormField
from wtforms.fields.simple import SubmitField, TextAreaField, FileField
from wtforms.validators import DataRequired, Regexp, Length
from sqlalchemy import Integer, String, Text, ForeignKey, Boolean, DateTime
from typing import List
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
import datetime as dt
import uuid as uuid

# TODO user profile section
# TODO user activation
# TODO forgotten password
# TODO password obfuscation on create and update

# info for the contact form
APP_EMAIL=os.environ.get('EMAIL')
APP_PASSWORD=os.environ.get('PASSWORD')

# secret key for create form
SECRET_KEY = os.environ.get('SECRET_KEY')

# database initialization
class Base(DeclarativeBase):
    pass
db = SQLAlchemy(model_class=Base)

# update config
app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY
app.config['SQLALCHEMY_DATABASE_URI'] = ('postgresql://postgres:Jester10qrz@localhost:5432/posts_db')
app.config['UPLOAD_FOLDER'] = 'static/usr_images'
db.init_app(app)
migrate = Migrate(app, db)

login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

ckeditor = CKEditor(app)
bootstrap = Bootstrap5(app)


### models ###

class User(UserMixin, db.Model):
    id:Mapped[int] = mapped_column(Integer, primary_key=True)
    first_name:Mapped[str] = mapped_column(String(255), nullable=False, default='none')
    last_name:Mapped[str] = mapped_column(String(255), nullable=False, default='none')
    email:Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    password:Mapped[str] = mapped_column(String(100), nullable=False)
    is_admin:Mapped[bool] = mapped_column(Boolean(), nullable=False, default=False)
    profile_pic:Mapped[str] = mapped_column(String(), nullable=True, default=None)
    date_created:Mapped[dt.datetime] = mapped_column(DateTime(), nullable=False, default=dt.datetime.now())
    date_updated: Mapped[dt.datetime] = mapped_column(DateTime(), nullable=False, default=dt.datetime.now())
    last_logged_in:Mapped[dt.datetime] = mapped_column(DateTime(), nullable=True, default=None)

    # parent relationships
    posts: Mapped[List['BlogPost']] = relationship('BlogPost', back_populates='author')
    comments:Mapped[List['Comment']] = relationship('Comment', back_populates='comment_author')

    @property
    def has_posts(self):
        return len(self.posts) > 0


class BlogPost(db.Model):
    id:Mapped[int] = mapped_column(Integer, primary_key=True)
    title:Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    subtitle:Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    body:Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    date_created:Mapped[dt.datetime] = mapped_column(DateTime(), nullable=False, default=dt.datetime.now())
    date_updated: Mapped[dt.datetime] = mapped_column(DateTime(), nullable=False, default=dt.datetime.now())
    img_url:Mapped[str] = mapped_column(String(255))

    # child relationship
    author_id:Mapped[int] = mapped_column(Integer, ForeignKey(User.id), nullable=False)
    author:Mapped[str] = relationship('User', back_populates='posts')

    # parent relationship
    post_comments:Mapped[List['Comment']] = relationship('Comment', back_populates='parent_post')


class Comment(db.Model):
    id:Mapped[int] = mapped_column(Integer, primary_key=True)
    date_created:Mapped[dt.datetime] = mapped_column(DateTime(), nullable=False, default=dt.datetime.now())
    date_updated: Mapped[dt.datetime] = mapped_column(DateTime(), nullable=False, default=dt.datetime.now())
    text: Mapped[str] = mapped_column(String(255), nullable=False)

    # child relationships
    author_id:Mapped[int] = mapped_column(Integer, ForeignKey(User.id), nullable=False)
    comment_author:Mapped[str] = relationship('User', back_populates='comments')
    post_id:Mapped[int] = mapped_column(Integer, ForeignKey(BlogPost.id), nullable=False)
    parent_post = relationship('BlogPost', back_populates='post_comments')

with app.app_context():
    db.create_all()


### forms ###
# create blog post
class BlogForm(FlaskForm):
    title = StringField(label='Title*', validators=[DataRequired()])
    subtitle = StringField(label='Subtitle*', validators=[DataRequired()])
    body = CKEditorField(label='Text*', validators=[DataRequired()])
    img_url = StringField(label='Image', default='./static/assets/img/rafa.jpg')
    submit = SubmitField(label='Post')

# create/ update a user
class UserForm(FlaskForm):
    email_error = 'Please enter a valid email address'
    password_error = 'Password must be at least 8 characters long'
    first_name = StringField(label='First Name*', validators=[DataRequired()])
    last_name = StringField(label='Last Name*', validators=[DataRequired()])
    profile_pic = FileField(label='Profile Picture')
    email = StringField(
        label='Email*',
        validators=[DataRequired(), Regexp(regex=r".+@.+\..+", message=email_error)]
    )
    password = StringField(
        label='Password*',
        validators=[DataRequired(), Length(min=8, message=password_error)],
    )
    submit = SubmitField(label='Submit')

class UpdateUserForm(FlaskForm):
    email_error = 'Please enter a valid email address'
    first_name = StringField(label='First Name', validators=[DataRequired()])
    last_name = StringField(label='Last Name', validators=[DataRequired()])
    email = StringField(
        label='Email',
        validators=[DataRequired(), Regexp(regex=r".+@.+\..+", message=email_error)]
    )
    submit = SubmitField(label='Update')

# user login
class LoginForm(FlaskForm):
    email = StringField(label='Email*', validators=[DataRequired()])
    password = StringField(label='Password*', validators=[DataRequired()])
    submit = SubmitField(label='Submit')

# message form
class ContactForm(FlaskForm):
    name = StringField(label='Name*', validators=[DataRequired()])
    email = StringField(label='Email*', validators=[DataRequired()])
    phone = StringField(label='Phone')
    message = TextAreaField(label='Message*', validators=[DataRequired()])
    submit = SubmitField(label='Submit')

# comment form
class CommentForm(FlaskForm):
    comment = TextAreaField(label='Comment', validators=[DataRequired()])
    submit = SubmitField(label='Submit')

# picture form
class PictureForm(FlaskForm):
    image = FileField(label='')
    update = SubmitField(label='submit')

class PasswordForm(FlaskForm):
    old_password = StringField(label='Old Password*', validators=[DataRequired()])
    new_password = StringField(label='New Password*', validators=[DataRequired()])
    check_password = StringField(label='Password Check*', validators=[DataRequired()])
    update = SubmitField(label='submit')




#admin user decorator
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin:
            return abort(403)
        return f(*args, **kwargs)
    return decorated_function


# date filter
@app.template_filter('datetimeformat')
def datetimeformat(value, string_format='%B %d, %Y'):
    return value.strftime(string_format)


# routes
@app.route('/')
def home():
    result = db.session.execute(db.select(BlogPost)).scalars().all()
    recent_blog_posts = result[-3:]
    return render_template('index.html', posts=recent_blog_posts[::-1])


@app.route('/old_posts')
def old_posts():
    result = db.session.execute(db.select(BlogPost)).scalars().all()
    old_blog_posts = result[:-3]
    return render_template('older_posts.html', posts=old_blog_posts[::-1])


@app.route('/my_posts')
def my_posts():
    my_posts = db.session.execute(db.select(BlogPost).where(BlogPost.author_id == current_user.id)).scalars().all()
    return render_template('my_index.html', posts=my_posts)


@app.route('/create', methods=['GET', 'POST'])
@admin_required
def create_blog():
    create_form = BlogForm()
    if create_form.validate_on_submit():
        blog_post = BlogPost(
            title=request.form.get('title'),
            subtitle=request.form.get('subtitle'),
            body=request.form.get('body'),
            img_url=request.form.get('img_url'),
            date_created = dt.datetime.now(),
            date_updated=dt.datetime.now(),
            author_id = current_user.id
        )
        db.session.add(blog_post)
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('create_blog_post.html', form=create_form)


@app.route('/edit/<int:post_id>', methods=['GET', 'POST'])
@admin_required
def edit_post(post_id):
    post = db.get_or_404(BlogPost, post_id)
    edit_form = BlogForm(
        title = post.title,
        subtitle = post.subtitle,
        body = post.body
    )
    if edit_form.validate_on_submit():
        blog_to_update = db.get_or_404(BlogPost, post_id)
        blog_to_update.title = request.form.get('title')
        blog_to_update.subtitle = request.form.get('subtitle')
        blog_to_update.body = request.form.get('body')
        blog_to_update.date_updated = dt.date.today()
        db.session.commit()
        return redirect(url_for('blog_post_detail', post_id=post_id))
    return render_template('edit_blog_post.html', post=post, edit_form=edit_form)


@app.route('/delete/<int:post_id>')
@admin_required
def delete_post(post_id):
    blog_post = db.get_or_404(BlogPost, post_id)
    db.session.delete(blog_post)
    db.session.commit()
    return redirect(url_for('home'))


@app.route('/about')
def about_author():
    return render_template('about.html')


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    contact_form = ContactForm()
    if contact_form.validate_on_submit():
        name = request.form.get('name')
        user_email = request.form.get('email')
        phone = request.form.get('phone')
        message = request.form.get('message')
        email_message = f"Subject:New Message\n\nName: {name}\nEmail: {user_email}\nPhone: {phone}\nMessage:{message}"
        with smtplib.SMTP("smtp.gmail.com") as connection:
            connection.starttls()
            connection.login(APP_EMAIL, APP_PASSWORD)
            connection.sendmail(APP_EMAIL, APP_EMAIL, email_message)
        return render_template("contact.html", msg_sent=True, form=contact_form)
    return render_template("contact.html", msg_sent=False, form=contact_form)


@app.route('/post/<int:post_id>', methods=['GET', 'POST'])
def blog_post_detail(post_id):
    blog_post = db.get_or_404(BlogPost, post_id)
    #comments = db.session.execute(db.select(Comment).where(Comment.post_id == post_id)).scalars().all()
    comment_form = CommentForm()
    if comment_form.validate_on_submit():
        comment = Comment(
            text = request.form.get('comment'),
            author_id = current_user.id,
            comment_author = current_user,
            post_id = post_id,
            parent_post = blog_post,
            date_created=dt.datetime.now(),
            date_updated=dt.datetime.now()
        )
        db.session.add(comment)
        db.session.commit()
        return redirect(url_for('blog_post_detail', post_id=blog_post.id,  post=blog_post, form=comment_form))

    return render_template('post_detail.html', post=blog_post, form=comment_form)


@app.route('/register', methods=['GET', 'POST'])
def register_user():
    register_form = UserForm()
    if register_form.validate_on_submit():
        email = request.form.get('email').lower()
        # check if user already exists
        user = db.session.execute(db.select(User).where(User.email==email)).scalar()
        if user:
            flash('User with this email address already exists. Please log in instead.', 'danger')
            return redirect(url_for('login'))
        password = generate_password_hash(
            request.form.get('password'),
            method='pbkdf2:sha256',
            salt_length=8
        )
        profile_pic_file = request.files.get('profile_pic')
        if profile_pic_file:
            profile_pic = secure_filename(profile_pic_file.filename)
            profile_pic_name = f'{uuid.uuid1()}_{profile_pic}'
            profile_pic_file.save(os.path.join(app.config['UPLOAD_FOLDER'], profile_pic_name))

        new_user = User(
            first_name=request.form.get('first_name'),
            last_name=request.form.get('last_name'),
            email=request.form.get('email').lower(),
            password=password,
            profile_pic=profile_pic_name if profile_pic_file else None,
            date_created=dt.datetime.now(),
            date_updated=dt.datetime.now(),
            last_logged_in=dt.datetime.now()
        )
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return redirect(url_for('home'))
    return render_template('register.html', register_form=register_form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    login_form = LoginForm()
    if login_form.validate_on_submit():
        email = request.form.get('email')
        password = request.form.get('password')
        user = db.session.execute(db.select(User).where(User.email==email)).scalar()
        if not user:
            flash('A user with this email address does not exist. Please register instead.', 'danger')
            return redirect(url_for('register_user'))
        if not check_password_hash(user.password, password):
            flash('Password is incorrect. Try again.', 'danger')
            return redirect(url_for('login'))
        login_user(user)
        user.last_logged_in = dt.datetime.now()
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('login.html', login_form=login_form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/list_users')
@admin_required
def list_users():
    result = db.session.execute(db.select(User).order_by(User.id)).scalars().all()
    users = result[1:]
    return render_template('list_users.html', users=users)


@app.route('/switch/<int:user_id>')
@admin_required
def switch_admin(user_id):
    user = db.get_or_404(User, user_id)
    if user.is_admin:
        user.is_admin = False
    else:
        user.is_admin = True
    db.session.commit()
    return redirect(url_for('list_users'))


@app.route('/delete_user/<int:user_id>')
@admin_required
def delete_user(user_id):
    user = db.get_or_404(User, user_id)
    db.session.delete(user)
    db.session.commit()
    return redirect(url_for('list_users'))


@app.route('/usr_profile/<int:user_id>')
def user_profile(user_id):
    user = db.get_or_404(User, user_id)
    return render_template('user_detail_profile.html', user=user)


@app.route('/usr_settings/<int:user_id>', methods=['GET', 'POST'])
def user_settings(user_id):
    user = db.get_or_404(User, user_id)
    picture_form = PictureForm(
        image=user.profile_pic
    )
    user_form = UpdateUserForm(
        first_name=user.first_name,
        last_name=user.last_name,
        email=user.email,
    )
    if user_form.validate_on_submit():
        user.first_name=request.form.get('first_name')
        user.last_name=request.form.get('last_name'),
        user.email=request.form.get('email').lower(),
        user.date_updated = dt.datetime.now()
        db.session.commit()
        return redirect(
            url_for('user_settings', user=user, user_id=user.id, user_form=user_form, picture_form=picture_form)
        )

    if picture_form.update.data and picture_form.validate():
        print('true')
        profile_pic_file = request.files.get('profile_pic')
        print(profile_pic_file)
        if profile_pic_file:
            profile_pic = secure_filename(profile_pic_file.filename)
            profile_pic_name = f'{uuid.uuid1()}_{profile_pic}'
            profile_pic_file.save(os.path.join(app.config['UPLOAD_FOLDER'], profile_pic_name))
            user.profile_pic = profile_pic_name
            db.session.commit()
            return redirect(
                url_for('user_settings', user=user, user_id=user.id, user_form=user_form, picture_form=picture_form)
            )

    return render_template(
        'user_detail_settings.html', user=user, user_form=user_form, picture_form=picture_form
    )

@app.route('/usr_comments/<int:user_id>')
def user_comments(user_id):
    user = db.get_or_404(User, user_id)
    return render_template('user_detail_comments.html', user=user)

@app.route('/usr_posts/<int:user_id>')
def user_posts(user_id):
    user = db.get_or_404(User, user_id)
    return render_template('user_detail_posts.html', user=user)

# TODO reset password from page settings
# login required old password, new password


if __name__ == '__main__':
    app.run(debug=True)

