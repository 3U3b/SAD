from flask import Blueprint, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy

sql_bp = Blueprint('sql', __name__)
db = SQLAlchemy()

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
        name = request.form['name']
        age = request.form['age']
        
        new_user = User(name=name, age=age)
        db.session.add(new_user)
        db.session.commit()
        
        return jsonify({'message': 'User added successfully'}), 201

    return render_template('user.html')

@sql_bp.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()  # 使用 ORM 查詢所有用戶
    return jsonify([{'id': user.id, 'name': user.name, 'age': user.age} for user in users])