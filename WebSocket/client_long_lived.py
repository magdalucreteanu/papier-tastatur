import websocket

# long-lived client, FUNKTIONIERT NICHT RICHTIG

def on_message(wsapp, message):
    print(message)

wsapp = websocket.WebSocketApp("ws://localhost:9001/", on_message=on_message)
wsapp.run_forever()

wsapp.send("Hello, Server, I am long-lived")
print(wsapp.recv())
