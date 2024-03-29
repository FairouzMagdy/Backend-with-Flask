from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired, URL, Email, Length
from flask_ckeditor import CKEditorField


# WTForm
class CreatePostForm(FlaskForm):
    title = StringField("Blog Post Title", validators=[DataRequired()])
    subtitle = StringField("Subtitle", validators=[DataRequired()])
    img_url = StringField("Blog Image URL", validators=[DataRequired(), URL()])
    body = CKEditorField("Blog Content", validators=[DataRequired()])
    submit = SubmitField("Submit Post")


# Register Form
class RegisterForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email(message="That's not a valid email address.")])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=8)])
    name = StringField("Name", validators=[DataRequired()])
    submit = SubmitField(label='Register')


# Login Form
class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField(label='Register')


# Comment Form
class CommentForm(FlaskForm):
    comment_text = CKEditorField("Comment")
    submit = SubmitField(label="Submit Comment")
