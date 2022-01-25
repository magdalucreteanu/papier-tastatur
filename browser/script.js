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

var isSynth

// WebAudio context erstellen
var audioContext = new (window.AudioContext || window.webkitAudioContext)();
var oscillatorNode = audioContext.createOscillator()
var gainNode = audioContext.createGain()
gainNode.gain.value = 0.5
let convolverNode = audioContext.createConvolver();
let distortionNode = audioContext.createWaveShaper();
distortionNode.curve = makeDistortionCurve(0);
distortionNode.oversample = "4x";

loadImpulseResponse("room");
synth()


// Quelle für Frequenzen/Halbtöne: https://de.wikipedia.org/wiki/Frequenzen_der_gleichstufigen_Stimmung
noten =
[
  { "id" : "whiteKey0", "frequez" : "130.813", "halbton" : false, piano: "noten/key08.mp3" }, // C3
  { "id" : "blackKey0", "frequez" : "138.591", "halbton" : true, piano: "noten/key09.mp3" } , // C#3/Db3
  { "id" : "whiteKey1", "frequez" : "146.832", "halbton" : false, piano: "noten/key10.mp3" }, // D3
  { "id" : "blackKey1", "frequez" : "155.563", "halbton" : true, piano: "noten/key11.mp3" },  // D#3/Eb3
  { "id" : "whiteKey2", "frequez" : "164.814", "halbton" : false, piano: "noten/key12.mp3" }, // E3
  { "id" : "whiteKey3", "frequez" : "174.614", "halbton" : false, piano: "noten/key13.mp3" }, // F3
  { "id" : "blackKey2", "frequez" : "184.997", "halbton" : true, piano: "noten/key14.mp3" },  // F#3/Gb3
  { "id" : "whiteKey4", "frequez" : "195.998", "halbton" : false, piano: "noten/key15.mp3" }, // G3
  { "id" : "blackKey3", "frequez" : "207.652", "halbton" : true, piano: "noten/key16.mp3" },  // G#3/Ab3
  { "id" : "whiteKey5", "frequez" : "220.000", "halbton" : false, piano: "noten/key17.mp3" }, // A3
  { "id" : "blackKey4", "frequez" : "233.082", "halbton" : true, piano: "noten/key18.mp3" },  // A#3/Bb3
  { "id" : "whiteKey6", "frequez" : "246.942", "halbton" : false, piano: "noten/key19.mp3" }  // B3
]

noten.forEach(note => {
  // id des Buttons
  var id = note.id
  // finde ob eine note ein Halbton ist oder nicht
  var halbton = ((note.halbton) ? " halbton" : "")
  // erstelle die Klasse dafür
  var klasse = "class='klavier__btn basic" + halbton +  "'"
  // setze die Frequenz der Note für Synth im HTML Element
  var frequenz = "frequez='" + note.frequez + "'"
  // setze die Datei für die Klaviernote
  var piano = "piano='" + note.piano + "'"
  // die Note wird zum Element 'klavier' hinzugefügt
  document.getElementById('klavier').innerHTML += "<button id='" + id + "' onClick='klickNote(this)' " + klasse + " " + frequenz + " " + piano + "</button>"
})

// ------------------------- EVENT LISTENER --------------------------------------------------------------------

document.querySelector("#distortionSlider").addEventListener("mousemove", function(e) {
  distortion(this.value);
});

// ------------------------- FUNKTIONEN --------------------------------------------------------------------

function loadImpulseResponse(name) {
  // Buttons enablen
  document.getElementById("cave").disabled = false
  document.getElementById("church").disabled = false
  document.getElementById("garage").disabled = false
  document.getElementById("room").disabled = false

  // Den aktiven Button disablen
  document.getElementById(name).disabled = true

  // Reverb laden
  var request = new XMLHttpRequest()
  request.open("GET",  ("/impulseResponses/" + name + ".wav"), true)
  request.responseType = "arraybuffer"

  request.onload = function () {
      var undecodedAudio = request.response
      audioContext.decodeAudioData(undecodedAudio, function (buffer) {
          if (convolverNode) {convolverNode.disconnect() }
          convolverNode = audioContext.createConvolver()
          convolverNode.buffer = buffer
          convolverNode.normalize = true

          gainNode.connect(convolverNode)
          convolverNode.connect(audioContext.destination)
      })
  }
  request.send()
}

function makeDistortionCurve(amount) {
  document.getElementById("distortionOutput").innerHTML = amount
  document.getElementById("distortionSlider").value = amount

  var n_samples = 44100,
      curve = new Float32Array(n_samples)

  var test = []

  for (i = 0; i < n_samples; i++ ) {
      var x = i * 2 / n_samples - 1
      curve[i] = (Math.PI + amount) * x / (Math.PI + (amount * Math.abs(x)))
  }

  return curve
};

function resetPressedElements() {
  // Finde die aktuell gedrückten Tasten und entferne die 'pressed' CSS
  var pressedElements = document.getElementsByClassName('pressed')
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
      source.connect(distortionNode);
      distortionNode.connect(gainNode)
      //gainNode.connect(convolverNode)
      //convolverNode(audioContext.destination);
      gainNode.connect(audioContext.destination)
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
  if (isSynth === false) {
    return
  }

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
  if (isSynth === true) {
    return
  }

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
  oscillatorNode.connect(distortionNode)
  distortionNode.connect(gainNode)

  // Gain Node konfigurieren
  gainNode.connect(convolverNode)
  convolverNode.connect(audioContext.destination)
  
  // Ausgewählte Taste wieder drücken
  var pressedElements = document.getElementsByClassName('pressed')
  Array.from(pressedElements).forEach(pressedElement => klickNote(pressedElement))
}

// BlackKey
function blackKey(obj) {
  var pressedElement = document.getElementById('blackKey' + obj.index)
  klickNote(pressedElement)
}

// WhiteKey
function whiteKey(obj) {
  var pressedElement = document.getElementById('whiteKey' + obj.index)
  klickNote(pressedElement)
}

// Distortion
function distortion(obj) {
  distortionNode.curve = makeDistortionCurve(obj)
}

// Reverb
function reverb(obj) {
  let index = obj.index
  if (index === 0) {
    cave()
  } else if (index === 1) {
    church()
  } else if (index === 2) {
    garage()
  } else if (index === 3) {
    room()
  }
}

// Cave
function cave() {
  loadImpulseResponse('cave')
}

// Church
function church() {
  loadImpulseResponse('church')
}

// Garage
function garage() {
  loadImpulseResponse('garage')
}

// Room
function room() {
  loadImpulseResponse('room')
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
    case 'whiteKey':
      whiteKey(obj)
      break
    case 'blackKey':
      blackKey(obj)
      break
    case 'distortion':
      distortion(obj.value)
      break
    case 'reverb':
      reverb(obj)
      break
  }
}
