from flask import Flask, render_template, request, redirect, url_for
from flask_socketio import SocketIO, join_room, leave_room
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
socketio = SocketIO(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# User class for Flask-Login
class User(UserMixin):
    def __init__(self, id, username):
        self.id = id
        self.username = username

@login_manager.user_loader
def load_user(user_id):
    # For simplicity, you can replace this with actual user loading logic (e.g., from a database)
    return User(user_id, f'User {user_id}')

@app.route('/')
@login_required
def index():
    return render_template('index.html', username=current_user.username)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_id = int(request.form['user_id'])
        user = User(user_id, f'User {user_id}')
        login_user(user)
        return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@socketio.on('message')
@login_required
def handle_message(msg):
    print('Message:', msg)
    socketio.emit('message', {'username': current_user.username, 'msg': msg})

@socketio.on('join')
@login_required
def handle_join(data):
    room = data['room']
    join_room(room)
    socketio.emit('message', {'username': 'System', 'msg': f'{current_user.username} has joined the room'}, room=room)

@socketio.on('leave')
@login_required
def handle_leave(data):
    room = data['room']
    leave_room(room)
    socketio.emit('message', {'username': 'System', 'msg': f'{current_user.username} has left the room'}, room=room)

if __name__ == '__main__':
    socketio.run(app, debug=True)
