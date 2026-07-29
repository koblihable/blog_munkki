from wtforms import StringField, PasswordField
from wtforms.fields.simple import SubmitField, TextAreaField, FileField
from wtforms.validators import DataRequired, Regexp, Length, EqualTo, Email
from flask_wtf import FlaskForm
from flask_ckeditor import CKEditorField


# TODO add tests
EMAIL_VALIDATORS = [
    DataRequired(),
    Email(message="Please enter a valid email address")
]

# create blog post
class BlogForm(FlaskForm):
    #TODO add a validator for a unique title
    title = StringField(label='Title', validators=[DataRequired()])
    subtitle = StringField(label='Subtitle', validators=[DataRequired()])
    body = CKEditorField(label='Text', validators=[DataRequired()])
    img_url = StringField(label='Image')
    submit = SubmitField(label='Post')

# create/ update a user
class UserForm(FlaskForm):
    #TODO fileAllowed, fileRequired
    password_error = 'Password must be at least 8 characters long'
    first_name = StringField(label='First Name', validators=[DataRequired()])
    last_name = StringField(label='Last Name', validators=[DataRequired()])
    profile_pic = FileField(label='Profile Picture')
    email = StringField(
        label='Email',
        validators=[DataRequired(), Email(message="Please enter a valid email address")]
    )
    password = PasswordField(
        label='Password',
        validators=[DataRequired(), Length(min=8, message=password_error)],
    )
    submit = SubmitField(label='Submit')

class UpdateUserForm(FlaskForm):
    first_name = StringField(label='First Name', validators=[DataRequired()])
    last_name = StringField(label='Last Name', validators=[DataRequired()])
    email = StringField(
        label='Email',
        validators=EMAIL_VALIDATORS
    )
    submit = SubmitField(label='Update')

# user login
class LoginForm(FlaskForm):
    email = StringField(label='Email', validators=EMAIL_VALIDATORS)
    password = PasswordField(label='Password', validators=[DataRequired()])
    submit = SubmitField(label='Submit')

# message form
class ContactForm(FlaskForm):
    name = StringField(label='Name', validators=[DataRequired()])
    email = StringField(label='Email', validators=EMAIL_VALIDATORS)
    phone = StringField(label='Phone')
    message = TextAreaField(label='Message', validators=[DataRequired()])
    submit = SubmitField(label='Submit')

# comment form
class CommentForm(FlaskForm):
    comment = TextAreaField(label='Comment', validators=[DataRequired()])
    submit = SubmitField(label='Submit')

# picture form
class PictureForm(FlaskForm):
    # TODO fileAllowed, fileRequired
    image = FileField(label='')
    update = SubmitField(label='Submit')

class ChangePasswordForm(FlaskForm):
    old_password = PasswordField(label='Old Password', validators=[DataRequired()])
    new_password = PasswordField(label='New Password', validators=[DataRequired()])
    check_password = PasswordField(
        "Confirm password",
        validators=[
            DataRequired(),
            EqualTo("new_password", message="Passwords must match.")
        ]
    )
    update = SubmitField(label='Update')