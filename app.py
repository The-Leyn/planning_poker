from flask import Flask, render_template, redirect, url_for, request
from flask_socketio import SocketIO, join_room, leave_room, send
import uuid  

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")  # Permet les connexions WebSocket

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/create-session')
def create_session():
    session_id = str(uuid.uuid4())[:8]  # ID unique (8 caractères)
    return redirect(url_for('session', session_id=session_id))

@app.route('/session/<session_id>')
def session(session_id):
    return render_template('session.html', session_id=session_id)

@socketio.on('join')
def handle_join(data):
    """Un utilisateur rejoint une room spécifique."""
    session_id = data['session_id']
    username = data['username']

    join_room(session_id)
    send(f"{username} a rejoint la session !", room=session_id)

@socketio.on('leave')
def handle_leave(data):
    """Un utilisateur quitte la room."""
    session_id = data['session_id']
    username = data['username']

    leave_room(session_id)
    send(f"{username} a quitté la session.", room=session_id)

@socketio.on('message')
def handle_message(data):
    """Un utilisateur envoie un message uniquement dans la room."""
    session_id = data['session_id']
    username = data['username']
    message = data['message']
    
    send(f"{username} : {message}", room=session_id)  # Envoie le message uniquement à la room

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=80)
