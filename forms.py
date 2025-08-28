from wtforms import StringField, SelectField, SubmitField, PasswordField, EmailField, BooleanField, FileField, RadioField
from flask_wtf import FlaskForm
from wtforms.validators import DataRequired, Email

class SignupForms(FlaskForm):
    username = StringField("Username", validators=[DataRequired(message="Enter your username")], render_kw={"placeholder":"Enter your name"})
    email = EmailField("Email", validators=[DataRequired(message="Enter a valid email address")], render_kw={"placeholder":"Enter your email"})
    password = PasswordField("Password", validators=[DataRequired(message="Enter a strong pass")], render_kw={"placeholder":"Enter your password"})
    submit = SubmitField("Submit")

class LoginForms(FlaskForm):
    username = StringField("Username", validators=[DataRequired(message="Enter your username")], render_kw={"placeholder":"Username"})
    password = PasswordField("Password",validators=[DataRequired(message="Enter your password")], render_kw={"placeholder":"Password"})
    submit = SubmitField("Submit")
    remember = BooleanField("Remember me")

class ProfileSet(FlaskForm):
    fullname = StringField("Fulname", validators=[DataRequired(message="Enter you fullname")])
    avatar = FileField("Avatar", validators=[DataRequired(message="Select a profile picture")])

#Welcome page/landing page