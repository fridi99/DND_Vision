from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn
import threading
import os

from app.Appdata import Appdata as state
from Effects.effects import aoe_man
if __name__ != "__main__":
    from Tracking.Tracking import tracker


app = FastAPI()

#_______________________________________________________________________________________________
"""
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path
static_dir = Path(__file__).parent.parent / "static"
print("[DEBUG] static_dir =", static_dir)

app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/effects")
def effects_demo():
    return FileResponse(static_dir / "effects_demo.html")
"""
#_______________________________________________________________________________________________

class Effect(BaseModel):
    type: str


@app.post("/effect")
def add_effect(effect: Effect):
    """
    effect keys: s: sphere, c: cone, r: cube, l: line, p: pathing
    :param effect:
    :return:
    """
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

@app.post("/move_effect")
def move():
    aoe_man.type = "m"
    aoe_man.active = True

@app.post("/escape")
def escape():
    if aoe_man.active:
        aoe_man.floating = False
        aoe_man.active = False
    else:
        aoe_man.quit = True



@app.post("/nextmap")
def nextmap(effect: Effect):
    if __name__ != "__main__":
        if (len(os.listdir("maps")) != 1):
            if (len(os.listdir("maps")) <= tracker.map_index + 1):
                tracker.map_index = 0
            else:
                tracker.map_index += 1
            tracker.open_map()
    return {"status": "ok"}


def run_server(host_ip):
    uvicorn.run(app, host=host_ip, port=8000)

def start_server():
    server_thread = threading.Thread(target=run_server, args=("127.0.0.1", ))
    server_thread.daemon = True
    server_thread.start()

if __name__ == "__main__":
    os.chdir("..")
    run_server("0.0.0.0")