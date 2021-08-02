from broadcaster import Broadcast
from fastapi import FastAPI, WebSocket
from starlette.concurrency import run_until_first_complete

broadcast = Broadcast("redis://localhost:6379")

app = FastAPI()


@app.on_event("startup")
async def startup_event():
    await broadcast.connect()


@app.on_event("shutdown")
async def shutdown_event():
    await broadcast.disconnect()


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    await run_until_first_complete(
        (chatroom_ws_receiver, {"websocket": websocket}),
        (chatroom_ws_sender, {"websocket": websocket}),
    )


async def chatroom_ws_receiver(websocket):
    async for message in websocket.iter_text():
        await broadcast.publish(channel="chatroom", message=message)


async def chatroom_ws_sender(websocket):
    async with broadcast.subscribe(channel="chatroom") as subscriber:
        async for event in subscriber:
            await websocket.send_text(event.message)
