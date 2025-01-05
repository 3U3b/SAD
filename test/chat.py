from dotenv import load_dotenv
from flask import Blueprint, Response, json, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
import google.generativeai as genai
from test import db
# from test.sql import User
import os
import datetime as dt

chat_bp = Blueprint("chat", __name__)

# 加載測試環境配置
load_dotenv(dotenv_path=".env.testing")
# 抓取API
API_key = os.getenv("API_KEY")
genai.configure(api_key=API_key)
# 初始化 Gemini 模型
model = genai.GenerativeModel("gemini-1.5-flash")
now = dt.datetime.now()# 獲取系統(電腦)中時區的日期和時間
# utc_time = dt.now(timezone.utc)  # 獲取UTC(包含時區資訊) #from datetime import timezone
# taipei_tz = timezone(timedelta(hours=8))  # 台北時區 UTC+8
# local_time = utc_time.astimezone(taipei_tz)
date = dt.datetime.today().date()
time = dt.datetime.now().time()
formatted_time = time.strftime("%H:%M:%S")
formatted_date = now.strftime(f"%Y年%m月%d日 %H時%M分%S秒 %A")

flag = True
cached_courses = None
# origin_order = None

class ConversationLog(db.Model):
    __bind_key__ = "chat_db"
    id = db.Column(db.Integer, primary_key=True)  # 設置主鍵
    # user_ID = db.Colum(db.String(5), nullable=False, default='guest') # 儲存是哪位使用者的輸入
    user_input = db.Column(db.Text, nullable=False)  # 儲存使用者的輸入
    llm_output = db.Column(db.Text, nullable=False)  # 儲存模型的回應
    # db.Text 允許儲存更長的字串
    def __repr__(self): # 為開發者提供訊息
        return f"<ConversationLog(user_ID={self.user_ID}, user_input={self.user_input}, llm_output={self.llm_output})>"

