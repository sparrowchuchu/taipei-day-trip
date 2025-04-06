from datetime import datetime, timedelta, timezone
from typing import Annotated, Optional
from dotenv import load_dotenv
import os
import mysql.connector
import json
import jwt
from passlib.context import CryptContext
from fastapi import *
from fastapi.responses import JSONResponse
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.security import OAuth2PasswordBearer


load_dotenv()

MYSQL_USER = os.getenv("MYSQL_USER")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
MYSQL_HOST = os.getenv("MYSQL_HOST")
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE")

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
TOKEN_EXPIRE_MINUTES = os.getenv("TOKEN_EXPIRE_MINUTES")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

app=FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_jwt_token(data: dict, expires_delta: timedelta | None = None):
	to_encode = data.copy()
	if expires_delta:
		expire = datetime.now(timezone.utc) + expires_delta
	else:
		expire = datetime.now(timezone.utc) + timedelta(minutes=int(TOKEN_EXPIRE_MINUTES))
	to_encode.update({"exp": expire})
	return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_jwt_token(token: str) -> Optional[dict]:
	try:
		return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
	except jwt.ExpiredSignatureError as e:
		print(f"Token expired: {e}")
		return None
	except jwt.InvalidTokenError as e:
		print(f"Invalid token: {e}")
		return None
		
def get_db_connection():
	return mysql.connector.connect(
		user = MYSQL_USER, 
        password = MYSQL_PASSWORD,
        host = MYSQL_HOST,
        database = MYSQL_DATABASE
	)


@app.post("/api/user")
async def user_signup( 
	request: Request,
	payload: Annotated[dict, Body()]
	):
	name = payload.get("name")
	email = payload.get("email")
	password = payload.get("password")
	if not email or not password:
		return JSONResponse(status_code=400, content={"message": "請提供 Email 和 Password"})
	try:
		cnx = get_db_connection()
		cursor = cnx.cursor()
		cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
		if cursor.fetchone():
			cnx.close()
			return JSONResponse(status_code=400, content={"error": True, "message": "Email 已註冊"})
		hashed_pw = get_password_hash(password)
		sql_query = """INSERT INTO users (name, email, password) VALUES (%s, %s, %s)"""
		cursor.execute(sql_query, (name, email, hashed_pw))
		cnx.commit()
		return JSONResponse({"ok": True})
	except Exception as e:
		print(f"Error: {e}")
		return JSONResponse(status_code=500, content={"error": True, "message": "伺服器內部錯誤"})
	finally:
		cursor.close()
		cnx.close()
		
@app.get("/api/user/auth")
def get_current_user(token: str = Depends(oauth2_scheme)):
	decoded_token = decode_jwt_token(token)
	if not decoded_token:
		return JSONResponse(status_code=200, content={"data": None})
	user_info = {
        "id": decoded_token["id"],
        "name": decoded_token["name"],
        "email": decoded_token["email"]
    }
	return JSONResponse(status_code=200, content={"data": user_info})

@app.put("/api/user/auth")
def user_signin(request: Request,
    payload: Annotated[dict, Body()]
	):
	email = payload.get("email")
	password = payload.get("password")
	if not email or not password:
		return JSONResponse(status_code=400, content={"message": "請提供 Email 和 Password"})
	try:
		cnx = get_db_connection()
		cursor = cnx.cursor(dictionary=True)
		cursor.execute("SELECT id, name, email, password FROM users WHERE email = %s", (email,))
		user_data = cursor.fetchone()
	except Exception as e:
		print(f"Error: {e}")
	finally:
		cursor.close()
		cnx.close()
	if not user_data or not verify_password(password, user_data["password"]):
		JSONResponse(status_code=401, content={"message": "帳號或密碼錯誤"})
	token = create_jwt_token({"id": user_data["id"], "name": user_data["name"], "email": user_data["email"]})
	return {"token": token}


