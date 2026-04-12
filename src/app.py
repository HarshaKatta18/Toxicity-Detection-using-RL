import os
from flask import Flask, send_from_directory, request
from flask_socketio import SocketIO, emit
from server_state import ServerState
from chat.toxicity_model import ToxicityModel
from chat.agent import EpsGreedyAgent, ACTIONS

app = Flask(__name__, static_folder="static")
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="threading")


STATE = ServerState()
TOX_MODEL = ToxicityModel()
AGENT = EpsGreedyAgent(epsilon=0.05, lr=0.05)

@app.route("/")
def index():
    return send_from_directory("static", "index.html")

@app.route("/<path:path>")
def static_proxy(path):
    return send_from_directory("static", path)

@socketio.on("connect")
def on_connect():
    emit("state:init", _serialize_state(), to=request.sid)

def _serialize_state():
    g = STATE.game
    return {
        "players": [
            {
                "pid": p.pid,
                "name": p.name,
                "position": p.position,
                "active": p.active,
                "warnings": p.warnings,
            } for p in g.players
        ],
        "turn": g.turn_idx,
        "die_last": g.die_last,
        "winner_pid": g.winner_pid,
    }

@socketio.on("game:roll")
def on_roll():
    g = STATE.game
    cur = g.current_player()
    if not cur.active:
        g.next_turn()
        emit("state:update", _serialize_state(), broadcast=True)
        return
    die = g.roll_and_move()
    emit("state:update", _serialize_state(), broadcast=True)

@socketio.on("game:restart")
def on_restart(data):
    names = data.get("names", ["P1", "P2", "P3", "P4"])
    STATE.reset(names)
    emit("state:update", _serialize_state(), broadcast=True)

@socketio.on("chat:message")
def on_chat(msg):
    pid = int(msg.get("pid", 0))
    text = (msg.get("text") or "").strip()
    if text == "":
        return

    player = STATE.game.players[pid]
    if not player.active:
        return

    pt = TOX_MODEL.score_proba(text)
    warnings = player.warnings
    action_idx = AGENT.act(pt, warnings)
    action = ACTIONS[action_idx]

    pseudo_label = 1 if pt >= 0.5 else 0
    AGENT.update(pt, warnings, action_idx, pseudo_label)
    AGENT.save()

    if action == "allow":
        emit("chat:broadcast", {"pid": pid, "text": text, "flag": "ok", "p": pt}, broadcast=True)
    elif action == "warn":
        player.warnings += 1
        if player.warnings >= 3:
            action = "kick"
            player.active = False
            emit("chat:broadcast", {"pid": pid, "text": text, "flag": "kick", "p": pt}, broadcast=True)
        else:
            emit("chat:broadcast", {"pid": pid, "text": text, "flag": "warn", "p": pt}, broadcast=True)
    else:
        player.active = False
        emit("chat:broadcast", {"pid": pid, "text": text, "flag": "kick", "p": pt}, broadcast=True)

    emit("state:update", _serialize_state(), broadcast=True)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5000"))
    socketio.run(app, host="0.0.0.0", port=port, debug=True)

