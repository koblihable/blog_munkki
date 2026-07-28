from forms import *
from models import *


import smtplib
from flask import Flask, render_template, redirect, url_for, flash, abort
from functools import wraps
from flask_bootstrap import Bootstrap5


from flask_ckeditor import CKEditor
from flask_login import LoginManager, login_user, current_user, logout_user, login_required
from flask_migrate import Migrate



from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
import datetime as dt
import uuid as uuid

# TODO user activation
# TODO forgotten password
# TODO password obfuscation on create and update

# info for the contact form
APP_EMAIL=os.environ.get('EMAIL')
APP_PASSWORD=os.environ.get('PASSWORD')

# secret key for create form
SECRET_KEY = os.environ.get('SECRET_KEY')



# update config
app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY
app.config['SQLALCHEMY_DATABASE_URI'] = ('postgresql://postgres:Jester10qrz@localhost:5432/posts_db')
app.config['UPLOAD_FOLDER'] = 'static/uploads'
db.init_app(app)

with app.app_context():
    db.create_all()

migrate = Migrate(app, db)

login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

ckeditor = CKEditor(app)
bootstrap = Bootstrap5(app)








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
            title=create_form.title.data,
            subtitle=create_form.subtitle.data,
            body=create_form.body.data,
            img_url=create_form.img_url.data,
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
    edit_form = BlogForm(obj=post)

    if edit_form.validate_on_submit():
        blog_to_update = db.get_or_404(BlogPost, post_id)
        blog_to_update.title = edit_form.title.data
        blog_to_update.subtitle = edit_form.subtitle.data
        blog_to_update.body = edit_form.body.data
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
        name = contact_form.name.data
        user_email = contact_form.email.data
        phone = contact_form.phone.data
        message = contact_form.message.data
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
            text = comment_form.comment.data,
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
        email = register_form.email.data.lower()
        # check if user already exists
        user = db.session.execute(db.select(User).where(User.email==email)).scalar()
        if user:
            flash('User with this email address already exists. Please log in instead.', 'danger')
            return redirect(url_for('login'))
        password = generate_password_hash(
            register_form.password.data,
            method='pbkdf2:sha256',
            salt_length=8
        )
        profile_pic_file = register_form.profile_pic.data
        if profile_pic_file:
            profile_pic_name = f"{uuid.uuid4()}_{secure_filename(profile_pic_file.filename)}"
            profile_pic_file.save(os.path.join(app.config['UPLOAD_FOLDER'], profile_pic_name))

        new_user = User(
            first_name=register_form.first_name.data,
            last_name=register_form.last_name.data,
            email=email,
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
        email = login_form.email.data
        password = login_form.password.data
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
    picture_form = PictureForm()

    user_form = UpdateUserForm(obj=user)
    password_form = ChangePasswordForm()

    #TODO move into separate functions
    if user_form.submit.data and user_form.validate():
        user.first_name=user_form.first_name.data
        user.last_name=user_form.last_name.data
        user.email=user_form.email.data.lower()
        user.date_updated = dt.datetime.now()
        db.session.commit()
        return redirect(url_for('user_settings', user_id=user.id))

    elif picture_form.update.data and picture_form.validate():

        profile_pic_file = picture_form.image.data
        if profile_pic_file:
            profile_pic_name = f"{uuid.uuid4()}_{secure_filename(profile_pic_file.filename)}"
            profile_pic_file.save(os.path.join(app.config['UPLOAD_FOLDER'], profile_pic_name))
            user.profile_pic = profile_pic_name
            db.session.commit()
            return redirect(url_for('user_settings', user_id=user.id))

    elif password_form.update.data and password_form.validate():
        old_password = password_form.old_password.data
        current_password = user.password
        if not check_password_hash(current_password, old_password):
            flash('Password is incorrect. Try again.', 'danger')
            return redirect(url_for('user_settings', user_id=user.id))
        else:
            password = generate_password_hash(
                password_form.new_password.data,
                method='pbkdf2:sha256',
                salt_length=8
            )
            user.password = password
            db.session.commit()
            return redirect(url_for('user_settings', user_id=user.id))

    return render_template(
        'user_detail_settings.html',
        user=user,
        user_form=user_form,
        picture_form=picture_form,
        password_form=password_form
    )

@app.route('/usr_comments/<int:user_id>')
def user_comments(user_id):
    user = db.get_or_404(User, user_id)
    return render_template('user_detail_comments.html', user=user)

@app.route('/usr_posts/<int:user_id>')
def user_posts(user_id):
    user = db.get_or_404(User, user_id)
    return render_template('user_detail_posts.html', user=user)


if __name__ == '__main__':
    app.run(debug=True)

