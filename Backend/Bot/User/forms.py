from flask_wtf import FlaskForm
from Bot import db
from wtforms import StringField,EmailField,PasswordField,ValidationError
from wtforms.validators import DataRequired,Email,Length,EqualTo
from .models import User

class RegisterForm(FlaskForm):
    name = StringField('name', validators=[DataRequired()])
    username = StringField('username', validators=[DataRequired()])
    email=EmailField('email',validators=[DataRequired(),Email()])
    password=PasswordField('password',validators=[Length(min=6)])
    password_match=PasswordField('password_match',validators=[EqualTo('password',message="Password is not matched")])

    class Meta:
        csrf=False

    def validate_username(self,field):
        exist=User.query.filter_by(username=field.data).first()
        if exist:
            raise ValidationError("User Name is already exist.")
        return True

    def validate_email(self,field):
        exist=User.query.filter_by(email=field.data).first()
        if exist:
            raise ValidationError("Email is already exist.")
        return True
    def save(self):
        name=self.name.data
        email=self.email.data
        password=self.password.data
        username=self.username.data
        user=User(name=name,email=email,username=username)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        return user
        
class LoginForm(FlaskForm):
    email=EmailField('email',validators=[DataRequired(),Email()])
    password=PasswordField('password',validators=[Length(min=6)])
    class Meta:
        csrf=False
    def validate(self,*args, **kwargs):
        if not super().validate(*args, **kwargs):
            return False
        
        exist=User.query.filter_by(email=self.email.data).first()
        if not exist:
            self.email.errors.append("Email is not exist")
        elif not exist.check_password(self.password.data):
            self.password.errors.append("Password is not correct")
        else:
            self.validated_user=exist
            return True
        return False

    def get_user(self):
        return self.validated_user
    # def validate_email(self,field):
    #     exist=user.query.filter_by(email=field.data).first()
    #     if not exist:
    #         raise ValidationError("Email is already exist.")
           
    #     return True
        
    