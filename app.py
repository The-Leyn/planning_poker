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
    session_id = str(uuid.uuid4())[:16]  # ID unique (8 caractères)
    return redirect(url_for('session', session_id=session_id))

@app.route("/register", methods=["GET","POST"])
def promo():
   return render_template("register.html")

@app.route('/session/<session_id>')
def session(session_id):
    return render_template('session.html', session_id=session_id)

@socketio.on('join')
def handle_join(data):
    session_id = data['session_id']
    username = data['username']

    join_room(session_id)

    if session_id not in rooms:
        rooms[session_id] = {"admin": request.sid, "users": {}}

    rooms[session_id]['users'][request.sid] = {"username": username}

    send(f"{username} a rejoint la session !", room=session_id)

    # Envoie la liste des utilisateurs mis à jour
    emit("update_users", {"users": [user["username"] for user in rooms[session_id]['users'].values()]}, room=session_id)

    # Envoie l'ID de l'admin à tous les utilisateurs
    emit("set_admin", {"admin_id": rooms[session_id]["admin"]}, room=session_id)

    print(rooms[session_id])

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


@socketio.on('create_vote')
def handle_create_vote(data):
    """Seul l'administrateur peut créer un vote."""
    session_id = data['session_id']
    user_id = request.sid  # L'ID du socket de l'utilisateur

    # Vérifie si la session existe et si l'utilisateur est l'admin
    if session_id in rooms and rooms[session_id]["admin"] == user_id:
        vote_id = str(uuid.uuid4())[:4]  # Générer un ID unique court pour le vote
        vote_title = data['title']

        if "votes" not in rooms[session_id]:
            rooms[session_id]["votes"] = {}

        rooms[session_id]["votes"][vote_id] = {
            "title": vote_title,
            "votes": {},  # Les votes des utilisateurs
            "result": {}
        }

        # Notifie tous les utilisateurs de la création du vote
        emit("new_vote", {"vote_id": vote_id, "title": vote_title}, room=session_id)

    else:
        emit("error", {"message": "Seul l'administrateur peut créer un vote."}, to=user_id)

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=80)
