from dotenv import load_dotenv
import os
import re
import json
import mysql.connector

print(os.getcwd()) 
with open('data/taipei-attractions.json', 'r', encoding='utf-8') as file:
    data = json.load(file)

load_dotenv()

try:
    cnx = mysql.connector.connect(
            user = os.getenv("MYSQL_USER"), 
            password = os.getenv("MYSQL_PASSWORD"),
            host=os.getenv("MYSQL_HOST"),
        )
    cursor = cnx.cursor()

    cursor.execute("CREATE DATABASE IF NOT EXISTS taipei_day_trip")
    cursor.execute("USE taipei_day_trip")
    cursor.execute("""CREATE TABLE IF NOT EXISTS mrt_stations (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(255) UNIQUE NOT NULL
        );""")

    cursor.execute("""CREATE TABLE IF NOT EXISTS taipei_attractions (
        id INT PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        category VARCHAR(255) NOT NULL,
        description TEXT,
        address VARCHAR(255),
        transport TEXT,
        mrt_id INT,
        lat DECIMAL(9, 6),
        lng DECIMAL(9, 6),
        images JSON,
        FOREIGN KEY (mrt_id) REFERENCES mrt_stations(id) ON DELETE SET NULL
        );""")
    
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
        if mrt:
            cursor.execute("SELECT id FROM mrt_stations WHERE name = %s", (mrt,))
            mrt_result = cursor.fetchone()
            if mrt_result:
                mrt_id = mrt_result[0]
            else:
                cursor.execute("INSERT INTO mrt_stations (name) VALUES (%s)", (mrt,))
                mrt_id = cursor.lastrowid
        else:
            mrt_id = None
        sql_query = """INSERT INTO taipei_attractions(id, name, category, description, address, transport, mrt_id, lat, lng, images) 
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
        data_tuple = (_id, name, category, description, address, transport, mrt_id, lat, lng, json.dumps(images))
        cursor.execute(sql_query, data_tuple)
    cnx.commit()
        
    cursor.execute("""CREATE TABLE users (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        email VARCHAR(255) UNIQUE NOT NULL,
        password VARCHAR(255) NOT NULL
        );""")
    
    cursor.close()
    cnx.close()

except mysql.connector.Error as err:
    print(f"Error: {err}")

    
