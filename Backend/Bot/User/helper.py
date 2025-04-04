import jwt
import os
from functools import wraps
from flask import request,jsonify
from Bot.responses import error


jwt_secret_key = os.getenv("secret")
algorithm=os.getenv("algorithm")


def getJwt(payload):
    print(jwt_secret_key)
    return jwt.encode(payload,jwt_secret_key,algorithm)

# decorated as middleware
def token_verify(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            token=None
            if "Authorization" in request.headers:
                token=request.headers["Authorization"].split(" ")[1]
            if not token:
                return error(400,"token","Token is not provided.")
            payload=jwt.decode(token,jwt_secret_key,["HS256"])
            return f(payload,*args, **kwargs)

        except jwt.ExpiredSignatureError:
            return error(401,"token","Token is expired."), 401
        except jwt.InvalidTokenError:
            return error(401,"token","Token is invalid."), 401
    
    return decorated