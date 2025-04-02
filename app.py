from dotenv import load_dotenv
import os
import mysql.connector
import json
from fastapi import *
from fastapi.responses import JSONResponse
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from typing import Annotated, Optional

app=FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

load_dotenv()

def get_db_connection():
	return mysql.connector.connect(
		user = os.getenv("MYSQL_USER"), 
        password = os.getenv("MYSQL_PASSWORD"),
        host=os.getenv("MYSQL_HOST"),
        database=os.getenv("MYSQL_DATABASE")
	)

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
		raise JSONResponse(status_code=500, detail={"error": True, "message": "伺服器內部錯誤"})
	
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
		raise JSONResponse(status_code=500, detail={"error": True, "message": "伺服器內部錯誤"})
	
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
		raise JSONResponse(
            status_code=500, 
			detail={"error": True, "message": "伺服器內部錯誤"}
			)
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



