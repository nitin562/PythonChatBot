from flask import request,jsonify
from .forms import RegisterForm,LoginForm
from .helper import getJwt
from Bot.responses import success,error
def register_controller():
    Form=RegisterForm(request.form)
    if Form.validate_on_submit():
        try:
            registered_user=Form.save()

        except Exception as e:
            print(e)
            return error(500,"server","Database Issue")
        else:
            token=getJwt({
                "id":registered_user.id,
                "email":registered_user.email
            })
            return success(200,"register",token)
    else:
        print(Form.errors)
        return error(400,"form",error=Form.errors)    
def login_controller():
    Form=LoginForm(request.form)
    if Form.validate_on_submit():
        user=Form.get_user()
        token=getJwt({
                "id":user.id,
                "email":user.email
            })
        return success(200,"register",token)