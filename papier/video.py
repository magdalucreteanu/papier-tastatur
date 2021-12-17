import cv2
# ausgewählter Pixel für den Tastaturrand
# rgb(180, 60, 60)
red = 180
green = 60
blue = 60

# Callback Funktion für Slider - tut nichts
def do_nothing():
    return

# Named Window Tastatur erstellen
cv2.namedWindow("Tastatur")
# Tracker in Tastatur Window erstellen
cv2.createTrackbar("Threshold", "Tastatur", 0, 50, do_nothing)
cv2.createTrackbar("Red", "Tastatur", 0, 255, do_nothing)
cv2.createTrackbar("Green", "Tastatur", 0, 60, do_nothing)
cv2.createTrackbar("Blue", "Tastatur", 0, 60, do_nothing)

#Video aus Datei öffnen
#cap = cv2.VideoCapture('../media/Papier_Tastatur_Video_MP4.mp4')

# Live Video
cap=cv2.VideoCapture(0)

while cap.isOpened():
    ret, frame = cap.read()

    # Original Video anzeigen
    cv2.imshow('Original', frame)

    # Threshold Wert aus Tracker lesen
    threshold = cv2.getTrackbarPos('Threshold', 'Tastatur')

    # Find best RGB
    red = cv2.getTrackbarPos('Red', 'Tastatur')
    green = cv2.getTrackbarPos('Green', 'Tastatur')
    blue = cv2.getTrackbarPos('Blue', 'Tastatur')

    # aufspalten in drei Farbkanäle
    b, g, r = cv2.split(frame)

    # Threshold setzen
    cv2.inRange(b, blue - threshold, blue + threshold, b)
    cv2.inRange(g, green - threshold, green + threshold, g)
    cv2.inRange(r, red - threshold, red + threshold, r)

    # Split Farben anzeigen
    #cv2.imshow('Blue', b)
    #cv2.imshow('Green', g)
    #cv2.imshow('Red', r)

    # Farben kombinieren (multiplizieren)
    mask = b * g * r
    # Kombiniertes Ergebnis anzeigen
    cv2.imshow('Tastatur', mask)
 
    # Abbruch bei Tastendruck
    if cv2.waitKey(25) != -1:
        break;

# cap wieder freigeben
cap.release()

# Fenster schließen
cv2.destroyAllWindows()
