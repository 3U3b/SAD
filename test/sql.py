from flask import Blueprint, redirect, render_template, request, jsonify, url_for
from flask_sqlalchemy import SQLAlchemy
from test import db

sql_bp = Blueprint('sql', __name__)

# 定義 User 模型
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    age = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f"<User {self.name}>"

# 定義新增用戶和獲取用戶的路由
@sql_bp.route('/', methods=['GET','POST'])
def add_user():
    if request.method == 'POST':
        username = request.form['username']
        # password = request.form['password']
        # email = request.form['email'] 
        # 沒有使用到的變數不可留著(不知為何會造成無法submit)
        age = request.form['age']
        
        new_user = User(name=username, age=age)
        db.session.add(new_user)
        db.session.commit()
        # return redirect(url_for('sql.success', name=username))
        return jsonify({'message': 'User added successfully'}), 201 # .then((response) => response.json()) 接收json格式
    return render_template('user.html')

@sql_bp.route('/users', methods=['GET']) #sql.html function loadUsers() fetch("/sql/users") 使用此頁面
def get_users():
    users = User.query.all()  # 使用 ORM 查詢所有用戶
    return jsonify([{'id': user.id, 'name': user.name, 'age': user.age} for user in users])