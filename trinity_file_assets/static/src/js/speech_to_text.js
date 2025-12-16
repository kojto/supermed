// Wrap in IIFE to prevent global variable conflicts
(function() {
  'use strict';

  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SpeechRecognition) {
    alert("Вашият браузър не поддържа разпознаване на реч. Опитайте с Chrome или Edge.");
    return;
  }

  const recognition = new SpeechRecognition();
  recognition.continuous = true;
  recognition.interimResults = true;
  recognition.lang = 'bg-BG';

  let isListening = false;
  let currentTextInput = null;
  let finalTranscripts = new Map();

  document.querySelectorAll('.mic-button').forEach(micButton => {
    const fieldId = micButton.id.replace('micButton_', '');
    const textInput = document.getElementById(fieldId);
    if (textInput) {
      finalTranscripts.set(fieldId, textInput.value || '');
      micButton.addEventListener('click', () => {
        if (!isListening) {
          currentTextInput = textInput;
          recognition.start();
          micButton.classList.add('listening');
          micButton.innerHTML = '<i class="fa fa-circle text-danger"></i>';
          isListening = true;
        } else {
          recognition.stop();
          micButton.classList.remove('listening');
          micButton.innerHTML = '<i class="fa fa-microphone"></i>';
          isListening = false;
          currentTextInput = null;
        }
      });
    }
  });

  recognition.onresult = (event) => {
    if (!currentTextInput) return;
    const fieldId = currentTextInput.id;
    let interimTranscript = '';
    for (let i = event.resultIndex; i < event.results.length; i++) {
      const transcript = event.results[i][0].transcript;
      if (event.results[i].isFinal) {
        finalTranscripts.set(fieldId, finalTranscripts.get(fieldId) + transcript + ' ');
      } else {
        interimTranscript += transcript;
      }
    }
    currentTextInput.value = finalTranscripts.get(fieldId) + interimTranscript;
  };

  recognition.onerror = (event) => {
    console.error('Грешка при разпознаване на реч:', event.error);
    document.querySelectorAll('.mic-button.listening').forEach(button => {
      button.classList.remove('listening');
      button.innerHTML = '<i class="fa fa-microphone"></i>';
    });
    isListening = false;
    currentTextInput = null;
    if (event.error === 'no-speech') {
      alert('Не е открита реч. Моля, опитайте отново.');
    } else if (event.error === 'not-allowed') {
      alert('Достъпът до микрофона е отказан. Моля, разрешете достъп до микрофона.');
    }
  };

  recognition.onend = () => {
    if (isListening && currentTextInput) {
      recognition.start();
    } else {
      document.querySelectorAll('.mic-button.listening').forEach(button => {
        button.classList.remove('listening');
        button.innerHTML = '<i class="fa fa-microphone"></i>';
      });
      isListening = false;
      currentTextInput = null;
    }
  };
})();
