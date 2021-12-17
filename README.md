# papier-tastatur

## Projektkonzept
https://docs.google.com/document/d/1S-t-nOo0IA7ApgKbyGDlr8_PjbnLUInCJjxqr1Cm6nQ/edit#heading=h.pkiixjec93n1

## Setup
pip install opencv-python
pip install websockets
pip install websocket-server

### Tastatur in Browser
Der Code (HTML, CSS, JS, WebAudio) befindet sich im Ordner "browser".

### Papier Tastatur
Der Code (python, opencv) befindet sich im Ordner "papier".

## Links

### Bibliotheken
https://github.com/Pithikos/python-websocket-server

### HowTos
https://linuxhint.com/how-to-implement-a-websocket-in-python/
https://betterprogramming.pub/how-to-create-a-websocket-in-python-b68d65dbd549
https://websocket-client.readthedocs.io/en/latest/examples.html

#### Kommunikation mit WebSockets (Beispiel befindet sich im Ordner WebSocket)
cd WebSocket
Starte server: python server.py
Starte Browser Client (bekommt und sendet Daten): öffne client.html in Browser
Starte Python Client (sendet Daten): python client.py

#### Simple-Server mit python auf Port 9999 starten:
python -m http.server 9999

## Offene Aufgaben
- Kommunikation mit WebSockets erproben (inklusive Server starten). Eventuell die Kommunikation über eine MIDI Schnittstelle ermöglichen.
- Identifizieren welche Taste wurde gedrückt auf die Papier Tastatur mittels OpenCV
- Klaviertastatur graphisch mit HTML erstellen
- Informationen über die gedrückten Tasten mit WebSockets an HTML übergeben 
- Papier- und HTML-Tastaturen sind beide funktional
- Weitere Knöpfe (für Lautstärke, Effekte usw.) in HTML erstellen
- Präsentation Inkrement
- Identifizieren welcher Knopf wurde gedrückt auf die Papier Tastatur mittels OpenCV
- Informationen über die gedrückten Knöpfe mit WebSockets/MIDI an HTML übergeben 
- Papier- und HTML-Knöpfe sind beide funktional
- Weitere Tests eventuell Bugfixes
- Präsentation Projektergebnis
- Abgabe Projektdokumentation und Konzept


## Erledigte Aufgaben
- Durcharbeitung der Vorlesungsinhalte, Bearbeitung der Video und Audio Aufgaben, Vorstellung der bearbeiteten Aufgaben
- Projektideen sammeln und bewerten/vergleichen
- Projektkonzept schreiben
- Projektkonzept vorstellen
- Github Projekt erstellen
