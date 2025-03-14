from dotenv import load_dotenv
import os
import mysql.connector
import json
from fastapi import *
from fastapi.responses import JSONResponse
from fastapi.responses import FileResponse
from typing import Annotated, Optional

app=FastAPI()

load_dotenv(dotenv_path='../.env')
password = os.getenv("PASSWORD")

def get_db_connection(password):
	return mysql.connector.connect(
		host="127.0.0.1",		
		user="root",
		password = password,
		database="taipei_day_trip"
	)

@app.get("/api/attractions")
async def api_attractions(page: Annotated[int, Query(ge=0)],
						  keyword: Annotated[Optional[str], Query()] = None
						  ):
	limit = 12
	offset = page * limit
	try:
		cnx = get_db_connection(password)
		cursor = cnx.cursor()
		if keyword == None:
			cursor.execute("SELECT * FROM taipei_attractions LIMIT %s OFFSET %s", (limit, offset))
		else:
			cursor.execute("SELECT * FROM taipei_attractions WHERE mrt LIKE %s OR name LIKE %s LIMIT %s OFFSET %s", ("%" + keyword + "%", "%" + keyword + "%", limit, offset))
		results = cursor.fetchall()
		if not results:
			message = "查無資料"
			return JSONResponse(status_code=400, content={"error": True, "message": message})
	except:
		message = "伺服器內部錯誤"
		return JSONResponse(status_code=500, content={"error": True, "message": message})
	else:
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
		print(data)
		return JSONResponse({"nextPage":next_page,"data": data})

@app.get("/api/attraction/{attractionId}")
async def api_attraction(attractionId: Annotated[int, Path(...)]):
	try:
		cnx = get_db_connection(password)
		cursor = cnx.cursor()
		cursor.execute("SELECT * FROM taipei_attractions WHERE id = %s", (attractionId,))
		result = cursor.fetchone()
		if result == None:
			message = "景點編號不正確"
			return JSONResponse(status_code=400, content={"error": True, "message": message})
	except:
		message = "伺服器內部錯誤"
		return JSONResponse(status_code=500, content={"error": True, "message": message})
	else:
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
		cnx = get_db_connection(password)
		cursor = cnx.cursor()
		cursor.execute("SELECT mrt FROM taipei_attractions WHERE mrt IS NOT NULL GROUP BY mrt ORDER BY COUNT(mrt) DESC")
		results = cursor.fetchall()
	except:
		message = "伺服器內部錯誤"
		return JSONResponse(status_code=500, content={"error": True, "message": message})
	else:
		data = results
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


if __name__ ==  "__main__":
    os.system("uvicorn app:app")
