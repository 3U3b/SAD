# from jinja2 import Template
from dotenv import load_dotenv
import datetime as dt
import os
from test import db  # 正確導入 db 實例
import test.sql as sql
import test.form as form
import test.chat as chat
from flask import Flask, render_template

app = Flask(__name__)

# 加載測試環境配置
load_dotenv(dotenv_path='.env.testing')

db_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'SQL', 'example.db')
chat_db_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'SQL', 'Chat_log.db')
SAD_db_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'SQL', 'SQL.db')

app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'# 設定資料庫類別為 SQLite，且此資料庫為默認資料庫
# 關閉不必要的 SQLAlchemy 功能(追蹤物件的變更並發送訊號) 來提升性能
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # 關閉訊息追蹤
# 配置多個資料庫
app.config['SQLALCHEMY_BINDS'] = {
    'chat_db': f'sqlite:///{chat_db_path}',  # 綁定資料庫，使用__bind_key__ = 'chat_db'指定綁定db
    'SAD_sql_db': f'sqlite:///{SAD_db_path}'
}

# db = SQLAlchemy() # 已在test/__init__.py初始化時運行過了

# 初始化 SQLAlchemy 實例
db.init_app(app)

with app.app_context():
    db.create_all()  # 創建所有資料表


# 註冊藍圖
app.register_blueprint(sql.sql_bp, url_prefix='/sql')  # 這會將所有路由加上 /sql 前綴
app.register_blueprint(form.form_bp, url_prefix='/form')# 在 form.py 中定義的路由都會自動加上 /form 前綴。
app.register_blueprint(chat.chat_bp, url_prefix='/chat')

User_Model = sql.User

@app.route('/')
def index():
    username = 'John'
    # dt模塊、datetime類別
    date = dt.datetime.today().date()
    time = dt.datetime.now().time()
    formatted_time = time.strftime("%H:%M:%S")

    # (html,html使用的變數=python變數)
    return render_template('page1.html', username=username, tdate=date, now_time=formatted_time)

@app.route('/user/<nam>', methods=['GET'])
def queryDataMessageByName(nam):# 在sqlite尋找相關用戶資料(兩種方法)
    a=False
    try:
        user1 = sql.User.query.filter_by(name=nam).first() # 可以過濾出特定屬性的值
        user2 = sql.User.query.get(user1.id) # 取得符合主鍵的值
    except Exception as e:
        print(f'{type(user1)} {user1} is not a user') # 當name在SQL中無符合資料
        a=True
    finally :
        print(f'{type(user1)} "User1: "{user1}') # type = test.sql.User
        if a :
            print(f'user is not exist')
            return 'String => {} is not a user and no exist'.format(nam)
        else:
            print(f'{type(user2)} "User2: "{user2}') # type = test.sql.User
        # print("type(name) : ", type(name))
            return 'String => {} is exist, id is {}'.format(nam,user1.id)
# --------------
# --------------

if __name__ == '__main__':
    app.run(debug=True)