from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn
import threading
import os
from Logic.Logic import open_map, calibration
from app.Appdata import Appdata as state
from Effects.effects import aoe_man

app = FastAPI()


class Effect(BaseModel):
    type: str


@app.post("/effect")
def add_effect(effect: Effect):
    allowlist = ["s", "c", "r", "l", "p"]  # will reject other types
    if effect.type not in allowlist:
        return {"status": "unrecognized type", "effect": effect, }
    print(f"successfully received post with type: {effect.type}")
    aoe_man.activate_type(effect.type)
    return {"status": "ok", "effect": effect}

@app.post("/deletelast")
def delete_last():
    res = aoe_man.delete_last()
    if res:
        return {"status": "effect deleted"}
    else:
        return {"status": "no effects to delete"}

@app.post("/deletenearest")
def delete_nearest():
    aoe_man.type = "d"
    aoe_man.floating = True
    aoe_man.active = True

@app.post("/escape")
def escape():
    if aoe_man.active:
        aoe_man.floating = False
        aoe_man.active = False
    else:
        aoe_man.quit = True


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

if __name__ == "__main__":
    run_server()