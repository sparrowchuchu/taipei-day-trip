# 匯入必要套件
import mysql.connector
from dotenv import load_dotenv
import os

# 載入 .env 檔案
load_dotenv()

# 取得密碼環境變數
password = os.getenv("PASSWORD")

# 測試連線函式
def test_connection():
    try:
        # 建立資料庫連線
        cnx = mysql.connector.connect(
            host="127.0.0.1",  # 若資料庫在其他機器，改成 EC2 私有 IP 或公有 IP
            user="root",
            password=password,
            database="taipei_day_trip"
        )

        # 建立 cursor 並測試查詢
        cursor = cnx.cursor()
        cursor.execute("SELECT DATABASE()")
        db_name = cursor.fetchone()[0]

        print("✅ 資料庫連線成功！目前使用的資料庫：", db_name)
        
        # 測試撈資料
        cursor.execute("SELECT COUNT(*) FROM taipei_attractions")
        attraction_count = cursor.fetchone()[0]
        print("景點資料筆數：", attraction_count)

        # 關閉連線
        cursor.close()
        cnx.close()

    except mysql.connector.Error as err:
        print("❌ 連線失敗，錯誤訊息：", err)

if __name__ == "__main__":
    print("正在測試資料庫連線...")
    print("使用密碼：", password)
    test_connection()
