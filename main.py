# from jinja2 import Template
from dotenv import load_dotenv
import datetime as dt
import os,sqlite3
import test.sql as sql
import test.form as form
import test.chat as chat
from flask import Flask, render_template
app = Flask(__name__)

# 加載測試環境配置
load_dotenv(dotenv_path='.env.testing')

# 配置資料庫設定
# 確保 SQL 資料夾存在
# if not os.path.exists('SQL'):
#     os.makedirs('SQL')

# sqlite:///relative/path/to/file.db
# sqlite:////absolute/path/to/file.db
db_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'SQL', 'example.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# 初始化 SQLAlchemy 實例
sql.db.init_app(app)

# 註冊藍圖
app.register_blueprint(sql.sql_bp, url_prefix='/sql')  # 這會將所有路由加上 /sql 前綴
app.register_blueprint(form.form_bp, url_prefix='/form')# 在 form.py 中定义的路由都会自动以 /form 为前缀。
app.register_blueprint(chat.chat_bp, url_prefix='/chat')
# 初始化資料庫（如果尚未存在）
# 執行 db.create_all() 時，Flask-SQLAlchemy 會檢查是否已經存在 example.db 文件
# # 如果不存在，它會自動創建instance\example.db
with app.app_context():
    sql.db.create_all()

@app.route('/')
def index():
    username = 'John'
    # dt模塊、datetime類別
    date = dt.datetime.today().date()
    time = dt.datetime.now().time()
    formatted_time = time.strftime("%H:%M:%S")
    # 頁面須放在templateS資料夾中
    # html變數=python變數
    return render_template('page1.html', username=username, tdate=date, now_time=formatted_time)

@app.route('/user/<name>', methods=['GET'])
def queryDataMessageByName(name):
    print("type(name) : ", type(name))
    return 'String => {}'.format(name)
# --------------
# --------------

if __name__ == '__main__':
    app.run(debug=True)