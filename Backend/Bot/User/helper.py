import jwt
from functools import wraps
from flask import request,jsonify
from Bot.responses import error
import secrets
# Generate a secure 256-bit (32-byte) key
jwt_secret_key = secrets.token_hex(32)  


def getJwt(payload):
    return jwt.encode(payload=payload,key=jwt_secret_key,algorithm="HS256")

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