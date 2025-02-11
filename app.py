from flask import Flask, render_template
from flask_socketio import SocketIO, emit

app = Flask(__name__)
# Créer un le serveur socketIO
socketio = SocketIO(app)

@app.route('/')
def index():
    return render_template('index.html')

# Gérer l'événement de vote
@socketio.on('vote')
def handle_vote(vote_data):
    print(f"Vote reçu : {vote_data}")
    # Diffuser le vote à tous les clients connectés
    emit('new_vote', vote_data, broadcast=True)

if __name__ == '__main__':
    socketio.run(app, debug=True)
