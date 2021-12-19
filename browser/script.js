// WebAudio context erstellen
var audioContext = new (window.AudioContext || window.webkitAudioContext)();
var oscillatorNode = audioContext.createOscillator()
var gainNode = audioContext.createGain()

// Oscillator Node konfigurieren
oscillatorNode.frequency.value = 0
// sofort starten
oscillatorNode.start(0)
oscillatorNode.connect(gainNode)

// Gain Node konfigurieren
gainNode.gain.value = 0.5
gainNode.connect(audioContext.destination)

// Quelle für Frequenzen/Halbtöne: https://de.wikipedia.org/wiki/Frequenzen_der_gleichstufigen_Stimmung
noten =
[
  { "frequez" : "130.813", "halbton" : false }, // C3
  { "frequez" : "138.591", "halbton" : true } , // C#3/Db3
  { "frequez" : "146.832", "halbton" : false }, // D3
  { "frequez" : "155.563", "halbton" : true },  // D#3/Eb3
  { "frequez" : "164.814", "halbton" : false }, // E3
  { "frequez" : "174.614", "halbton" : false }, // F3
  { "frequez" : "184.997", "halbton" : true },  // F#3/Gb3
  { "frequez" : "195.998", "halbton" : false }, // G3
  { "frequez" : "207.652", "halbton" : true },  // G#3/Ab3
  { "frequez" : "220.000", "halbton" : false }, // A3
  { "frequez" : "233.082", "halbton" : true },  // A#3/Bb3
  { "frequez" : "246.942", "halbton" : false }  // B3
]

noten.forEach(note => {
  // finde ob eine note ein Halbton ist oder nicht
  var halbton = ((note.halbton) ? " halbton" : "")
  // erstelle die Klasse dafür
  var klasse = "class='klavier__btn basic" + halbton +  "'"
  // setze die Frequenz der Note im HTML Element
  var frequenz = "frequez='" + note.frequez + "'"
  // die Note wird zum Element 'klavier' hinzugefügt
  document.getElementById('klavier').innerHTML += "<button onClick='klickNote(this)' " + klasse + " " + frequenz + "</button>"
})

// Taste wurde gedrückt
function klickNote(element) {
  // Finde die aktuell gedrückten Tasten und entferne die 'pressed' CSS
  var pressedElements = document.getElementsByClassName('pressed');
  // pressedElements ist eine HTMLCollection, wir müssen diese in Array konvertieren
  Array.from(pressedElements).forEach(pressedElement => pressedElement.classList.remove('pressed'))
  // wir setzen die CSS 'pressed' zur gedrückten Taste
  element.classList.add('pressed')

  // Frequenz setzen
  oscillatorNode.frequency.value = parseInt(element.getAttribute('frequez'))
}

// Volume Minus
function minus() {
  var newValue = gainNode.gain.value - 0.1
  if (newValue < 0) {
    newValue = 0
  }
  gainNode.gain.setValueAtTime(newValue, audioContext.currentTime);
}

// Volume Plus
function plus() {
  var newValue = gainNode.gain.value + 0.1
  if (newValue > 1) {
    newValue = 1
  }
  gainNode.gain.setValueAtTime(newValue, audioContext.currentTime);
}