@app.get("/api/attractions")
async def api_attractions(page: Annotated[int, Query(ge=0)],
						  keyword: Annotated[Optional[str], Query()] = None
						  ):
	limit = 12
	offset = page * limit
	try:
		cnx = get_db_connection()
		cursor = cnx.cursor()
		if keyword:
			sql_query = """
                SELECT t.id, t.name, t.category, t.description, t.address, t.transport, 
                       m.name AS mrt, t.lat, t.lng, t.images
                FROM taipei_attractions t
                LEFT JOIN mrt_stations m ON t.mrt_id = m.id
                WHERE t.name LIKE %s OR m.name LIKE %s
                LIMIT %s OFFSET %s
            """
			cursor.execute(sql_query, ("%" + keyword + "%", "%" + keyword + "%", limit, offset))
		else:
			sql_query = """
                SELECT t.id, t.name, t.category, t.description, t.address, t.transport, 
                       m.name AS mrt, t.lat, t.lng, t.images
                FROM taipei_attractions t
                LEFT JOIN mrt_stations m ON t.mrt_id = m.id
                LIMIT %s OFFSET %s
            """
			cursor.execute(sql_query, (limit, offset))
		results = cursor.fetchall()
	except Exception as e:
		print(f"Error: {e}")
		return JSONResponse(status_code=500, content={"error": True, "message": "伺服器內部錯誤"})
	finally:
		cursor.close()
		cnx.close()	
	if not results:
			return JSONResponse(status_code=400, content={"error": True, "message": "查無資料"})
	next_page = page + 1 if len(results) == limit else None 
	data = []
	for result in results:
		dict = {
		"id": result[0],
		"name": result[1],
		"category": result[2],
		"description": result[3],
		"address": result[4],
		"transport": result[5],
		"mrt": result[6],
		"latitude": str(result[7]),
		"longitude": str(result[8]),
		"images": json.loads(result[9])
		}
		data.append(dict)
	return JSONResponse({"nextPage":next_page,"data": data})

@app.get("/api/attraction/{attractionId}")
async def api_attraction(attractionId: Annotated[int, Path(...)]):
	try:
		cnx = get_db_connection()
		cursor = cnx.cursor()
		sql_query = """
            SELECT t.id, t.name, t.category, t.description, t.address, t.transport, 
                   m.name AS mrt, t.lat, t.lng, t.images
            FROM taipei_attractions t
            LEFT JOIN mrt_stations m ON t.mrt_id = m.id
            WHERE t.id = %s
        """
		cursor.execute(sql_query, (attractionId,))
		result = cursor.fetchone()
	except Exception as e:
		print(f"Error: {e}")
		return JSONResponse(status_code=500, content={"error": True, "message": "伺服器內部錯誤"})
	finally:
		cursor.close()
		cnx.close()
	if result == None:
			return JSONResponse(status_code=400, content={"error": True, "message": "景點編號不正確"})
	data = {
		"id": result[0],
		"name": result[1],
		"category": result[2],
		"description": result[3],
		"address": result[4],
		"transport": result[5],
		"mrt": result[6],
		"latitude": str(result[7]),
		"longitude": str(result[8]),
		"images": json.loads(result[9])
	}
	return JSONResponse({"data": data})

@app.get("/api/mrts")
async def api_mrts():
	try:
		cnx = get_db_connection()
		cursor = cnx.cursor()
		cursor.execute("SELECT name FROM mrt_stations;")
		results = cursor.fetchall()
	except Exception as e:
		print(f"Error: {e}")
		return JSONResponse(status_code=500, content={"error": True, "message": "伺服器內部錯誤"})	
	finally:
		cursor.close()
		cnx.close()
	data = [mrt for mrt in results]
	return JSONResponse({"data": data})


# Static Pages (Never Modify Code in this Block)
@app.get("/", include_in_schema=False)
async def index(request: Request):
	return FileResponse("./static/index.html", media_type="text/html")
@app.get("/attraction/{id}", include_in_schema=False)
async def attraction(request: Request, id: int):
	return FileResponse("./static/attraction.html", media_type="text/html")
@app.get("/booking", include_in_schema=False)
async def booking(request: Request):
	return FileResponse("./static/booking.html", media_type="text/html")
@app.get("/thankyou", include_in_schema=False)
async def thankyou(request: Request):
	return FileResponse("./static/thankyou.html", media_type="text/html")

