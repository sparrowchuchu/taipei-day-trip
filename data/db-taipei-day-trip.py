from dotenv import load_dotenv
import os
import re
import json
import mysql.connector

with open('taipei-attractions.json', 'r', encoding='utf-8') as file:
    data = json.load(file)

load_dotenv(dotenv_path='../.env')
password = os.getenv("PASSWORD")

try:
    cnx = mysql.connector.connect(
        user='root', 
        password = password,
        host='127.0.0.1',
        database='taipei_day_trip'
    )
    cursor = cnx.cursor()

    cursor.execute("CREATE DATABASE IF NOT EXISTS taipei_day_trip")
    cursor.execute("USE taipei_day_trip")
    cursor.execute("""CREATE TABLE IF NOT EXISTS taipei_attractions(
        id INT PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        category VARCHAR(255) NOT NULL,
        description TEXT,
        address VARCHAR(255),
        transport TEXT,
        mrt VARCHAR(255),
        lat DECIMAL(9, 6),
        lng DECIMAL(9, 6),
        images JSON
        )""")

    for i in data["result"]["results"]:    
        _id= i["_id"]
        name = i["name"]
        category = i["CAT"]
        description = i["description"]
        address = i["address"]
        transport = i["direction"]
        mrt = i["MRT"]
        lat = i["latitude"]
        lng = i["longitude"]
        pattern = r'https:.+?\.jpg|png'
        images = re.findall(pattern, i["file"], flags=re.IGNORECASE)
        
        sql_query = """INSERT INTO taipei_attractions(id, name, category, description, address, transport, mrt, lat, lng, images) 
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
        data_turple = (_id, name, category, description, address, transport, mrt, lat, lng, json.dumps(images))
        
        cursor.execute(sql_query, data_turple)
        cnx.commit()
        
    cursor.close()
    cnx.close()

except:
    print("Error: unable to connect to MySQL")
else:
    print("Data inserted successfully")
    


