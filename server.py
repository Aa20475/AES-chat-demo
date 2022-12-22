from flask import Flask, render_template
from flask_socketio import SocketIO
from AES import encrypt, decrypt

app = Flask(__name__)

app.config["TEMPLATES_AUTO_RELOAD"] = True
socketio = SocketIO(app)

@app.route("/")
def helloWorld():
    return render_template("sessions.html")

@socketio.on("event")
def handleCustomEvent(json,methods=["GET","POST"]):
    response = {
        'status': "OK"
    }

    if json['user']=="":
        print(json['data'])
    elif json['action']=="encrypt":
        if json['user']==1:
            response['data'] = encrypt(json['data'])
            response['user'] = 2
        elif json['user']==2:
            response['data'] = encrypt(json['data'])
            response['user'] = 1
        response['action'] = json['action']
    elif json['action']=='decrypt':
        response['data'] = decrypt(json['data'])
        response['user'] = json['user']
        response['action'] = json['action']
    socketio.emit("response",response)

if __name__ == '__main__':
    socketio.run(app)