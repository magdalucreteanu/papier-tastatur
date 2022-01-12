import websocket
import cv2
import json
import time
import numpy as np

# ausgewählter Pixel für den Tastaturrand
keyboard_border_color = cv2.imread('../media/Tastaturrand_Farbe.jpg',cv2.IMREAD_COLOR )
keyboard_border_color_HSV = cv2.cvtColor(keyboard_border_color, cv2.COLOR_BGR2HSV)
h_keyboard_border_color = int(keyboard_border_color_HSV[0][0][0])
s_keyboard_border_color = int(keyboard_border_color_HSV[0][0][1])
v_keyboard_border_color = int(keyboard_border_color_HSV[0][0][2])

# ausgewählter Pixel für den Finger
finger_color = cv2.imread('../media/Finger_Farbe.jpg',cv2.IMREAD_COLOR )
finger_color_HSV = cv2.cvtColor(finger_color, cv2.COLOR_BGR2HSV)
h_finger_color = int(finger_color_HSV[0][0][0])
s_finger_color = int(finger_color_HSV[0][0][1])
v_finger_color = int(finger_color_HSV[0][0][2])
finger_radius = 30

# Koordinaten der Elemente innerhalb des originalen Bilders (mit den zwei Beispieltastaturen)
# Das Bild befindet sich in media/Papier_Tastatur_Image.jpeg
# Wir identifizieren este die Tastatur anhand des roten Randes.
# Danach finden wir die einzelnen Elemente mathematisch anhand der Koordinaten.

# Tastatur
# Outer
paper_outer_margin_upper_x = 171
paper_outer_margin_upper_y = 1239
paper_outer_margin_lower_x = 926
paper_outer_margin_lower_y = 1607
# Inner
paper_inner_margin_upper_x = 192
paper_inner_margin_upper_y = 1261
paper_inner_margin_lower_x = 904
paper_inner_margin_lower_y = 1586

# Volume Minus
paper_volume_minus_upper_x = 202
paper_volume_minus_upper_y = 1108
paper_volume_minus_w = 63
paper_volume_minus_h = 63

# Volume Plus
paper_volume_plus_upper_x = 283
paper_volume_plus_upper_y = 1108
paper_volume_plus_w = 63
paper_volume_plus_h = 63

# Piano
paper_piano_upper_x = 382
paper_piano_upper_y = 1095
paper_piano_w = 89
paper_piano_h = 89

# Synth
paper_synth_upper_x = 504
paper_synth_upper_y = 1095
paper_synth_w = 89
paper_synth_h = 89

# Attack
paper_attack_upper_x = 624
paper_attack_upper_y = 1075
paper_attack_w = 282
paper_attack_h = 35

# Release
paper_release_upper_x = 624
paper_release_upper_y = 1144
paper_release_w = 282
paper_release_h = 35

command = 'none'

# Callback Funktion für Slider - tut nichts
def do_nothing(no):
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

# Sende blackKey Kommando über WebSocket
def blackKey(index):
    data = {
        "timestamp": time.time(),
        "name": "blackKey",
        "index": index
    }
    sendMessage(data)

