from dotenv import load_dotenv
from flask import Blueprint, request, jsonify, render_template
import google.generativeai as genai
import os
chat_bp = Blueprint('chat', __name__)

# 加載測試環境配置
load_dotenv(dotenv_path='.env.testing')
# 抓取API
API_key = os.getenv("API_KEY")
genai.configure(api_key=API_key)
# 初始化 Gemini 模型
model = genai.GenerativeModel("gemini-1.5-flash")

# 全局變量來保存對話上下文
conversation_history = []

# 使用模型生成回應
def generate_response(user_input):
    try:
        # 把用戶輸入加入對話上下文
        conversation_history.append(f"你: {user_input}")
        
        # 把過往對話作為上下文傳給模型
        context = "\n".join(conversation_history)
        
        # 使用模型生成內容
        response = model.generate_content(context, stream=False)
        
        # 取得模型的回應文本
        bot_response = response.text if hasattr(response, 'text') else '抱歉，我無法理解你的問題。'
        
        # 把機器人的回應加入對話上下文
        conversation_history.append(f"{bot_response}")
        
        return bot_response
    except Exception as e:
        return f"發生錯誤：{str(e)}"

# 設定一個路由，處理 POST 請求以獲取聊天回應
@chat_bp.route('/', methods=['GET'])
def chat():
    return render_template('chat.html')

@chat_bp.route('/', methods=['POST'])
def chat_post():
    try:
        # 獲取用戶的消息
        user_input = request.json.get("message")
        
        if user_input:
            # 根據用戶輸入生成回應
            bot_response = generate_response(user_input)
            return jsonify({"response": bot_response})  # 回應 JSON 格式
        else:
            return jsonify({"response": "請發送消息給我。"}), 400  # 沒有消息時返回錯誤
    except Exception as e:
        return jsonify({"response": f"發生錯誤：{str(e)}"}), 500  # 處理錯誤並返回