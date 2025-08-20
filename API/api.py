from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn
import threading
import os
from Logic.Logic import open_map
from app.Appdata import Appdata as state
from Effects.effects import aoe_man

app = FastAPI()


class Effect(BaseModel):
    type: str


@app.post("/effect")
def add_effect(effect: Effect):
    allowlist = ["s", "c", "r", "l"]  # will reject other types
    if effect.type not in allowlist:
        return {"status": "unrecognized type", "effect": effect, }
    print(f"successfully received post with type: {effect.type}")
    aoe_man.activate_type(effect.type)
    return {"status": "ok", "effect": effect}

@app.post("/nextmap")
def test(effect: Effect):
    if (len(os.listdir("maps")) != 1):
        if (len(os.listdir("maps")) <= state.map_index + 1):
            state.map_index = 0
        else:
            state.map_index += 1
        open_map(state.map_index)
    return {"status": "ok"}


def run_server():
    uvicorn.run(app, host="127.0.0.1", port=8000)

def start_server():
    server_thread = threading.Thread(target=run_server)
    server_thread.daemon = True
    server_thread.start()

run_server()