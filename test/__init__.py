# test/__init__.py
from flask_sqlalchemy import SQLAlchemy

# 全域的 SQLAlchemy 實例
db = SQLAlchemy()
print("Initializing the test package") # 初始化時列印一則訊息

# __all__ = ['module1'] # 只有 module1 會被導入
