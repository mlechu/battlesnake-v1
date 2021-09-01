import logging
import os

from flask import Flask
from flask import request

import server_logic

app = Flask(__name__)

@app.get("/")
def handle_info():
    print("INFO")
    return {
        "apiversion": "1",
        "author": "im-echu",
        "color": "#000000",
        "head": "default",
        "tail": "default",
    }


@app.post("/start")
def handle_start():
    data = request.get_json()
    server_logic.init_maps(data)

    print(f"{data['game']['id']} START")
    return "ok"


@app.post("/move")
def handle_move():
    data = request.get_json()
    move = server_logic.choose_move(data)

    return {"move": move}


@app.post("/end")
def end():
    data = request.get_json()

    print(f"{data['game']['id']} END")
    return "ok"


if __name__ == "__main__":
    logging.getLogger("werkzeug").setLevel(logging.ERROR)

    print("Starting Battlesnake Server...")
    port = int(os.environ.get("PORT", "8080"))
    app.run(host="0.0.0.0", port=port, debug=True)
