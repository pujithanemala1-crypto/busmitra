/**
 * BUSMITRA - Voice Recognition Module (Web Speech API)
 * Enables speech-to-text input with feedback animations and error handling.
 */

window.BUSMITRA_VOICE = {
  recognition: null,
  isListening: false,

  init: function() {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
      console.warn("Speech Recognition API is not supported in this browser.");
      return null;
    }

    const recog = new SpeechRecognition();
    recog.continuous = false;
    recog.interimResults = true;
    recog.maxAlternatives = 1;

    // Detect language preference
    const lang = window.getCurrentLanguage ? window.getCurrentLanguage() : "en";
    const langMap = {
      en: "en-IN",
      te: "te-IN",
      hi: "hi-IN",
      ta: "ta-IN",
      kn: "kn-IN",
      ml: "ml-IN",
      bn: "bn-IN",
      mr: "mr-IN"
    };
    recog.lang = langMap[lang] || "en-IN";

    return recog;
  },

  toggleVoiceInput: function(targetInputId, micButtonId, feedbackContainerId) {
    const inputEl = document.getElementById(targetInputId);
    const micBtn = document.getElementById(micButtonId);
    const feedbackEl = document.getElementById(feedbackContainerId);

    if (this.isListening) {
      this.stop();
      return;
    }

    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
      if (feedbackEl) {
        feedbackEl.textContent = "Voice input is not supported in this browser. Please type your destination.";
        feedbackEl.className = "voice-feedback error";
        feedbackEl.style.display = "block";
      }
      if (window.showToast) window.showToast("Voice input not supported in your browser. Please type manually.");
      return;
    }

    try {
      this.recognition = this.init();
      if (!this.recognition) return;

      this.isListening = true;
      if (micBtn) micBtn.classList.add("mic-recording-pulse", "active");
      if (feedbackEl) {
        feedbackEl.innerHTML = `<span class="listening-wave"></span> Listening... Please speak your destination (e.g., "Guntur", "Mangalagiri")`;
        feedbackEl.className = "voice-feedback listening";
        feedbackEl.style.display = "flex";
      }

      this.recognition.onresult = (event) => {
        let transcript = "";
        for (let i = event.resultIndex; i < event.results.length; ++i) {
          transcript += event.results[i][0].transcript;
        }

        // Clean trailing punctuation
        const cleaned = transcript.trim().replace(/[.,!?]+$/, "");
        if (inputEl) {
          inputEl.value = cleaned;
          inputEl.dispatchEvent(new Event('input'));
        }
        if (feedbackEl) {
          feedbackEl.textContent = `Heard: "${cleaned}"`;
        }
      };

      this.recognition.onerror = (event) => {
        let errorMsg = "Voice recognition error.";
        if (event.error === 'not-allowed') {
          errorMsg = "Microphone access blocked. Please allow microphone permission in your browser.";
        } else if (event.error === 'no-speech') {
          errorMsg = "No speech detected. Please tap the mic and try again.";
        } else {
          errorMsg = `Voice error: ${event.error}`;
        }
        if (feedbackEl) {
          feedbackEl.textContent = errorMsg;
          feedbackEl.className = "voice-feedback error";
        }
        this.stop(micBtn, feedbackEl);
      };

      this.recognition.onend = () => {
        this.stop(micBtn, feedbackEl);
        if (inputEl && inputEl.value.trim() && feedbackEl) {
          feedbackEl.textContent = `Recognized: "${inputEl.value.trim()}"`;
          setTimeout(() => {
            if (feedbackEl && !this.isListening) feedbackEl.style.display = "none";
          }, 3500);
        }
      };

      this.recognition.start();
    } catch (err) {
      console.error("Failed to start voice recognition", err);
      this.stop(micBtn, feedbackEl);
    }
  },

  stop: function(micBtn, feedbackEl) {
    this.isListening = false;
    if (this.recognition) {
      try { this.recognition.stop(); } catch (e) {}
    }
    if (micBtn) micBtn.classList.remove("mic-recording-pulse", "active");
  }
};
