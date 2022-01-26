import websocket
import cv2
import json
import time
import numpy as np

# Ausgewählter Pixel für den Tastaturrand, einlesen und in HSV-Farbbereich umwandeln
keyboard_border_color = cv2.imread('../media/Tastaturrand_Farbe.jpg',cv2.IMREAD_COLOR )
keyboard_border_color_HSV = cv2.cvtColor(keyboard_border_color, cv2.COLOR_BGR2HSV)
h_keyboard_border_color = int(keyboard_border_color_HSV[0][0][0])
s_keyboard_border_color = int(keyboard_border_color_HSV[0][0][1])
v_keyboard_border_color = int(keyboard_border_color_HSV[0][0][2])

# Ausgewählter Pixel für den Finger, einlesen und in HSV-Farbbereich umwandeln
finger_color = cv2.imread('../media/Finger_Farbe.jpg',cv2.IMREAD_COLOR )
finger_color_HSV = cv2.cvtColor(finger_color, cv2.COLOR_BGR2HSV)
h_finger_color = int(finger_color_HSV[0][0][0])
s_finger_color = int(finger_color_HSV[0][0][1])
v_finger_color = int(finger_color_HSV[0][0][2])
finger_radius = 10

# Koordinaten der Elemente innerhalb des originalen Bilders (mit den zwei Beispieltastaturen)
# Wir identifizieren este die Tastatur anhand des roten Randes.
# Danach finden wir die einzelnen Elemente mathematisch anhand der Koordinaten.

# Tastatur-Kooardinaten
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

# Distortion
paper_distortion_upper_x = 624
paper_distortion_upper_y = 1015
paper_distortion_w = 290
paper_distortion_h = 45

# Reverb
paper_reverb_upper_x = 624
paper_reverb_upper_y = 1108
paper_reverb_w = 290
paper_reverb_h = 63

# Gespeicherte Werte
command = 'none'
savedXKeyboard = 0
savedWKeyboard = 0
printAgain = True

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

# Sende Distortion Kommando über WebSocket
def distortion(value):
    data = {
        "timestamp": time.time(),
        "name": "distortion",
        "value": value
    }
    sendMessage(data)

# Sende Reverb Kommando über WebSocket
def reverb(index):
    data = {
        "timestamp": time.time(),
        "name": "reverb",
        "index": index
    }
    sendMessage(data)

#--------------------------FUNKTIONEN FÜRS VIDEO-------------------------------------------

# Größe Region einer Farbe finden
def findBiggestRegionForColor(frame, h, s, v, h_threshold, s_threshold_min, v_threshold_min, isHand):
    # Umwandlung in HSV Farbraum
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Grenzen
    lower = np.array([h - h_threshold, s_threshold_min, v_threshold_min])
    upper = np.array([h + h_threshold, 255, 255])

    # Threshold HSV Image um nur Piano Randfarben zu bekommen
    mask = cv2.inRange(hsv, lower, upper)

    # Dilation: Schwächere Pixel stärken
    kernel = np.ones((3,3),np.uint8)
    mask = cv2.dilate(mask,kernel,iterations = 1)
    
    # Opening: Noise aus dem Hintergrund entfernen
    # Für die Hand etwas höher eingestellt, um bei Schattenwurf weniger Störungen zu haben
    if(isHand == True):
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (15,15))
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    else:
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5,5))
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)

    # Medianfilter: Bild "smoothen"
    mask = cv2.medianBlur(mask, 5)

    # Region Finding Algorithmus: liefert Array contours, jedes Objekt repräsentiert eine zusammenhängende Region
    contours, hierarchy = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    # Berechnet Fläche einer Region
    biggestRegion = 0
    biggestRegionIndex = 0
    cnt = 0
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

# Pixel Größenverhälnis errechnen
def getPixelSize(w):
    return 1.0 * w / (paper_outer_margin_lower_y - paper_outer_margin_upper_y)

# Innere Tastatur Werte der Region berechnen
def getInnerKeyboard(keyboard_x,keyboard_y,keyboard_w,keyboard_h,pixel_size):
    innerKeyboard_x = keyboard_x + pixel_size * (paper_inner_margin_upper_x - paper_outer_margin_upper_x)
    innerKeyboard_y = keyboard_y + pixel_size * (paper_inner_margin_upper_y - paper_outer_margin_upper_y) 
    innerKeyboard_w = keyboard_w - 2 * (pixel_size * (paper_inner_margin_upper_x - paper_outer_margin_upper_x))
    innerKeyboard_h = keyboard_h - 2 * (pixel_size * (paper_inner_margin_upper_y - paper_outer_margin_upper_y))
    return int(innerKeyboard_x), int(innerKeyboard_y), int(innerKeyboard_w), int(innerKeyboard_h)

