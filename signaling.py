from aiohttp import web
import socketio

ROOM = 'room'
people = {}

sio = socketio.AsyncServer(cors_alllowed_origins="*")
app = web.Application()
sio.attach(app)

async def index(request):
    with open('index.html') as f:
        return web.Response(text=f.read(), content_type="text/html")

@sio.event
async def connect(sid, environ):
    print("Connected", sid, environ)
    await sio.emit("ready", room=ROOM, skip_sid=sid)
    sio.enter_room(sid, ROOM)

@sio.event
async def disconnect(sid):
    sio.leave_room(sid, ROOM)
    print('Disconnected', sid)
    try:
        people.pop(sid)
    except KeyError:
        pass

@sio.event
async def message(sid, msg):
    print(f"Message from {sid}: {msg}")
    data = {"status":"msg", "sender":people[sid], "message": msg}
    await sio.emit('data', data, room=ROOM)

@sio.event
async def data(sid, data):
    print(f"{sid} has sent {data}")
    if data["status"] == "login":
        people[sid] = data["name"]
        sio.emit("data", data, room=ROOM, skip_sid=sid)
    elif data["status"] == "length":
        sio.emit("data", {"status": "length", "names": list(people.values())}, to=sid)



app.router.add_get('/', index)

if __name__ == '__main__':
    web.run_app(app, host="0.0.0.0", port=9999)