// ------------------------- WEB SOCKET INITIALISIEREN  ---------------------------------------------------

// WebSocket Kommunikation erstellen
var websocket = new WebSocket("ws://127.0.0.1:9001/");

// Event handlers für das WebSocket
websocket.onopen = function() {
  console.log("WebSocket opened");
};

websocket.onmessage = function(e) {
  // e.data enthaltet das String mit Daten
  websocketMessage(e.data);
};

websocket.onclose = function() {
  console.log("WebSocket closed");
};

websocket.onerror = function(e) {
  console.log(e)
};


// ------------------------- WEB AUDIO INITIALISIEREN ------------------------------------------------------

// Spielt synth falls true, ansonsten spielt Klavier
var isSynth = true

// WebAudio context erstellen
var audioContext = new (window.AudioContext || window.webkitAudioContext)();
var oscillatorNode = audioContext.createOscillator()
var gainNode = audioContext.createGain()
let compressor = audioContext.createDynamicsCompressor();
synth()

// Quelle für Frequenzen/Halbtöne: https://de.wikipedia.org/wiki/Frequenzen_der_gleichstufigen_Stimmung
noten =
[
  { "frequez" : "130.813", "halbton" : false, piano: "noten/key08.mp3" }, // C3
  { "frequez" : "138.591", "halbton" : true, piano: "noten/key09.mp3" } , // C#3/Db3
  { "frequez" : "146.832", "halbton" : false, piano: "noten/key10.mp3" }, // D3
  { "frequez" : "155.563", "halbton" : true, piano: "noten/key11.mp3" },  // D#3/Eb3
  { "frequez" : "164.814", "halbton" : false, piano: "noten/key12.mp3" }, // E3
  { "frequez" : "174.614", "halbton" : false, piano: "noten/key13.mp3" }, // F3
  { "frequez" : "184.997", "halbton" : true, piano: "noten/key14.mp3" },  // F#3/Gb3
  { "frequez" : "195.998", "halbton" : false, piano: "noten/key15.mp3" }, // G3
  { "frequez" : "207.652", "halbton" : true, piano: "noten/key16.mp3" },  // G#3/Ab3
  { "frequez" : "220.000", "halbton" : false, piano: "noten/key17.mp3" }, // A3
  { "frequez" : "233.082", "halbton" : true, piano: "noten/key18.mp3" },  // A#3/Bb3
  { "frequez" : "246.942", "halbton" : false, piano: "noten/key19.mp3" }  // B3
]

noten.forEach(note => {
  // finde ob eine note ein Halbton ist oder nicht
  var halbton = ((note.halbton) ? " halbton" : "")
  // erstelle die Klasse dafür
  var klasse = "class='klavier__btn basic" + halbton +  "'"
  // setze die Frequenz der Note für Synth im HTML Element
  var frequenz = "frequez='" + note.frequez + "'"
  // setze die Datei für die Klaviernote
  var piano = "piano='" + note.piano + "'"
  // die Note wird zum Element 'klavier' hinzugefügt
  document.getElementById('klavier').innerHTML += "<button onClick='klickNote(this)' " + klasse + " " + frequenz + " " + piano + "</button>"
})

// ------------------------- EVENT LISTENER --------------------------------------------------------------------

document.querySelector("#attackSlider").addEventListener("mousemove", function(e) {
  attack(this.value);
});

document.querySelector("#releaseSlider").addEventListener("mousemove", function(e) {
  release(this.value);
});

// ------------------------- FUNKTIONEN --------------------------------------------------------------------

function resetPressedElements() {
  // Finde die aktuell gedrückten Tasten und entferne die 'pressed' CSS
  var pressedElements = document.getElementsByClassName('pressed');
  // pressedElements ist eine HTMLCollection, wir müssen diese in Array konvertieren
  Array.from(pressedElements).forEach(pressedElement => pressedElement.classList.remove('pressed'))
}

// Taste wurde gedrückt
function klickNote(element) {
  // entferne CSS 'pressed' von allen Tasten
  this.resetPressedElements();

  // wir setzen die CSS 'pressed' zur gedrückten Taste
  element.classList.add('pressed')

  if (isSynth === true) {
    // Frequenz setzen für Synth
    oscillatorNode.frequency.value = parseInt(element.getAttribute('frequez'))
  } else {
    // Note setzen für Piano
    let URL = element.getAttribute('piano')
    window.fetch(URL)
    .then(response => response.arrayBuffer())
    .then(arrayBuffer => audioContext.decodeAudioData(arrayBuffer))
    .then(audioBuffer => {
      const source = audioContext.createBufferSource();
      source.buffer = audioBuffer;
      source.connect(compressor);
      compressor.connect(gainNode);
      gainNode.connect(audioContext.destination);
      source.start();
    });
  }
}

// Volume Minus
function volumeMinus() {
  var newValue = gainNode.gain.value - 0.1
  if (newValue < 0) {
    newValue = 0
  }
  gainNode.gain.setValueAtTime(newValue, audioContext.currentTime)
}

// Volume Plus
function volumePlus() {
  var newValue = gainNode.gain.value + 0.1
  if (newValue > 1) {
    newValue = 1
  }
  gainNode.gain.setValueAtTime(newValue, audioContext.currentTime)
}

// Piano
function piano() {
  isSynth = false

  // Piano Button ist disabled
  document.getElementById("piano").disabled = true;
  // Synth Button ist enabled
  document.getElementById("synth").disabled = false;

  // beende oscillator ( = synth Node)
  oscillatorNode.stop()

  // Ausgewählte Taste wieder drücken
  var pressedElements = document.getElementsByClassName('pressed');
  Array.from(pressedElements).forEach(pressedElement => klickNote(pressedElement))
}

// Synth
function synth() {
  isSynth = true

  // Piano Button ist enabled
  document.getElementById("piano").disabled = false;
  // Synth Button ist enabled
  document.getElementById("synth").disabled = true;

  oscillatorNode = audioContext.createOscillator()
  // Oscillator Node konfigurieren
  oscillatorNode.frequency.value = 0
  // sofort starten
  oscillatorNode.start(0)
  oscillatorNode.connect(compressor)
  compressor.connect(gainNode)

  // Gain Node konfigurieren
  gainNode.gain.value = 0.5
  gainNode.connect(audioContext.destination)
  
  // Ausgewählte Taste wieder drücken
  var pressedElements = document.getElementsByClassName('pressed');
  Array.from(pressedElements).forEach(pressedElement => klickNote(pressedElement))
}

// Attack
function attack(obj) {
  compressor.attack.value = (obj / 100);
  document.querySelector("#attackOutput").innerHTML = (obj / 100) + " sec";
}

// Attack
function release(obj) {
  compressor.release.value = (obj / 100);
  document.querySelector("#releaseOutput").innerHTML = (obj / 100) + " sec";
}

// Eine neue Meldung kamm über WebSocket
function websocketMessage(message) {
  console.log(message)
  const obj = JSON.parse(message)
  switch(obj.name) {
    case 'volume_minus':
      volumeMinus()
      break
    case 'volume_plus':
      volumePlus()
      break
    case 'piano':
      piano()
      break
    case 'synth':
      synth()
      break
    case 'attack':
      attack(obj)
      break
    case 'release':
      release(obj)
      break
  }
}