# Weiße Tasten Werte der Region berechnen
def getWhiteKeyRegion(keyboard_x,keyboard_y,keyboard_w,keyboard_h,pixel_size, key_number):
    # Keyboard innen Koordinaten links oben + Weite und Höhe
    innerKeyborad_x = keyboard_x + pixel_size * (paper_inner_margin_upper_x - paper_outer_margin_upper_x)
    key_y = keyboard_y + pixel_size * (paper_inner_margin_upper_y - paper_outer_margin_upper_y) # key_y = innerKeyborad_y 
    innerKeyborad_w = keyboard_w - 2 * (pixel_size * (paper_inner_margin_upper_x - paper_outer_margin_upper_x))
    key_h = keyboard_h - 2 * (pixel_size * (paper_inner_margin_upper_y - paper_outer_margin_upper_y)) # key_h = innerKeyborad_h 
    
    key_x = innerKeyborad_x + key_number * (innerKeyborad_w / 7)
    key_w = innerKeyborad_w / 7

    return int(key_x), int(key_y), int(key_w), int(key_h)

# Schwarze Tasten Werte der Region berechnen
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

# Lautstärke Minus Werte der Region berechnen
def getVolumeMinusRegion(keyboard_x,keyboard_y,pixel_size):
    volume_minus_x = keyboard_x + pixel_size * (paper_volume_minus_upper_x -  paper_outer_margin_upper_x)
    volume_minus_y = keyboard_y + pixel_size * (paper_volume_minus_upper_y - paper_outer_margin_upper_y)
    volume_minus_w = pixel_size * paper_volume_minus_w
    volume_minus_h = pixel_size * paper_volume_minus_h
    return int(volume_minus_x), int(volume_minus_y), int(volume_minus_w), int(volume_minus_h)

# Lautstärke Minus Werte der Region berechnen
def getVolumePlusRegion(keyboard_x,keyboard_y,pixel_size):
    volume_plus_x = keyboard_x + pixel_size * (paper_volume_plus_upper_x -  paper_outer_margin_upper_x)
    volume_plus_y = keyboard_y + pixel_size * (paper_volume_plus_upper_y - paper_outer_margin_upper_y)
    volume_plus_w = pixel_size * paper_volume_plus_w
    volume_plus_h = pixel_size * paper_volume_plus_h
    return int(volume_plus_x), int(volume_plus_y), int(volume_plus_w), int(volume_plus_h)

# Lautstärke Plus Werte der Region berechnen
def getPianoRegion(keyboard_x,keyboard_y,pixel_size):
    # Nicht das Piano, sondern nur der Piano Button
    piano_x = keyboard_x + pixel_size * (paper_piano_upper_x -  paper_outer_margin_upper_x)
    piano_y = keyboard_y + pixel_size * (paper_piano_upper_y - paper_outer_margin_upper_y)
    piano_w = pixel_size * paper_piano_w
    piano_h = pixel_size * paper_piano_h
    return int(piano_x), int(piano_y), int(piano_w), int(piano_h)

# Synthesizer Werte der Region berechnen
def getSynthRegion(keyboard_x,keyboard_y,pixel_size):
    synth_x = keyboard_x + pixel_size * (paper_synth_upper_x -  paper_outer_margin_upper_x)
    synth_y = keyboard_y + pixel_size * (paper_synth_upper_y - paper_outer_margin_upper_y)
    synth_w = pixel_size * paper_synth_w
    synth_h = pixel_size * paper_synth_h
    return int(synth_x), int(synth_y), int(synth_w), int(synth_h)

# Distortion Werte der Region berechnen
def getDistortionRegion(keyboard_x,keyboard_y,pixel_size):
    distortion_x = keyboard_x + pixel_size * (paper_distortion_upper_x -  paper_outer_margin_upper_x)
    distortion_y = keyboard_y + pixel_size * (paper_distortion_upper_y - paper_outer_margin_upper_y)
    distortion_w = pixel_size * paper_distortion_w
    distortion_h = pixel_size * paper_distortion_h
    return int(distortion_x), int(distortion_y), int(distortion_w), int(distortion_h)