# Sende whiteKey Kommando über WebSocket
def whiteKey(index):
    data = {
        "timestamp": time.time(),
        "name": "whiteKey",
        "index": index
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

#--------------------------FUNKTIONEN FÜRS VIDEO-------------------------------------------
def findBiggestRegionForColor(frame, h, s, v, threshold):

    # Umwandlung in HSV Farbraum
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    lower = np.array([h - threshold, s - threshold, v - threshold])
    upper = np.array([h + threshold, s + threshold, v + threshold])

    # Threshold HSV image um nur Piano Randfarben zu bekommen
    mask = cv2.inRange(hsv, lower, upper)

    # Region Finding Algorithmus: liefert Array contours, jedes Objekt repräsentiert eine zusammenhängende Region
    contours, hierarchy = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    # Berechnet Fläche einer Region
    biggestRegion = 0
    biggestRegionIndex = 0
    cnt = np.array([[0, 0]])
    for index in range(len(contours)):
        area = cv2.contourArea(contours[index])
        # Schwärzung aller Regionen
        cv2.drawContours(mask, contours, index, (0,0,0), cv2.FILLED)
        # Bestimmung des Index der Region mit größter Fläche
        if area > biggestRegion:
            biggestRegion = area
            biggestRegionIndex = index
            cnt = contours[index]
    return mask, contours, biggestRegionIndex, cnt

def getPixelSize(w):
    return 1.0 * w / (paper_outer_margin_lower_y - paper_outer_margin_upper_y)

def getInnerKeyboard(keyboard_x,keyboard_y,keyboard_w,keyboard_h,pixel_size):
    innerKeyboard_x = keyboard_x + pixel_size * (paper_inner_margin_upper_x - paper_outer_margin_upper_x)
    innerKeyboard_y = keyboard_y + pixel_size * (paper_inner_margin_upper_y - paper_outer_margin_upper_y) 
    innerKeyboard_w = keyboard_w - 2 * (pixel_size * (paper_inner_margin_upper_x - paper_outer_margin_upper_x))
    innerKeyboard_h = keyboard_h - 2 * (pixel_size * (paper_inner_margin_upper_y - paper_outer_margin_upper_y))
    return int(innerKeyboard_x), int(innerKeyboard_y), int(innerKeyboard_w), int(innerKeyboard_h)

def getWhiteKeyRegion(keyboard_x,keyboard_y,keyboard_w,keyboard_h,pixel_size, key_number):
    # Keyboard innen Koordinaten links oben + Weite und Höhe
    innerKeyborad_x = keyboard_x + pixel_size * (paper_inner_margin_upper_x - paper_outer_margin_upper_x)
    key_y = keyboard_y + pixel_size * (paper_inner_margin_upper_y - paper_outer_margin_upper_y) # key_y = innerKeyborad_y 
    innerKeyborad_w = keyboard_w - 2 * (pixel_size * (paper_inner_margin_upper_x - paper_outer_margin_upper_x))
    key_h = keyboard_h - 2 * (pixel_size * (paper_inner_margin_upper_y - paper_outer_margin_upper_y)) # key_h = innerKeyborad_h 
    
    key_x = innerKeyborad_x + key_number * (innerKeyborad_w / 7)
    key_w = innerKeyborad_w / 7

    return int(key_x), int(key_y), int(key_w), int(key_h)

def getBlackKeyRegion(keyboard_x,keyboard_y,keyboard_w,keyboard_h,pixel_size, key_number):
    # Für die "Lücke" in der Tastatur
    if key_number > 1:
        key_number += 1
    # Keyboard innen Koordinaten links oben + Weite und Höhe
    innerKeyborad_x = keyboard_x + pixel_size * (paper_inner_margin_upper_x - paper_outer_margin_upper_x)
    key_y = keyboard_y + pixel_size * (paper_inner_margin_upper_y - paper_outer_margin_upper_y) # key_y = innerKeyborad_y
    innerKeyborad_w = keyboard_w - 2 * (pixel_size * (paper_inner_margin_upper_x - paper_outer_margin_upper_x))
    innerKeyborad_h = keyboard_h - 2 * (pixel_size * (paper_inner_margin_upper_y - paper_outer_margin_upper_y))
    
    key_x = innerKeyborad_x + (key_number * 2 + 1.5)  * (innerKeyborad_w / 14)
    key_w = innerKeyborad_w / 14
    key_h = innerKeyborad_h * 2/3

    return int(key_x), int(key_y), int(key_w), int(key_h)

def getVolumeMinusRegion(keyboard_x,keyboard_y,pixel_size):
    volume_minus_x = keyboard_x + pixel_size * (paper_volume_minus_upper_x -  paper_outer_margin_upper_x)
    volume_minus_y = keyboard_y + pixel_size * (paper_volume_minus_upper_y - paper_outer_margin_upper_y)
    volume_minus_w = pixel_size * paper_volume_minus_w
    volume_minus_h = pixel_size * paper_volume_minus_h
    return int(volume_minus_x), int(volume_minus_y), int(volume_minus_w), int(volume_minus_h)

def getVolumePlusRegion(keyboard_x,keyboard_y,pixel_size):
    volume_plus_x = keyboard_x + pixel_size * (paper_volume_plus_upper_x -  paper_outer_margin_upper_x)
    volume_plus_y = keyboard_y + pixel_size * (paper_volume_plus_upper_y - paper_outer_margin_upper_y)
    volume_plus_w = pixel_size * paper_volume_plus_w
    volume_plus_h = pixel_size * paper_volume_plus_h
    return int(volume_plus_x), int(volume_plus_y), int(volume_plus_w), int(volume_plus_h)

def getPianoRegion(keyboard_x,keyboard_y,pixel_size):
    # Nicht das Piano, sondern nur der Piano Button
    piano_x = keyboard_x + pixel_size * (paper_piano_upper_x -  paper_outer_margin_upper_x)
    piano_y = keyboard_y + pixel_size * (paper_piano_upper_y - paper_outer_margin_upper_y)
    piano_w = pixel_size * paper_piano_w
    piano_h = pixel_size * paper_piano_h
    return int(piano_x), int(piano_y), int(piano_w), int(piano_h)

def getSynthRegion(keyboard_x,keyboard_y,pixel_size):
    synth_x = keyboard_x + pixel_size * (paper_synth_upper_x -  paper_outer_margin_upper_x)
    synth_y = keyboard_y + pixel_size * (paper_synth_upper_y - paper_outer_margin_upper_y)
    synth_w = pixel_size * paper_synth_w
    synth_h = pixel_size * paper_synth_h
    return int(synth_x), int(synth_y), int(synth_w), int(synth_h)

def getAttackRegion(keyboard_x,keyboard_y,pixel_size):
    attack_x = keyboard_x + pixel_size * (paper_attack_upper_x -  paper_outer_margin_upper_x)
    attack_y = keyboard_y + pixel_size * (paper_attack_upper_y - paper_outer_margin_upper_y)
    attack_w = pixel_size * paper_attack_w
    attack_h = pixel_size * paper_attack_h
    return int(attack_x), int(attack_y), int(attack_w), int(attack_h)

def getReleaseRegion(keyboard_x,keyboard_y,pixel_size):
    release_x = keyboard_x + pixel_size * (paper_release_upper_x -  paper_outer_margin_upper_x)
    release_y = keyboard_y + pixel_size * (paper_release_upper_y - paper_outer_margin_upper_y)
    release_w = pixel_size * paper_release_w
    release_h = pixel_size * paper_release_h
    return int(release_x), int(release_y), int(release_w), int(release_h)

def isFingerIn(finger_x, finger_y, rectangle_x, rectangle_y, rectangle_w, rectangle_h):
    return (rectangle_x < finger_x) and (finger_x < rectangle_x + rectangle_w) and (rectangle_y < finger_y) and (finger_y < rectangle_y + rectangle_h)


def getMilliseconds():
    return time.time_ns() // 1_000_000 

def isCommandTimeoutExceeded(commandStart):
    currentTime = getMilliseconds()
    return (currentTime - commandStart) > 1000

def colorPicker(event,x,y,flags,param): 
    # Bei anderen Lichtverhältnissen die Farbe anpassen
    global h_keyboard_border_color, s_keyboard_border_color, v_keyboard_border_color, h_finger_color, s_finger_color, v_finger_color
    # Pixel an der Mausposition
    pixel = frame[y, x]
    pixel = np.array([[[pixel[0], pixel[1], pixel[2]]]])
    color_HSV = cv2.cvtColor(pixel, cv2.COLOR_BGR2HSV)

    # Linksklick passt die Farbe des Tastaturrands an
    if event == cv2.EVENT_LBUTTONDOWN:
        h_keyboard_border_color = int(color_HSV[0][0][0])
        s_keyboard_border_color = int(color_HSV[0][0][1])
        v_keyboard_border_color = int(color_HSV[0][0][2])
        print("Tastaturfarbe angepasst")
    #Rechtsklick passt die Farbe der Hand an
    elif event == cv2.EVENT_RBUTTONDOWN:
        h_finger_color = int(color_HSV[0][0][0])
        s_finger_color = int(color_HSV[0][0][1])
        v_finger_color = int(color_HSV[0][0][2])
        print("Handfarbe angepasst")


# ------------------------- VIDEO  --------------------------------------------------------

# Named Window Tastatur erstellen
cv2.namedWindow("Tastatur")
# Tracker in Tastatur Window erstellen
cv2.createTrackbar("ThresholdTastatur", "Tastatur", 80, 100, do_nothing)

# Named Window Finger erstellen
cv2.namedWindow("Finger")
# Tracker in Finger Window erstellen
cv2.createTrackbar("ThresholdFinger", "Finger", 70, 100, do_nothing)

# Video aus Datei öffnen
# cap = cv2.VideoCapture('../media/Papiertastatur_MitFinger.mp4')
cap = cv2.VideoCapture('../media/TastaturOhneAR.mp4')

# Live Video
#cap=cv2.VideoCapture(0)

# Zeitstempel für die Finger Kommandos
commandStart = getMilliseconds()
while cap.isOpened():
    ret, frame = cap.read()

    # Skaling (für mp4-Video)
    frame = cv2.resize(frame, (960, 540))
    
    # Original Video anzeigen
    cv2.imshow('Original', frame)

    cv2.setMouseCallback("Original", colorPicker)

    ###################### FINGER #################################

    # Threshold Wert aus Tracker lesen
    finger_threshold = cv2.getTrackbarPos('ThresholdFinger', 'Finger')
    # Finger Rand finden
    finger_mask, finger_contours, finger_biggestRegionIndex, finger_cnt = findBiggestRegionForColor(frame, h_finger_color, s_finger_color, v_finger_color, finger_threshold)
    # Zeichnet größte Region (Finger) weiß
    cv2.drawContours(finger_mask, finger_contours, finger_biggestRegionIndex, (255,255,255), cv2.FILLED)
    # Finger zeichnen
    # wir finden die Spitze des Fingers (das ist die Top Y Koordinate)
    finger_upper_point = finger_cnt[finger_cnt[:,:,1].argmin()][0]
    # und wir zeichnen einen Kreis. Dafür erxtrahieren wir den Radius der Finger, sodass unser Kreis über den Finger liegt
    finger_upper_point[1] = finger_upper_point[1] + finger_radius
    cv2.circle(frame, tuple(finger_upper_point), finger_radius, (0, 0, 255), -1)

    ###################### KEYBOARD #################################

    # Threshold Wert aus Tracker lesen
    keyboard_threshold = cv2.getTrackbarPos('ThresholdTastatur', 'Tastatur')
    # Keyboard Rand finden
    keyboard_mask, keyboard_contours, keyboard_biggestRegionIndex, keyboard_cnt = findBiggestRegionForColor(frame, h_keyboard_border_color, s_keyboard_border_color, v_keyboard_border_color, keyboard_threshold)

    # Zeichnet größte Region (Keyboard) weiß
    cv2.drawContours(keyboard_mask, keyboard_contours, keyboard_biggestRegionIndex, (255,255,255), cv2.FILLED)

    # Rotiertes Keyboard
    # Here, bounding rectangle is drawn with minimum area, so it considers the rotation also. 
    # The function used is cv.minAreaRect(). It returns a Box2D structure which contains 
    # following details - ( center (x,y), (width, height), angle of rotation ). 
    # But to draw this rectangle, we need 4 corners of the rectangle. It is obtained by the function cv.boxPoints()
    keyboard_rect = cv2.minAreaRect(keyboard_cnt)
    keyboard_box = cv2.boxPoints(keyboard_rect)
    keyboard_box = np.int0(keyboard_box)
    # keyboard_box_x = keyboard_box[0][0]
    # keyboard_box_y = keyboard_box[0][1]
    # keyboard_box_w = keyboard_rect[1][0]
    # keyboard_box_h = keyboard_rect[1][1]
    cv2.drawContours(frame,[keyboard_box],0,(255,0,255),2)
    # Hiermit kann später die Tastatur genauer erfasst werden, auch wenn sie gedreht ist

    # Keyboard zeichnen
    keyboard_x,keyboard_y,keyboard_w,keyboard_h = cv2.boundingRect(keyboard_cnt)
    # es ist möglich dass die Hand/Finger ein Teil der Tasatur abdeckt
    # in diesem Fall wird nicht die ganze Tastatur als Contour identifiziert, sondern nur einen Teil
    # und wir müssen die richtigen Koordinaten berechnen
    if (keyboard_w < 2 * keyboard_h):
        # Teil der Tastatur ist von Hand abgedeckt und muss richtig berechnete werden
        # Shift nach Rechts für X
        keyboard_x = keyboard_x + keyboard_w
        # neues Width berechnen
        keyboard_w = int(2.05 * keyboard_h)
        # Shift nach Links für X
        keyboard_x = keyboard_x - keyboard_w
    cv2.rectangle(frame, (keyboard_x, keyboard_y), (keyboard_x + keyboard_w, keyboard_y + keyboard_h), color=(0, 255, 0), thickness=2)

    ###################### PIXEL GRÖßE #################################

    # relative Pixelgrüße finden
    pixel_size = getPixelSize(keyboard_h)

    ###################### KNÖPFE #################################

    ## Inner Keyboard
    innerKeyboard_x, innerKeyboard_y, innerKeyboard_w, innerKeyboard_h = getInnerKeyboard(keyboard_x,keyboard_y,keyboard_w,keyboard_h,pixel_size)
    # cv2.rectangle(frame, (innerKeyboard_x, innerKeyboard_y), (innerKeyboard_x + innerKeyboard_w, innerKeyboard_y + innerKeyboard_h), color=(255, 0, 0), thickness=5)

    ## Weiße Tasten zeichnen
    whiteKeys = np.zeros(shape=(7,4))
    for x in range(7):
        key_x, key_y, key_w, key_h = getWhiteKeyRegion(keyboard_x,keyboard_y,keyboard_w,keyboard_h,pixel_size,x)
        whiteKeys[x,0] = key_x 
        whiteKeys[x,1] = key_y 
        whiteKeys[x,2] = key_w
        whiteKeys[x,3] = key_h
        cv2.rectangle(frame, (key_x, key_y), (key_x + key_w, key_y + key_h), color=(0, 0, 255), thickness=2)

    ## Schwarze Tasten zeichnen
    blackKeys = np.zeros(shape=(5,4))
    for y in range(5):
        key_x, key_y, key_w, key_h = getBlackKeyRegion(keyboard_x,keyboard_y,keyboard_w,keyboard_h,pixel_size,y)
        blackKeys[y,0] = key_x 
        blackKeys[y,1] = key_y 
        blackKeys[y,2] = key_w
        blackKeys[y,3] = key_h
        cv2.rectangle(frame, (key_x, key_y), (key_x + key_w, key_y + key_h), color=(0, 255, 255), thickness=2)
    
    ## Volume Minus zeichnen
    volume_minus_x, volume_minus_y, volume_minus_w, volume_minus_h = getVolumeMinusRegion(keyboard_x,keyboard_y,pixel_size)
    cv2.rectangle(frame, (volume_minus_x, volume_minus_y), (volume_minus_x + volume_minus_w, volume_minus_y + volume_minus_h), color=(0, 255, 0), thickness=2)
 
    ## Volume Plus zeichnen
    volume_plus_x, volume_plus_y, volume_plus_w, volume_plus_h = getVolumePlusRegion(keyboard_x,keyboard_y,pixel_size)
    cv2.rectangle(frame, (volume_plus_x, volume_plus_y), (volume_plus_x + volume_plus_w, volume_plus_y + volume_plus_h), color=(0, 255, 0), thickness=2)

    ## Piano (Button) zeichnen
    piano_x, piano_y, piano_w, piano_h = getPianoRegion(keyboard_x,keyboard_y,pixel_size)
    cv2.rectangle(frame, (piano_x, piano_y), (piano_x + piano_w, piano_y + piano_h), color=(0, 255, 0), thickness=2)

    ## Synth zeichnen
    synth_x, synth_y, synth_w, synth_h = getSynthRegion(keyboard_x,keyboard_y,pixel_size)
    cv2.rectangle(frame, (synth_x, synth_y), (synth_x + synth_w, synth_y + synth_h), color=(0, 255, 0), thickness=2)

    ## Attack zeichnen
    attack_x, attack_y, attack_w, attack_h = getAttackRegion(keyboard_x,keyboard_y,pixel_size)
    cv2.rectangle(frame, (attack_x, attack_y), (attack_x + attack_w, attack_y + attack_h), color=(0, 255, 0), thickness=2)

    ## Release zeichnen
    release_x, release_y, release_w, release_h = getReleaseRegion(keyboard_x,keyboard_y,pixel_size)
    cv2.rectangle(frame, (release_x, release_y), (release_x + release_w, release_y + release_h), color=(0, 255, 0), thickness=2)

    ###################### PRÜFE WELCHES ELEMENT WURDE GEDRÜCKT #################################

    finger_x = finger_upper_point[0]
    finger_y = finger_upper_point[1]
    fingerOnBlackKey = False

    # Inner Keyboard
    if (isFingerIn(finger_x, finger_y, innerKeyboard_x, innerKeyboard_y, innerKeyboard_w, innerKeyboard_h)):
        # Wenn im inneren Keyboard, dann erst schwarze Tasten überprüfen
        # Black Keys
        for x in range(5):
            if (isFingerIn(finger_x, finger_y, blackKeys[x,0], blackKeys[x,1], blackKeys[x,2], blackKeys[x,3])):
                fingerOnBlackKey = True
                if (command != "Play Black Key " + str(x)):
                    command = "Play Black Key " + str(x)
                    commandStart = getMilliseconds()
                elif isCommandTimeoutExceeded(commandStart):
                    print('Play Black Key ' + str(x))
                    blackKey(x)
                    command = 'none'
        # White Keys
        if not fingerOnBlackKey: # Schwarze Tasten liegen im Bereich der weißen Tasten, deswegen erst sichergehen, dass keine schwarze Taste gedrückt wurde
            for y in range(7):
                if (isFingerIn(finger_x, finger_y, whiteKeys[y,0], whiteKeys[y,1], whiteKeys[y,2], whiteKeys[y,3])):
                    if (command != "Play White Key " + str(y)):
                        command = "Play White Key " + str(y)
                        commandStart = getMilliseconds()
                    elif isCommandTimeoutExceeded(commandStart):
                        print('Play White Key ' + str(y))
                        whiteKey(y)
                        command = 'none'
    # Volume Minus
    elif (isFingerIn(finger_x, finger_y, volume_minus_x, volume_minus_y, volume_minus_w, volume_minus_h)):
        if (command != "Volume Minus"):
            command = "Volume Minus"
            commandStart = getMilliseconds()
        elif isCommandTimeoutExceeded(commandStart):
            print('Volume Minus')
            volumeMinus()
            command = 'none'
    # Volume Plus
    elif (isFingerIn(finger_x, finger_y, volume_plus_x, volume_plus_y, volume_plus_w, volume_plus_h)):
        if (command != "Volume Plus"):
            command = "Volume Plus"
            commandStart = getMilliseconds()
        elif isCommandTimeoutExceeded(commandStart):
            print('Volume Plus')
            volumePlus()
            command = 'none'
    # Piano
    elif (isFingerIn(finger_x, finger_y, piano_x, piano_y, piano_w, piano_h)):
        if (command != "Piano"):
            command = "Piano"
            commandStart = getMilliseconds()
        elif isCommandTimeoutExceeded(commandStart):
            print('Piano')
            piano()
            command = 'none'
    # Synth
    elif (isFingerIn(finger_x, finger_y, synth_x, synth_y, synth_w, synth_h)):
        if (command != "Synth"):
            command = "Synth"
            commandStart = getMilliseconds()
        elif isCommandTimeoutExceeded(commandStart):
            print('Synth')
            synth()
            command = 'none'
    # Attack
    elif (isFingerIn(finger_x, finger_y, attack_x, attack_y, attack_w, attack_h)):
        if (command != "Attack"):
            command = "Attack"
            commandStart = getMilliseconds()
        elif isCommandTimeoutExceeded(commandStart):
            print('Attack')
            attack()
            command = 'none'
    # Release
    elif (isFingerIn(finger_x, finger_y, release_x, release_y, release_w, release_h)):
        if (command != "Release"):
            command = "Release"
            commandStart = getMilliseconds()
        elif isCommandTimeoutExceeded(commandStart):
            print('Release')
            release()
            command = 'none'
    else:
        command = 'none'

    ###################### ERGEBNISSE #################################

    # Kombiniertes Ergebnis anzeigen
    cv2.imshow('Tastatur', keyboard_mask)
    cv2.imshow('Finger', finger_mask)
    cv2.imshow("Contour", frame)
 
    # Abbruch bei Tastendruck
    if cv2.waitKey(25) != -1:
        break

# cap wieder freigeben
cap.release()

# Fenster schließen
cv2.destroyAllWindows()
