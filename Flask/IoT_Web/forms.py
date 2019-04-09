from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed #FileField the type of field, FileAllowed is a validator
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from IoT_Web.models import User

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)]) #name must be entered, Length() checks that the name exceed 2 characters and remain within 20
    email = StringField('Email', validators=[DataRequired(), Email()]) #email must be entered, Email() checks to see if the email is valid
    password = PasswordField('Password', validators=[DataRequired()]) #password must be entered
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')]) #password must be re-entered and must match the first password entered
    submit = SubmitField('Sign Up')

    def validate_username(self, username): #check if the username already exists in the db, and if it does show error message
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('The username is already taken')

    def validate_email(self, email): #check if the email already exists in the db, and if it does show error message
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('The email is already taken')


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()]) #name must be entered, Length() checks that the name exceed 2 characters and remain within 20
    password = PasswordField('Password', validators=[DataRequired()]) #password must be entered
    remember = BooleanField('Remember Me') #stay logged in after closing browser, using secure cookies
    submit = SubmitField('Log In')


class UpdateAccountForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png', 'jpeg'])])
    submit = SubmitField('Update')

    def validate_username(self, username):
        if username.data != current_user.username: #if the new username entered is not the same as the current username then update the username
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        if email.data != current_user.email: #if the new email entered is not the same as the current email then update the email
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('That email is taken. Please choose a different one.')

class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    content = TextAreaField('Content', validators=[DataRequired()])
    submit = SubmitField('Post')

class CreateIntance(FlaskForm):
    image_id = StringField('Image ID', validators=[DataRequired()])
    count = SelectField('Count', choices=[('ch1', 'Choice 1'),('ch2', 'Choice 2')], validators=[DataRequired])
    instance_type = StringField('Instance Type', validators=[DataRequired])
    key_name = StringField('Key Name', validators=[DataRequired])
    commands = SelectField('Commands', choices=[('com1','Command 1'), ('com2','Command 2')], validators=[DataRequired])
    instance_info = TextAreaField('Instance Info', validators=[DataRequired])
    submit = SubmitField('Submit')



