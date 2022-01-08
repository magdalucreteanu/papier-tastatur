import websocket
import cv2
import json
import time
import numpy as np

# ausgewählter Pixel für den Tastaturrand
keyboard_border_color = cv2.imread('../media/Tastaturrand_Farbe.jpg',cv2.IMREAD_COLOR )
keyboard_border_color_HSV = cv2.cvtColor(keyboard_border_color, cv2.COLOR_BGR2HSV)
h_keyboard_border_color1 = keyboard_border_color_HSV[0][0][0]
h_keyboard_border_color = int(h_keyboard_border_color1)
s_keyboard_border_color1 = keyboard_border_color_HSV[0][0][1]
s_keyboard_border_color = int(s_keyboard_border_color1)
v_keyboard_border_color1 = keyboard_border_color_HSV[0][0][2]
v_keyboard_border_color = int(v_keyboard_border_color1)

# Callback Funktion für Slider - tut nichts
def do_nothing():
    return

# ------------------------- WEB SOCKET  ---------------------------------------------------

# WebSocket Funktion um ein Message zu senden
def sendMessage(message):
    ws = websocket.WebSocket()
    ws.connect("ws://127.0.0.1:9001/")
    ws.send(json.dumps(message))
    ws.close()

# Sende ein Volume Minus Kommando über WobSocket
def volumeMinus():
    data = {
        "timestamp": time.time(),
        "name": "volume_minus"
    }
    sendMessage(data)

# Sende ein Volume Minus Kommando über WobSocket
def volumePlus():
    data = {
        "timestamp": time.time(),
        "name": "volume_plus"
    }
    sendMessage(data)

# Sende Piano Kommando über WebSocket
def piano():
    data = {
        "timestamp": time.time(),
        "name": "piano"
    }
    sendMessage(data)

# Sende Synth Kommando über WebSocket
def synth():
    data = {
        "timestamp": time.time(),
        "name": "synth"
    }
    sendMessage(data)

# Sende Attack Kommando über WebSocket
def attack():
    data = {
        "timestamp": time.time(),
        "name": "attack"
        # TODO - Attack Kontrolparameter hier
    }
    sendMessage(data)

# Sende Release Kommando über WebSocket
def release():
    data = {
        "timestamp": time.time(),
        "name": "release"
        # TODO - Release Kontrolparameter hier
    }
    sendMessage(data)


# ------------------------- VIDEO  --------------------------------------------------------

# Named Window Tastatur erstellen
cv2.namedWindow("Tastatur")
# Tracker in Tastatur Window erstellen
cv2.createTrackbar("Threshold", "Tastatur", 80, 100, do_nothing)

#Video aus Datei öffnen
# cap = cv2.VideoCapture('../media/Papier_Tastatur_Video_MP4.mp4')
cap = cv2.VideoCapture('../media/Papiertastatur_OhneFinger.mp4')

# Live Video
#cap=cv2.VideoCapture(0)

while cap.isOpened():
    ret, frame = cap.read()

    # Skaling (für mp4-Video)
    frame = cv2.resize(frame, (960, 540)) 

    # Original Video anzeigen
    cv2.imshow('Original', frame)

    # Umwandlung in HSV Farbraum
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Threshold Wert aus Tracker lesen
    threshold = cv2.getTrackbarPos('Threshold', 'Tastatur')

    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    lower = np.array([h_keyboard_border_color - threshold, s_keyboard_border_color - threshold, v_keyboard_border_color - threshold])
    upper = np.array([h_keyboard_border_color + threshold, s_keyboard_border_color + threshold, v_keyboard_border_color + threshold])

    # Threshold HSV image um nur Piano Randfarben zu bekommen
    mask = cv2.inRange(hsv, lower, upper)

    # Region Finding Algorithmus: liefert Array contours, jedes Objekt repräsentiert eine zusammenhängende Region
    contours, hierarchy = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    # Berechnet Fläche einer Region. Im Beispiel werden die Flächen aller Regionen ausgegeben
    biggestRegion = 0
    biggestRegionIndex = 0
    for index in range(len(contours)):
        area = cv2.contourArea(contours[index])
        # Schwärzung aller Regionen
        cv2.drawContours(mask, contours, index, (0,0,0), cv2.FILLED)
        # Bestimmung des Index der Region mit größter Fläche
        if area > biggestRegion:
            biggestRegion = area
            biggestRegionIndex = index
            cnt = contours[index]
    # Zeichnet größte Region weiß
    cv2.drawContours(mask, contours, biggestRegionIndex, (255,255,255), cv2.FILLED)

    x,y,w,h = cv2.boundingRect(cnt)
    
    cv2.rectangle(frame, (x,y), (x+w, y+h), color=(0, 255, 0), thickness=2)

    # Kombiniertes Ergebnis anzeigen
    cv2.imshow('Tastatur', mask)
    cv2.imshow("Contour", frame)
 
    # Abbruch bei Tastendruck
    if cv2.waitKey(25) != -1:
        break

# cap wieder freigeben
cap.release()

# Fenster schließen
cv2.destroyAllWindows()