class Course(db.Model):
    __bind_key__ = "SAD_sql_db"
    __tablename__ = 'course'  # 確保表名正確

    id = db.Column(db.String(5), primary_key=True)
    name = db.Column(db.String(20), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    time = db.Column(db.String(11), nullable=False)
    week = db.Column(db.String(50), nullable=False) 
    coachName = db.Column(db.String(20), nullable=False)

# class User(db.Model):
#     __bind_key__ = "SAD_sql_db"
#     mId = db.Column(db.String(5), primary_key=True)
#     name = db.Column(db.String(20), nullable=False)
#     phone = db.Column(db.String(10), nullable=False)
#     age = db.Column(db.INTEGER, nullable=False)
#     email = db.Column(db.String(50), nullable=False)
#     password = db.Column(db.String(20), nullable=False)
#     role = db.Column(db.String(20), nullable=False)
#     # __table_args__ 是用來設置與表格相關的高階功能的地方。其主要功能包括：
#     # 定義表級約束（如唯一性約束）。
#     # 設置索引。
#     # 指定資料庫的表格參數。
#     __table_args__ = (
#         db.UniqueConstraint('email', name='unique_email'),  # 單欄位唯一性約束
#         # db.UniqueConstraint('email', 'phone', name='unique_email_phone') # 組合必須唯一
#         # db.Index('idx_name', 'name'),  # 為 username 設置索引 (, unique=True 設置唯一索引)
#     )

# class Orders(db.Model):
#     oId = db.Column(db.String(5), primary_key=True)
#     mId = db.Column(db.String(5), db.ForeignKey('user.mId'), nullable=False)
#     cId = db.Column(db.String(5), db.ForeignKey('course.id'), nullable=False)
#     order_date = db.Column(db.Date, default=date) # 只取日期部分
#     selected_date = db.Column(db.Date, nullable=False)

#     __table_args__ = (
#         # ForeignKeyComstraint 用於設置複合外鍵或更複雜的約束
#         db.ForeignKeyConstraint(
#             ['mId', 'cId'],  # 子表的外鍵欄位
#             ['user.mid', 'course.id']  # 父表的欄位
#         ),
#     )

def get_courses_info():
    courses = Course.query.all()  # 使用 ORM 查詢所有課程
    courses_data = [{'id': course.id,
                     'name': course.name,
                     'price':course.price,
                     'time':course.time,
                     'week':course.week,
                     'coachName':course.coachName} for course in courses]

    decoded_data = json.dumps(courses_data, ensure_ascii=False)  # 确保非 ASCII 字符保持原样
    return decoded_data   # return json.dumps(courses_data)

# def get_order_info():
#     orders = Orders.query.all()
#     order_data = [{
#         "oId":order.oId,
#         "mId":order.mId,
#         "cId":order.cId,
#         "order_date":order.order_date,
#         "selected_date":order.selected_date
#     }for order in orders]
#     decoded_data = json.dumps(order_data, ensure_ascii=False)  # 确保非 ASCII 字符保持原样
#     return decoded_data

# origin_order = get_order_info()
# # 全局變量來保存對話上下文
# for local llm training format
conversation_history = []
# for conversation memory
Customer_Service_Rule = [
    f"You are a professional gym customer service, not llm, target to answering customers questions",
    f"Eliminate generated hallucinations",
    f"Natural language processing",
    f"Responding to customers using the correct language is respectful"
    f"Zh-TW is the first preferred language for replying",
    f"Use markdown to make answers more readable",
    f"The course calendar is fixed, you can read and reply informtion"
]
conver_list = [
    f'''{Customer_Service_Rule}''',
    f"Today's is {formatted_date}",
]
# 使用模型生成回應
def generate_response(user_input):

    try:
        # 把用戶輸入加入對話上下文
        conver_list.append(f"{user_input}")
        # 把過往對話作為上下文傳給模型
        context = "".join(conver_list)
        # 使用模型生成內容
        response = model.generate_content(context, stream=False)
        
        # 流式資料
        # response = model.generate_content(context, stream=True)
        # for part in response:
        # 將每個部分包裝為 JSON 格式
            # yield json.dumps({"response": part}) + "\n"  # 用 \n 分隔json
        
        # 取得模型的回應文本
        bot_response = (
            response.text if hasattr(response, "text") else "抱歉，我無法理解你的問題。"
        )
        # 把機器人的回應加入對話上下文
        conver_list.append(f"{bot_response}")

        # json格式
        entry = {"input": f"{user_input}", "output": f"{bot_response}"}
        conversation_history.append(entry)
        new_log = ConversationLog(user_input=entry["input"], llm_output=entry["output"])
        db.session.add(new_log)
        db.session.commit()
        return bot_response
    except Exception as e:
        return f"發生錯誤：{str(e)}"


# 設定一個路由，處理 POST 請求以獲取聊天回應
@chat_bp.route("/", methods=["GET"])
def chat():
    global flag,cached_courses
    #golbal origin_order
    cached_courses = get_courses_info()
    # cached_order = get_order_info()
    if flag:
        conver_list.append(f'''The course calendar \n{cached_courses}''')
        flag = False

    # origin_course!=cached_courses 比繳所有元素順序和內容
    # if set(map(frozenset, origin_course)) != set(map(frozenset, cached_courses)):
    #     conver_list.remove(f'''The course calendar \n{origin_course}''')
    #     conver_list.append(f'''The course calendar \n{cached_courses}''')
    #     origin_course = cached_courses

    # if set(map(frozenset, origin_order)) != set(map(frozenset, cached_order)):
    #     conver_list.remove(f'''The order history \n{origin_order}''')
    #     conver_list.append(f'''The order history \n{cached_order}''')
    #     origin_order = cached_order
    return render_template("chat.html")


@chat_bp.route("/", methods=["POST"])
def chat_post():
    try:
        # 獲取用戶的消息
        user_input = request.json.get("message")
        
        if not user_input:
            return jsonify({"response": "請發送消息給我。"}), 400  # 沒有消息時返回錯誤

        # 根據用戶輸入生成回應
        # print(cached_courses) # <Response 3770 bytes [200 OK]>
        bot_response = generate_response(user_input)
        return jsonify({"response": bot_response})  # 回應 JSON 格式
            # return Response(generate_response(user_input), content_type='application/json;charset=utf-8')
            # 回應流
    except Exception as e:
        return jsonify({"response": f"發生錯誤：{str(e)}"}), 500  # 處理錯誤並返回
    finally:
        print("DONE")
        print(conver_list)
        # print(conversation_history)
