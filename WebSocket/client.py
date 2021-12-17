import websocket

# short-lived client
ws = websocket.WebSocket()
ws.connect("ws://localhost:9001/")
ws.send("Hello, Server, I am short-lived")
print(ws.recv())
ws.close()
