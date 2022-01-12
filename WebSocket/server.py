import logging
from websocket_server import WebsocketServer

# diese Funktion wird aufgerufen wann ein Client sich mit dem Server verbindet
def new_client(client, server):
    print("Neuer Client verbunden, id %d" % client['id'])

# diese Funktion wird aufgerufen wann ein Client die Verbindung mit dem Server trennt
def client_left(client, server):
    print("Client(%d) hat den Server verlassen" % client['id'])

# diese Funktion wird aufgerufen wann ein Client ein Message sendet
def message_received(client, server, message):
    print("Client(%d) Message: %s" % (client['id'], message))
    # der Server sendet diese Messages an allen verbundenen Clients
    server.send_message_to_all(message)

# Server wird mit Addresse 127.0.0.1 (localhost) und auf Port 9001 initialisiert
server = WebsocketServer(host='127.0.0.1', port=9001, loglevel=logging.INFO)
# Server reagiert auf neue Clients
server.set_fn_new_client(new_client)
# Server reagiert wann Clients die Verbindung trennen
server.set_fn_client_left(client_left)
# Server reagiert wann ein Client Message gesendet wurde
server.set_fn_message_received(message_received)
# Der Server soll für eine unbestimmte Zeit (für immer) laufen
server.run_forever()
