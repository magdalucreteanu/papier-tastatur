# papier-tastatur

## Projektkonzept
https://docs.google.com/document/d/1S-t-nOo0IA7ApgKbyGDlr8_PjbnLUInCJjxqr1Cm6nQ/edit#heading=h.pkiixjec93n1

## Miro Board
https://miro.com/app/board/uXjVOahhAI0=/

## Setup
pip install opencv-python  
pip install websockets  
pip install websocket-client   
pip install websocket-server  

### WebSocket Server
Der Websocket Server ermöglicht die Kommunikation über WebSockets zwischen Python und HTML Client.  
Der Server läuft auf 127.0.0.1 (localhost) und Port 9001.  
Server starten:
- cd websocket
- python server.py

### Klaviertastatur im Browser
Der Code (HTML, CSS, JS, WebAudio) befindet sich im Ordner "browser".  
HTML Client starten:
- cd browser
- python -m http.server 9999 - wir benötigen einen WebServer um Zugriff auf lokalen Dateien (in unserem Fall Klaviernoten) zu haben. Ohne den WebServer erlaubt uns der Browser wegen CORS (Cross-Origin) Fehler den Zugriff auf Dateien nicht.
- öffne die localhost:9999 Datei in einem Browser

### Papier Tastatur
Der Code (python, opencv) befindet sich im Ordner "papier".  
Python Client starten:
- cd papier
- python video.py

### Projekt starten
1. Starte WebSocket Server  
2. Starte HTML Client (Klaviertastatur in Browser)  
3. Starte Python Client (Papier Tastatur)

## Links

### Bibliotheken
https://github.com/Pithikos/python-websocket-server

### Klavier Noten (mp3 Dateien)
https://archive.org/details/24-piano-keys/
Die erste Note hier ist F und unsere Klaviertastatur beginnt mir C. D.H.: die erste C Note ist die achte Datei, also key08.mp3.

### HowTos
https://linuxhint.com/how-to-implement-a-websocket-in-python/  
https://betterprogramming.pub/how-to-create-a-websocket-in-python-b68d65dbd549  
https://websocket-client.readthedocs.io/en/latest/examples.html  
https://www.pyimagesearch.com/2016/04/11/finding-extreme-points-in-contours-with-opencv/  

#### Simple-Server mit python auf Port 9999 starten:
python -m http.server 9999  

## Offene Aufgaben
- Abgabe Projektdokumentation und Konzept

## Erledigte Aufgaben
- Durcharbeitung der Vorlesungsinhalte, Bearbeitung der Video und Audio Aufgaben, Vorstellung der bearbeiteten Aufgaben
- Projektideen sammeln und bewerten/vergleichen
- Projektkonzept schreiben
- Projektkonzept vorstellen
- Github Projekt erstellen
- wie können wir Piano abspielen (derzeit ist Synth mit dem Oscillator simuliert)
- Kommunikation mit WebSockets erproben (inklusive Server starten). Eventuell die Kommunikation über eine MIDI Schnittstelle ermöglichen.
- Klaviertastatur graphisch mit HTML erstellen
- Präsentation Inkrement
- Weitere Knöpfe (für Lautstärke, Effekte usw.) in HTML erstellen
- Identifizieren welche Taste wurde gedrückt auf die Papier Tastatur mittels OpenCV
- Informationen über die gedrückten Knöpfe mit WebSockets/MIDI an HTML übergeben 
- Papier- und HTML-Knöpfe sind beide funktional
- Weitere Tests eventuell Bugfixes
- Präsentation Projektergebnis

Projektkonzept  
- Sequence Diagram  
- Usecase Diagram  
- Quellen  
- Bilder referenzieren und verzeichnen

## Code und Algorithmen

### Allgemeine Hinweise
Quelle für Frequenzen/Halbtöne: https://de.wikipedia.org/wiki/Frequenzen_der_gleichstufigen_Stimmung

### index.html
Das script.js wird im Body (und nicht im Header) gesetzt.  
Begründung: wir benötigen Zugriff auf HTML document um die Tasten zu erstellen und das Dcoument ist erst im Body verfügbar.

### Tastatur in Browser
Es gibt mehrere Möglichkeiten um die Tastatur in Browser anzuzeigen:  

1. wir zeichnen die Klavier Tasten mit HTML5 Canvas.  
Alles wird manuell gezeichnet, d.H. wir berechnen welche und wo geometrische Figuren gezeichnet werden sollen. Wir müssen die Mausposition manuell finden um zu identifizieren welche Taste gedrückt wurde.  
Anschliessend müssen wir die gedrückten Tasten neu zeichen, um zu simulieren dass sie gedrückt wurden. Das ganze ist machbar, aber dafür ist die Logik etwas komplexer und weniger geeignet für HTML Seiten.  

2. wir nutzen HTML Elemente(z.B. Buttons) für die Klavier Tasten.  
Wir generieren dafür die Buttons (Tasten) dynamisch. Der Vorteil ist: wir können die Klaviertastatur jederzeit erweitern, ohne dass wir die Logik des Programms ändern.  
Wir zeigen dass eine Taste gedrückte oder nicht gedrückte ist indem wir auf HTML Elemente zugreifen und deren CSS Klassen zu ändern (entfernen oder hinzufügen).  
Die gedrückte Taste bekommt eine neue CSS Klasse 'pressed'. Diese Klasse ändert das visuelle Aussehen des gedrückten Elements und zeichnet es mit einer grauen Farbe.  
Die nicht gedrückten Tasten haben die Standard Farben, weiß für volle Töne und schwarz für Halbtöne.  

Wir haben uns für die zweite Variante entscheiden, d.H. jede Klaviertaste wird ein HTML Button der mittels CSS gestyled wird.
