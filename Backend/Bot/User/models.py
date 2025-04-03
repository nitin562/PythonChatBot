from Bot import db
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String
from werkzeug.security import generate_password_hash, check_password_hash
class User(db.Model):
    id:Mapped[int]=mapped_column(primary_key=True)
    username:Mapped[str]=mapped_column(unique=True,nullable=False)
    name:Mapped[str]=mapped_column(String(30),nullable=False)
    email:Mapped[str]=mapped_column(String(100),nullable=False,unique=True)
    pwd_hash:Mapped[str]=mapped_column(nullable=False)
    
    
    def set_password(self,pwd):
        self.pwd_hash=generate_password_hash(pwd)
    
    def check_password(self,pwd):
        return check_password_hash(self.pwd_hash,pwd)