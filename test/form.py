from flask import Blueprint, redirect, render_template, request, url_for

# 创建 Blueprint 对象
form_bp = Blueprint('form', __name__) # , template_folder='templates'

# the blueprint in form.py @form_bp.route('/') will effiet url to be => http://localhost:5000/form/（即 /form/）。
# @form_bp.route('/register') URL will be => http://localhost:5000/form/register。
@form_bp.route('/', methods=['GET'])
def formPage():
    return render_template('form.html')

@form_bp.route('/', methods=['GET','POST'])
def submit():
    if request.method == 'POST':
        '''# 获取表单数据
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        '''
        user = request.form['username']
        print("post : user => ", user)
        return redirect(url_for('form.success', name=user, action="post"))
    else:
        user = request.args.get('username')
        print("get : user => ", user)
        return redirect(url_for('form.success', name=user, action="get"))
        # 这里可以添加逻辑来处理用户数据，如保存到数据库等
        # return f'Username: {username}, Email: {email}'  # 这里暂时只是显示数据
    # return render_template('form.html')

@form_bp.route('/success/<action>/<name>')
def success(action, name):
    return '{} : Welcome {} ~ !!!'.format(action, name)