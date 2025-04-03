from dotenv import load_dotenv
import os
import mysql.connector
import bcrypt
import json
import jwt
import datetime
from fastapi import *
from fastapi.responses import JSONResponse
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Annotated, Optional

load_dotenv()
MYSQL_USER = os.getenv("MYSQL_USER"), 
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
MYSQL_HOST = os.getenv("MYSQL_HOST")
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE")
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")

app=FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

security = HTTPBearer()

def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode(), salt).decode()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode(), hashed_password.encode())

def create_jwt_token(data: dict):
    payload = data.copy()
    payload["exp"] = datetime.datetime.now(datetime.UTC) + datetime.timedelta(minutes=os.getenv("TOKEN_EXPIRE_MINUTES"))
    token = jwt.encode(payload, SECRET_KEY, algorithm = ALGORITHM)
    return token

def verify_jwt_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload 
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token 已過期")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="無效的 Token")

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    return verify_jwt_token(token)

def get_db_connection():
	return mysql.connector.connect(
		user = MYSQL_USER, 
        password = MYSQL_PASSWORD,
        host = MYSQL_HOST,
        database = MYSQL_DATABASE
	)

@app.post("/api/user")
async def user_signup(user: Annotated[dict, Body()]):
	try:
		cnx = get_db_connection()
		cursor = cnx.cursor()
		cursor.execute("SELECT id FROM users WHERE email = %s", (user["email"],))
		if cursor.fetchone():
			cnx.close()
			return JSONResponse(status_code=400, content={"error": True, "message": "Email 已註冊"})
		hashed_pw = hash_password(user.password)
		sql_query = """INSERT INTO users (name, email, password) VALUES (%s, %s, %s)"""
		cursor.execute(sql_query, (user["name"], user["email"], hashed_pw))
	except Exception as e:
		print(f"Error: {e}")
	finally:
		cursor.close()
		cnx.commit()
		cnx.close()
		return JSONResponse({"message": "註冊成功"})

@app.get("/api/user/auth")
def get_user_info(current_user: dict = Depends(get_current_user)):
    return {"user": current_user}

@app.put("api/user/auth")
def user_signin(user: Annotated[dict, Body()]):
	email = user.get("email")
	password = user.get("password")
	if not email or not password:
		return JSONResponse(status_code=400, detail="請提供 Email 和 Password")
	try:
		conn = get_db_connection()
		cursor = conn.cursor(dictionary=True)
		cursor.execute("SELECT id, name, email, password FROM users WHERE email = %s", (email,))
		user_data = cursor.fetchone()
		conn.close()
	except Exception as e:
		print(f"Error: {e}")
	if not user_data or not verify_password(password, user_data["password"]):
		return JSONResponse(status_code=401, detail="帳號或密碼錯誤")
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
		print(results)
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
		sql_query = """
            SELECT m.name AS mrt, COUNT(t.id) AS attraction_count
            FROM taipei_attractions t
            JOIN mrt_stations m ON t.mrt_id = m.id
            WHERE t.mrt_id IS NOT NULL
            GROUP BY m.name
            ORDER BY attraction_count DESC
        """
		cursor.execute(sql_query)
		results = cursor.fetchall()
	except Exception as e:
		print(f"Error: {e}")
		return JSONResponse(status_code=500, content={"error": True, "message": "伺服器內部錯誤"})
	finally:
		cursor.close()
		cnx.close()
	data = [mrt[0] for mrt in results]
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




