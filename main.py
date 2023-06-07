from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime, timedelta
import jwt
from uuid import uuid4
from fastapi.param_functions import Query

app = FastAPI()

# Thiết lập cấu hình JSON Web Token (JWT).
JWT_SECRET_KEY = "c0b8ab2d4a29cb85a121f38f42f324b8c6b2b302d28e6f7bf2bb61e0e1097619"
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_TIME_MINUTES = 30

# Định nghĩa lớp User.
class User(BaseModel):
    id: str
    full_name: str
    birthday: datetime
    gender: str
    phone_number: str
    address: str

    def __init__(self, **kwargs):
        if 'id' not in kwargs:
            kwargs['id'] = str(uuid4())
        super().__init__(**kwargs)


# Khởi tạo danh sách người dùng giả lập.
fake_users = [
    User(
        full_name = "Nguyen Van A",
        birthday=datetime.strptime("1990-01-01", "%Y-%m-%d"),
        gender="Male",
        phone_number="0123456789",
        address="Hà Nội"
    ),
    User(
        full_name="Lê Thị B",
        birthday=datetime.strptime("1995-02-01", "%Y-%m-%d"),
        gender="Female",
        phone_number="0987654321",
        address="Sài Gòn"
    )
]


# Tạo mã thông báo JWT (JSON Web Token).
def create_jwt_token(username: str):
    expiration = datetime.utcnow() + timedelta(minutes=JWT_EXPIRATION_TIME_MINUTES)
    jwt_payload = {"sub": username, "exp": expiration}
    jwt_token = jwt.encode(jwt_payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return jwt_token


# Kiểm tra thông tin đăng nhập và trả về JWT nếu đăng nhập thành công.
def authenticate_user(username: str, password: str):
    if username == "admin" and password == "password":
        return create_jwt_token(username)
    else:
        raise HTTPException(status_code=401, detail="Incorrect username or password")


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")


# Hàm giải mã JWT token và kiểm tra tính hợp lệ của nó.
def decode_jwt_token(token: str):
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        username = payload.get('sub')
        return username
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


# Tạo đường dẫn /token để đăng nhập và lấy JWT.
@app.post("/token")
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    jwt_token = authenticate_user(form_data.username, form_data.password)
    return {"access_token": jwt_token, "token_type": "bearer"}


# API để đăng ký các thông tin người dùng mới.
@app.post("/users", response_model=User)
def create_user(user: User, token: str = Depends(oauth2_scheme)):
    try:
        # Kiểm tra tính hợp lệ của JWT token
        username = decode_jwt_token(token)

        # Them user_id moi vao user duoc tao tu client.
        # user.user_id = str(uuid.uuid4())

        # Giả lập lưu thông tin người dùng vào cơ sở dữ liệu.
        fake_users.append(user)

        # Tra ve nguoi dung moi tao ra co id moi.
        return user
    except:
        raise HTTPException(status_code=401, detail="Invalid token or unauthorized access")


# API để lấy thông tin chi tiết của một người dùng.
@app.get("/users/{user_id}", response_model=User)
def read_user(user_id: str, token: str = Depends(oauth2_scheme)):
    try:
        # Kiểm tra tính hợp lệ của JWT token
        username = decode_jwt_token(token)

        # Giả lập truy vấn thông tin người dùng từ cơ sở dữ liệu.
        for user in fake_users:
            if user.id == user_id:
                return user
        raise HTTPException(status_code=404, detail="User not found")
    except:
        raise HTTPException(status_code=401, detail="Invalid token or unauthorized access")


# API để cập nhật thông tin người dùng.
@app.put("/users/{user_id}", response_model=User)
def update_user(user_id: str, user: User, token: str = Depends(oauth2_scheme)):
    try:
        # Kiểm tra tính hợp lệ của JWT token
        username = decode_jwt_token(token)

        # Giả lập cập nhật thông tin người dùng trong cơ sở dữ liệu.
        for i, u in enumerate(fake_users):
            if u.id == user_id:
                fake_users[i] = user
                return user
        raise HTTPException(status_code=404, detail="User not found")
    except:
        raise HTTPException(status_code=401, detail="Invalid token or unauthorized access")


# API để xóa một người dùng.
@app.delete("/users/{user_id}")
def delete_user(user_id: str, token: str = Depends(oauth2_scheme)):
    try:
        # Kiểm tra tính hợp lệ của JWT token
        username = decode_jwt_token(token)

        # Giả lập xóa thông tin người dùng ra khỏi cơ sở dữ liệu.
        for i, user in enumerate(fake_users):
            if user.id == user_id:
                del fake_users[i]
                return {"message": "User deleted successfully"}
        raise HTTPException(status_code=404, detail="User not found")
    except:
        raise HTTPException(status_code=401, detail="Invalid token or unauthorized access")


# API để lấy danh sách tất cả người dùng đã đăng ký.
@app.get("/users", response_model=List[User])
def list_users(token: str = Depends(oauth2_scheme)):
    try:
        # Kiểm tra tính hợp lệ của JWT token
        username = decode_jwt_token(token)

        # Giả lập truy vấn danh sách người dùng từ cơ sở dữ liệu.
        return fake_users
    except:
        raise HTTPException(status_code=401, detail="Invalid token or unauthorized access")
