from flask import Flask, render_template, redirect, url_for, request
from flask_socketio import SocketIO, join_room, leave_room, send, emit, disconnect
import uuid  

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# Dictionnaire pour suivre les utilisateurs dans chaque room
rooms = {}

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

    # Associer l'ID du socket au username
    if session_id not in rooms:
        rooms[session_id] = {}
    rooms[session_id][request.sid] = username  

    send(f"{username} a rejoint la session !", room=session_id)

    # Envoie la liste des utilisateurs mis à jour
    emit("update_users", {"users": list(rooms[session_id].values())}, room=session_id)

@socketio.on('leave')
def handle_leave(data):
    """Un utilisateur quitte la room manuellement."""
    session_id = data['session_id']
    username = data['username']

    leave_room(session_id)

    # Supprime l'utilisateur de la liste de la room
    if session_id in rooms and request.sid in rooms[session_id]:
        del rooms[session_id][request.sid]

        if not rooms[session_id]:  # Si plus personne dans la room, on la supprime
            del rooms[session_id]

    send(f"{username} a quitté la session.", room=session_id)

    # Met à jour la liste des utilisateurs
    emit("update_users", {"users": list(rooms.get(session_id, {}).values())}, room=session_id)

@socketio.on('disconnect')
def handle_disconnect():
    """Gestion automatique de la déconnexion quand un onglet est fermé."""
    for session_id, users in rooms.items():
        if request.sid in users:
            username = users[request.sid]
            del users[request.sid]

            send(f"{username} s'est déconnecté.", room=session_id)
            emit("update_users", {"users": list(users.values())}, room=session_id)

            if not users:  # Supprime la room si elle est vide
                del rooms[session_id]
            break

@socketio.on('message')
def handle_message(data):
    """Un utilisateur envoie un message uniquement dans la room."""
    session_id = data['session_id']
    username = data['username']
    message = data['message']
    
    send(f"{username} : {message}", room=session_id)  # Envoie le message uniquement à la room

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=80)
