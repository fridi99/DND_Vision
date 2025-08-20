from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn

app = FastAPI()


class Effect(BaseModel):
    type: str


@app.post("/effect")
def add_effect(effect: Effect):
    print(f"successfully received Post for effect of type: {effect.type}")
    return {"status": "ok", "effect": effect}

@app.post("/nextmap")
def test(effect: Effect):
    print("received")
    return {"status": "ok"}

uvicorn.run(app, host="127.0.0.1", port=8000)