# Reverb Werte der ganzen Region berechnen
def getReverbFullRegion(keyboard_x,keyboard_y,pixel_size ):
    reverb_x = keyboard_x + pixel_size * (paper_reverb_upper_x -  paper_outer_margin_upper_x)
    reverb_y = keyboard_y + pixel_size * (paper_reverb_upper_y - paper_outer_margin_upper_y)
    reverb_w = pixel_size * paper_reverb_w
    reverb_h = pixel_size * paper_reverb_h
    return int(reverb_x), int(reverb_y), int(reverb_w), int(reverb_h)

# Reverb Werte der einzelnen Regionen berechnen
def getReverbRegion(keyboard_x,keyboard_y,pixel_size, reverb_number):
    reverb_x = keyboard_x + pixel_size * (paper_reverb_upper_x -  paper_outer_margin_upper_x)
    reverb_y = keyboard_y + pixel_size * (paper_reverb_upper_y - paper_outer_margin_upper_y)
    reverb_w = pixel_size * (paper_reverb_w / 4)
    reverb_h = pixel_size * paper_reverb_h
    reverb_x = reverb_x + (reverb_number ) * reverb_w 
    return int(reverb_x), int(reverb_y), int(reverb_w), int(reverb_h)

# Berechnung, ob der Finger sich in einer Region befindet
def isFingerIn(finger_x, finger_y, rectangle_x, rectangle_y, rectangle_w, rectangle_h):
    return (rectangle_x < finger_x) and (finger_x < rectangle_x + rectangle_w) and (rectangle_y < finger_y) and (finger_y < rectangle_y + rectangle_h)

# Millisekunden bekommen
def getMilliseconds():
    return time.time_ns() // 1_000_000 

# Hat ein Kommanda die vorgegebene Zeit überschritten
def isCommandTimeoutExceeded(commandStart):
    currentTime = getMilliseconds()
    return (currentTime - commandStart) > 1000

# Farben des Tastaturrands und der Hand anpassen
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
cv2.createTrackbar("HThresTastatur", "Tastatur", 15, 120, do_nothing)
cv2.createTrackbar("SThresTastaturMin", "Tastatur", 60, 120, do_nothing)
cv2.createTrackbar("VThresTastaturMin", "Tastatur", 20, 120, do_nothing)

# Named Window Finger erstellen
cv2.namedWindow("Finger")
# Tracker in Finger Window erstellen
cv2.createTrackbar("HThresFinger", "Finger", 15, 120, do_nothing)
cv2.createTrackbar("SThresFingerMin", "Finger", 70, 120, do_nothing)
cv2.createTrackbar("VThresFingerMin", "Finger", 40, 120, do_nothing)

# Video aus Datei öffnen
# cap = cv2.VideoCapture('../media/Tastatur_MitFinger_01.mp4')
cap = cv2.VideoCapture('../media/Tastatur_MitFinger_02.mp4')
# cap = cv2.VideoCapture('../media/Tastatur_MitFinger_03.mp4')
# cap = cv2.VideoCapture('../media/Tastatur_MitFinger_04.mp4')

# Live Video
# cap=cv2.VideoCapture(0)

