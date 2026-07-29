from forms import (BlogForm, UserForm, UpdateUserForm, LoginForm, ContactForm, CommentForm, ChangePasswordForm,
                   PictureForm)
from extensions import db
from models import User, BlogPost, Comment
from helpers import admin_required
import smtplib
from flask import render_template, redirect, url_for, flash, abort
from flask_login import login_user, current_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
import datetime as dt
import uuid as uuid


# info for the contact form
APP_EMAIL=os.environ.get('EMAIL')
APP_PASSWORD=os.environ.get('PASSWORD')




def configure_routes(app):
    # routes
    @app.route('/')
    def home():
        recent_blog_posts = db.session.execute(
            db.select(BlogPost).order_by(BlogPost.date_created.desc().limit(3)).scalars().all()
        )

        return render_template('index.html', posts=recent_blog_posts)

    #TODO pagination
    @app.route('/old_posts')
    def old_posts():
        old_blog_posts = db.session.execute(
            db.select(BlogPost).order_by(BlogPost.date_created.desc()).scalars().all()
        )

        return render_template('older_posts.html', posts=old_blog_posts[3:])


    #TODO pagination
    @app.route('/my_posts')
    @login_required
    def my_posts():
        my_blog_posts = (
            db.session.execute(
                db.select(BlogPost)
                .where(BlogPost.author_id == current_user.id)
                .order_by(BlogPost.date_created.desc())
            ).scalars().all()
        )

        return render_template('my_index.html', posts=my_blog_posts)


    @app.route('/create', methods=['GET', 'POST'])
    @login_required
    @admin_required
    def create_blog():
        form = BlogForm()

        if form.validate_on_submit():
            blog_post = BlogPost(
                title=form.title.data,
                subtitle=form.subtitle.data,
                body=form.body.data,
                img_url=form.img_url.data,
                author = current_user
            )

            db.session.add(blog_post)
            db.session.commit()

            flash("Blog post created successfully.", "success")
            return redirect(url_for('home'))

        return render_template('create_blog_post.html', form=form)


    @app.route('/edit/<int:post_id>', methods=['GET', 'POST'])
    @login_required
    @admin_required
    def edit_post(post_id):
        post = db.get_or_404(BlogPost, post_id)
        edit_form = BlogForm(obj=post)

        if edit_form.validate_on_submit():
            #TODO use edit_form.populate_obj(post)
            post.title = edit_form.title.data
            post.subtitle = edit_form.subtitle.data
            post.body = edit_form.body.data

            db.session.commit()

            flash("Blog post updated.", "success")
            return redirect(url_for('blog_post_detail', post_id=post.id))
        return render_template('edit_blog_post.html', post=post, edit_form=edit_form)


    #TODO restyle the delete button
    @app.route('/delete/<int:post_id>', methods=['POST'])
    @login_required
    @admin_required
    def delete_post(post_id):
        post = db.get_or_404(BlogPost, post_id)
        db.session.delete(post)
        db.session.commit()

        flash("Blog post deleted.", "success")
        return redirect(url_for('home'))


    @app.route('/about')
    def about_author():
        return render_template('about.html')


    @app.route('/contact', methods=['GET', 'POST'])
    def contact():
        form = ContactForm()

        if form.validate_on_submit():
            name = form.name.data
            user_email = form.email.data
            phone = form.phone.data
            message = form.message.data
            email_message = (
                f"Subject: New Message\n\n"
                f"Name: {name}\n"
                f"Email: {user_email}\n"
                f"Phone: {phone}\n"
                f"Message: {message}"
            )
            # TODO: Move email sending into email_service.py
            # TODO: Read SMTP server and port from config.py
            # TODO: Add logging when email sending fails
            try:
                with smtplib.SMTP("smtp.gmail.com") as connection:
                    connection.starttls()
                    connection.login(APP_EMAIL, APP_PASSWORD)
                    connection.sendmail(APP_EMAIL, APP_EMAIL, email_message)
            except Exception:
                flash(
                    "Sorry, your message could not be sent. Please try again later.",
                    "danger",
                )
                return redirect(url_for("contact"))
            flash("Message sent.", "success")
            return redirect(url_for("contact"))
        return render_template("contact.html", form=form)


    @app.route('/post/<int:post_id>', methods=['GET', 'POST'])
    def blog_post_detail(post_id):
        post = db.get_or_404(BlogPost, post_id)
        comment_form = CommentForm()

        if comment_form.validate_on_submit():

            if not current_user.is_authenticated:
                flash("Please log in to comment.", "warning")
                return redirect(url_for('login'))

            comment = Comment(
                text = comment_form.comment.data,
                comment_author = current_user,
                parent_post = post,
            )

            db.session.add(comment)
            db.session.commit()

            return redirect(url_for('blog_post_detail', post_id=post.id))

        return render_template('post_detail.html', post=post, form=comment_form)


    @app.route('/register', methods=['GET', 'POST'])
    def register_user():
        form = UserForm()

        if form.validate_on_submit():
            email = form.email.data.lower()
            # check if user already exists
            user = db.session.execute(db.select(User).where(User.email==email)).scalar_one_or_none()

            if user:
                flash('User with this email address already exists. Please log in instead.', 'danger')
                return redirect(url_for('login'))

            password = generate_password_hash(
                form.password.data,
                method='pbkdf2:sha256',
                salt_length=8
            )

            # TODO: Validate uploaded profile images
            # TODO: Limit image size
            # TODO: Resize images before saving
            profile_pic_file = form.profile_pic.data

            if profile_pic_file:
                #TODO make sure the form has enctype="multipart/form-data"
                profile_pic_name = f"{uuid.uuid4()}_{secure_filename(profile_pic_file.filename)}"
                profile_pic_file.save(os.path.join(app.config['UPLOAD_FOLDER'], profile_pic_name))

            new_user = User(
                first_name=form.first_name.data,
                last_name=form.last_name.data,
                email=email,
                password=password,
                profile_pic=profile_pic_name if profile_pic_file else None,
                last_logged_in=None
            )
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user)

            return redirect(url_for('home'))
        return render_template('register.html', register_form=form)


    # TODO add remember me functionality
    # TODO consider using next functionality which allows users to be redirected to where they were after logging in
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        login_form = LoginForm()

        if login_form.validate_on_submit():
            email = login_form.email.data.lower()
            password = login_form.password.data
            user = db.session.execute(db.select(User).where(User.email==email)).scalar_one_or_none()

            if not user:
                flash("Invalid email or password.","danger")
                return redirect(url_for('register_user'))

            if not check_password_hash(user.password, password):
                flash("Invalid email or password.","danger")
                return redirect(url_for('login'))

            user.last_logged_in = dt.datetime.now()
            login_user(user)
            db.session.commit()

            return redirect(url_for('home'))
        return render_template('login.html', login_form=login_form)


    # TODO: Finalize logout action to POST and style submit button as navbar link
    @app.route('/logout', methods=['POST'])
    @login_required
    def logout():
        logout_user()
        flash("You have been logged out.", "success")

        return redirect(url_for('home'))


    @app.route('/list_users')
    @login_required
    @admin_required
    def list_users():
        users = db.session.execute(db.select(User).where(User.is_protected.is_(False)).order_by(User.id)).scalars().all()

        return render_template('list_users.html', users=users)


    #TODO restyle the form buttons
    @app.route('/switch/<int:user_id>', methods=['POST'])
    @login_required
    @admin_required
    def switch_admin(user_id):
        user = db.get_or_404(User, user_id)

        if user.id == current_user.id:
            flash('You cannot change your own admin status', 'danger')
            return redirect(url_for('list_users'))

        if user.is_protected:
            flash('This user is protected. You cannot change the permission.', 'danger')

        user.is_admin = not user.is_admin
        db.session.commit()

        flash(f'User {user.first_name} {user.last_name} has now been updated.', 'success')

        return redirect(url_for('list_users'))


    @app.route('/delete_user/<int:user_id>', methods=['POST'])
    @login_required
    @admin_required
    def delete_user(user_id):
        user = db.get_or_404(User, user_id)

        if user.id == current_user.id:
            flash('You cannot delete your own account', 'danger')
            return redirect(url_for('list_users'))

        if user.is_protected:
            flash('This user is protected. It cannot be deleted.', 'danger')
            return redirect(url_for('list_users'))

        if user.has_posts:
            flash('This user created blog posts. It cannot be deleted.', 'danger')
            return redirect(url_for('list_users'))

        if user.has_comments:
            flash(
                'This user commented on blog posts. Existing comments will remain, but the author information will be removed.',
                'warning'
            )

        db.session.delete(user)
        db.session.commit()

        flash(f'User {user.first_name} {user.last_name} has now been deleted.', 'success')
        return redirect(url_for('list_users'))


    @app.route('/user_profile/<int:user_id>')
    @login_required
    def user_profile(user_id):
        user = db.get_or_404(User, user_id)
        return render_template('user_detail_profile.html', user=user)


    @app.route('/usr_settings/<int:user_id>', methods=['GET', 'POST'])
    @login_required
    def user_settings(user_id):
        user = db.get_or_404(User, user_id)
        if user.id != current_user.id:
            abort(403)

        picture_form = PictureForm()
        user_form = UpdateUserForm(obj=user)
        password_form = ChangePasswordForm()

        if user_form.submit.data and user_form.validate_on_submit():

            existing_user = db.session.execute(
                db.select(User).where(User.email == user_form.email.data.lower())
            ).scalar_one_or_none()

            if existing_user and existing_user.id != user.id:
                flash('This email address already exists', 'danger')

                return redirect(url_for('usr_settings'))

            user.first_name=user_form.first_name.data
            user.last_name=user_form.last_name.data
            user.email=user_form.email.data.lower()
            db.session.commit()
            flash('Details updated successfully.', 'success')

            return redirect(url_for('user_settings', user_id=user.id))

        elif picture_form.update.data and picture_form.validate_on_submit():

            #TODO eventually have a helper function
            profile_pic_file = picture_form.image.data

            if profile_pic_file:
                profile_pic_name = f"{uuid.uuid4()}_{secure_filename(profile_pic_file.filename)}"
                profile_pic_file.save(os.path.join(app.config['UPLOAD_FOLDER'], profile_pic_name))
                user.profile_pic = profile_pic_name
                db.session.commit()
                flash('Profile picture updated successfully.', 'success')

                return redirect(url_for('user_settings', user_id=user.id))

        elif password_form.update.data and password_form.validate_on_submit():
            old_password = password_form.old_password.data

            if not check_password_hash(user.password, old_password):
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
                flash('Password updated successfully.', 'success')

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