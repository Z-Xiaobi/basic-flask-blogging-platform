'''
Forms in webpage
'''


from flask_wtf import FlaskForm,Form

# field types
from wtforms import StringField, IntegerField,PasswordField, SubmitField,BooleanField
from wtforms import TextAreaField,FileField
from wtforms.fields.html5 import DateField
from wtforms.validators import DataRequired,ValidationError,Length,Email,Regexp,EqualTo
from wtforms.ext.sqlalchemy.fields import QuerySelectField

from wtforms import widgets
from wtforms import validators

from .models import User
# page down
from flask_pagedown.fields import PageDownField

class UserLoginForm(FlaskForm):
    # username = StringField('username',validators=[DataRequired('username is null')])
    email = StringField('email',validators=[DataRequired(),Length(1,64),Email()])
    password = PasswordField('password',validators=[DataRequired('password is null')])
    # if remember_me is true, will write a cookie for user session
    # if false, close the browser, relogin is needed
    remember_me = BooleanField('Keep me logged in')
    submit = SubmitField('login')
    #


class UserRegisterForm(FlaskForm):
    username = StringField('username',
                           validators=[DataRequired('username is null'),
                                       validators.Length(min=6, max=32,
                                                         message='username must longer than %(min)d, shorter than %(max)d'),],
                           widget=widgets.TextInput('username is null'),
                           render_kw={'class': 'form-control'},
                           # default='alex'
                           )
    email = StringField('email', validators=[DataRequired(), Length(1, 64), Email()])

    password = PasswordField('password',
                           validators=[
                               DataRequired(),
                               Length(min=6, message='password must longer than %(min)d'),
                               # validators.regexp('^[A-Za-z][A-Za-z0-9_.]*$',0,'Usersname must have only letters numbers, dots'
                               #                   ' or underscores')
                               Regexp(
                                   regex="^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[$@$!%*?&])[A-Za-z\d$@$!%*?&]{6,}",
                                   message='password must have at least 1 uppercase letter，1 lowercase letter，1 number，1 special character'
                               )
                           ])
    password_confirm = PasswordField('password_confirm',
                                     validators=[
                                         DataRequired(message='repeat password is null'),
                                         EqualTo('password', message="two passwords are not equal")
                                     ],
                                     widget=widgets.PasswordInput(),
                                     render_kw={'class': 'form-control'}

    )
    submit = SubmitField('submit')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Username already exist!')
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Email already exist!')



class PostForm(FlaskForm):
    title = StringField(validators=[DataRequired()])
    # body = TextAreaField("What's on your mind",validators=[DataRequired()])
    body = PageDownField("What's on your mind?",validators=[DataRequired()])
    submit = SubmitField('Submit')




class EditProfileForm(FlaskForm):

    location = StringField('Location',validators=[Length(0,64)])
    submit = SubmitField('Submit')

    # about_me = TextAreaField('About me')
class EidtProfilePicForm(FlaskForm):
    avatar = FileField('Avatar')

class PasswordResetForm(FlaskForm):
    # email = StringField('email', validators=[DataRequired(), Length(1, 64), Email()])
    old_password = PasswordField('Old password', validators=[DataRequired()])
    password = PasswordField('password',
                           validators=[
                               DataRequired(),
                               Length(min=6, message='password must longer than %(min)d'),
                               # validators.regexp('^[A-Za-z][A-Za-z0-9_.]*$',0,'Usersname must have only letters numbers, dots'
                               #                   ' or underscores')
                               Regexp(
                                   regex="^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[$@$!%*?&])[A-Za-z\d$@$!%*?&]{6,}",
                                   message='password must have at least 1 uppercase letter，1 lowercase letter，1 number，1 special character'
                               )
                           ])
    password_confirm = PasswordField('password_confirm',
                                     validators=[
                                         DataRequired(message='repeat password is null'),
                                         EqualTo('password', message="two passwords are not equal")
                                     ],
                                     widget=widgets.PasswordInput(),
                                     render_kw={'class': 'form-control'}

                                     )
    submit = SubmitField('Change Password')

class CommentForm(FlaskForm):
    body = StringField('Enter your comment', validators=[DataRequired()])
    submit = SubmitField('Submit')


class SearchForm(FlaskForm):
    body = StringField()
    submit = SubmitField()

class SetModeratorForm(FlaskForm):
    email = StringField(validators=[DataRequired(),Length(1,64),Email()])
    submit = SubmitField()