# Zeitstempel für die Finger Kommandos
commandStart = getMilliseconds()
while cap.isOpened():
    ret, frame = cap.read()

    # Skaling (für mp4-Video aus Datei)
    frame = cv2.resize(frame, (960, 540))

    # Original Video anzeigen
    cv2.imshow('Original', frame)

    # Farben des Tastaturrands und der Hand anpassen
    cv2.setMouseCallback("Original", colorPicker)

    ###################### FINGER #################################

    # Threshold Wert aus Tracker lesen
    h_finger_threshold = cv2.getTrackbarPos('HThresFinger', 'Finger')
    s_finger_threshold_min = cv2.getTrackbarPos('SThresFingerMin', 'Finger')
    v_finger_threshold_min = cv2.getTrackbarPos('VThresFingerMin', 'Finger')
    # Finger Rand finden
    finger_mask, finger_contours, finger_biggestRegionIndex, finger_cnt = findBiggestRegionForColor(frame, h_finger_color, s_finger_color, v_finger_color, h_finger_threshold, s_finger_threshold_min, v_finger_threshold_min, True)
    
    # Wenn CNT für Finger vorhanden ist
    if(type(finger_cnt) != int):
        # Zeichnet größte Region (Finger) weiß
        cv2.drawContours(finger_mask, finger_contours, finger_biggestRegionIndex, (255,255,255), cv2.FILLED)
        # Finger zeichnen
        # wir finden die Spitze des Fingers (das ist die Top Y Koordinate)
        finger_upper_point = finger_cnt[finger_cnt[:,:,1].argmin()][0]
        # Und wir zeichnen einen Kreis. Dafür erxtrahieren wir den Radius der Finger, sodass unser Kreis über den Finger liegt
        # Die Y-Koordinate des Fingers wird etwas nach unten verschoben
        # Dadurch wird nicht direkt die Fingerspitze, sondern die Mitte der Fingerspitze erkannt
        finger_upper_point[1] = finger_upper_point[1] + finger_radius
        cv2.circle(frame, tuple(finger_upper_point), finger_radius, (0, 0, 255), -1)

    ###################### KEYBOARD #################################

    # Threshold Wert aus Tracker lesen
    h_keyboard_threshold = cv2.getTrackbarPos('HThresTastatur', 'Tastatur')
    s_keyboard_threshold_min = cv2.getTrackbarPos('SThresTastaturMin', 'Tastatur')
    v_keyboard_threshold_min = cv2.getTrackbarPos('VThresTastaturMin', 'Tastatur')
    # Keyboard Rand finden
    keyboard_mask, keyboard_contours, keyboard_biggestRegionIndex, keyboard_cnt = findBiggestRegionForColor(frame, h_keyboard_border_color, s_keyboard_border_color, v_keyboard_border_color, h_keyboard_threshold, s_keyboard_threshold_min, v_keyboard_threshold_min, False)

    # Wenn CNT für Keyboard vorhanden ist
    if(type(keyboard_cnt) != int):
        # Zeichnet größte Region (Keyboard) weiß
        cv2.drawContours(keyboard_mask, keyboard_contours, keyboard_biggestRegionIndex, (255,255,255), cv2.FILLED)

        # Rotiertes Keyboard
        # von https://docs.opencv.org/3.4/dd/d49/tutorial_py_contour_features.html
        # Here, bounding rectangle is drawn with minimum area, so it considers the rotation also. 
        # The function used is cv.minAreaRect(). It returns a Box2D structure which contains 
        # following details - ( center (x,y), (width, height), angle of rotation ). 
        # But to draw this rectangle, we need 4 corners of the rectangle. It is obtained by the function cv.boxPoints()
        keyboard_rect = cv2.minAreaRect(keyboard_cnt)
        keyboard_box = cv2.boxPoints(keyboard_rect)
        keyboard_box = np.int0(keyboard_box)
        # cv2.drawContours(frame,[keyboard_box],0,(255,0,255),2) # Kontur malen
        # Wenn Papier zu sehr gedreht, Warnung ausgeben
        if (keyboard_rect[2] > 5.0 and keyboard_rect[2] < 85.0):
            if(printAgain == True):
                print('Das Papier ist zur Zeit zu sehr gedreht. Bitte richte das Papier gerade aus.')
                printAgain=False
        else:
            printAgain=True
       
        # Keyboard zeichnen
        # Keyboard Werte bestimmen
        keyboard_x,keyboard_y,keyboard_w,keyboard_h = cv2.boundingRect(keyboard_cnt)
        # Es ist möglich dass die Hand / der Finger ein Teil der Tasatur abdeckt
        # In diesem Fall wird nicht die ganze Tastatur als Contour identifiziert, sondern nur einen Teil
        # und wir müssen die richtigen Koordinaten berechnen
        if (keyboard_w < 1.95 * keyboard_h):
            # Teil der Tastatur ist von Hand abgedeckt und muss richtig berechnet werden
            # Wenn Breite kleiner als 1.95 * Höhe ist, dann ist entweder links oder rechts teilweise bedeckt
            # Dann greift das Programm kurzzeitig auf die vorher gespeicherten Punkte zu

            # Verdeckte Seite ermitteln
            if((keyboard_x - savedXKeyboard) > (savedWKeyboard/20)):
                # Links ist verdeckt, X-Koordinate und Weite überschreiben
                keyboard_x = savedXKeyboard
                keyboard_w = savedWKeyboard
            else:
                # Rechts ist verdeckt, X-Koordinate stimmt also noch, nur Weite muss korrigiert werden
                keyboard_w = savedWKeyboard
            
        else:
            # Falls das nicht der Fall sein sollte, jetzige Punkte der Tastatur zwischenspeichern
            if(savedWKeyboard != keyboard_w or savedXKeyboard != keyboard_x):
                    savedXKeyboard = keyboard_x
                    savedWKeyboard = keyboard_w

        # Tatsächliches Zeichnen des Keyboards
        cv2.rectangle(frame, (keyboard_x, keyboard_y), (keyboard_x + keyboard_w, keyboard_y + keyboard_h), color=(0, 255, 0), thickness=2)

        ###################### PIXEL GRÖßE #################################

        # Relative Pixelgröße finden
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

        ## Distortion zeichnen
        distortion_x, distortion_y, distortion_w, distortion_h = getDistortionRegion(keyboard_x,keyboard_y,pixel_size)
        cv2.rectangle(frame, (distortion_x, distortion_y), (distortion_x + distortion_w, distortion_y + distortion_h), color=(0, 255, 0), thickness=2)

        ## Full Reverb Region
        reverb_x, reverb_y, reverb_w, reverb_h = getReverbFullRegion(keyboard_x,keyboard_y,pixel_size)
        # cv2.rectangle(frame, (reverb_x, reverb_y), (reverb_x + reverb_w, reverb_y + reverb_h), color=(255, 255, 0), thickness=2)

        ## Reverb zeichnen
        reverbButtons = np.zeros(shape=(4,4))
        for z in range(4):
            button_x, button_y, button_w, button_h = getReverbRegion(keyboard_x,keyboard_y,pixel_size,z)
            reverbButtons[z,0] = button_x 
            reverbButtons[z,1] = button_y 
            reverbButtons[z,2] = button_w
            reverbButtons[z,3] = button_h
            cv2.rectangle(frame, (button_x, button_y), (button_x + button_w, button_y + button_h), color=(0, 255, 0), thickness=2)
        
        ###################### PRÜFE WELCHES ELEMENT WURDE GEDRÜCKT #################################

        # Überprüfen, ob ein Element gedrückt wurde. Wenn der Finger sich eine Sekunde auf einer Taste befindet, wird diese ausgelöst.
        # Durch das Warten von einer Sekunde wird sichergestellt, dass die Taste nicht versehentlich ausgelöst wird. 
        # Zum Beispiel, wenn die Hand nur kurz über die Tastatur bewegt wird, um an die Tasten oben zu kommen.
        # Das entsprechende Kommando der jeweiligen Taste wird dann mit Web Sockets an den Audio-Teil gesendet.
        
        # Wenn ein CNT für das Keyboard (bereits bestehende if-Bedingung) und ein CNT für den Finger vorhanden sind
        if(type(finger_cnt) != int):
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
            # Distortion
            elif (isFingerIn(finger_x, finger_y, distortion_x, distortion_y, distortion_w, distortion_h)):
                if (command != "Distortion"):
                    command = "Distortion"
                    commandStart = getMilliseconds()
                elif isCommandTimeoutExceeded(commandStart):
                    value_distortion = ((finger_x - distortion_x) / distortion_w) * 100 # Zahl zischen 0 und 100
                    print('Distortion ' + str(int(value_distortion)))
                    distortion(int(value_distortion))
                    command = 'none'
            # Reverb
            elif (isFingerIn(finger_x, finger_y, reverb_x, reverb_y, reverb_w, reverb_h)):
                for x in range(4):
                    if (isFingerIn(finger_x, finger_y, reverbButtons[x,0], reverbButtons[x,1], reverbButtons[x,2], reverbButtons[x,3])):
                        if (command != "Reverb " + str(x)):
                            command = "Reverb " + str(x)
                            commandStart = getMilliseconds()
                        elif isCommandTimeoutExceeded(commandStart):
                            print('Reverb ' + str(x))
                            reverb(x)
                            command = 'none'
            else:
                command = 'none'

    # Kommando als Text in Frame schreiben
    cv2.putText(frame, 'Command: '+ command, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, 
                (0, 0, 0), 2, cv2.LINE_AA)

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
