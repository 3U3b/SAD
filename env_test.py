from dotenv import load_dotenv
import os

# 加載測試環境配置
load_dotenv(dotenv_path='.env.testing')

# 讀取環境變數

db_host = os.getenv("DB_HOST")
db_user = os.getenv("DB_USER")
api_key = os.getenv("API_KEY")

print(f"Connecting to test database at {db_host} as {db_user}\nAPI_KEY is {api_key}")
