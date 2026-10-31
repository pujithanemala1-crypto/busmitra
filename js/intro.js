/**
 * BUSMITRA - Cinematic Road Bus Animation & Logo Reveal (GSAP Powered)
 * Orchestrates realistic road transit animation, sound synthesis, logo reveal and smooth page transition.
 */

window.BUSMITRA_INTRO = {
  soundEnabled: false,
  audioCtx: null,
  engineOscillator: null,
  timeline: null,

  init: function() {
    const stage = document.getElementById("intro-stage");
    if (!stage) return;

    this.setupAudioToggle();
    this.setupSkipButton();
    this.runAnimationSequence();
  },

  setupAudioToggle: function() {
    const audioBtn = document.getElementById("intro-sound-toggle");
    if (!audioBtn) return;

    audioBtn.addEventListener("click", () => {
      this.soundEnabled = !this.soundEnabled;
      if (this.soundEnabled) {
        this.startEngineAudio();
        audioBtn.innerHTML = `
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"/><path d="M19.07 4.93a10 10 0 0 1 0 14.14M15.54 8.46a5 5 0 0 1 0 7.07"/></svg>
          <span>Sound ON</span>
        `;
        audioBtn.style.borderColor = "#06B6D4";
      } else {
        this.stopEngineAudio();
        audioBtn.innerHTML = `
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"/><line x1="23" y1="9" x2="17" y2="15"/><line x1="17" y1="9" x2="23" y2="15"/></svg>
          <span>Sound OFF</span>
        `;
        audioBtn.style.borderColor = "rgba(255,255,255,0.2)";
      }
    });
  },

  setupSkipButton: function() {
    const skipBtn = document.getElementById("skip-intro-btn");
    if (skipBtn) {
      skipBtn.addEventListener("click", () => {
        this.stopEngineAudio();
        this.transitionToNextPage();
      });
    }
  },

  // Web Audio API engine purr synthesis without requiring external audio assets
  startEngineAudio: function() {
    try {
      const AudioContext = window.AudioContext || window.webkitAudioContext;
      if (!AudioContext) return;
      this.audioCtx = new AudioContext();

      const osc = this.audioCtx.createOscillator();
      const gain = this.audioCtx.createGain();

      osc.type = "sawtooth";
      osc.frequency.setValueAtTime(65, this.audioCtx.currentTime); // Low engine diesel hum
      gain.gain.setValueAtTime(0.08, this.audioCtx.currentTime);

      osc.connect(gain);
      gain.connect(this.audioCtx.destination);
      osc.start();
      this.engineOscillator = osc;
    } catch (e) {
      console.warn("Audio context could not start", e);
    }
  },

  stopEngineAudio: function() {
    if (this.engineOscillator) {
      try { this.engineOscillator.stop(); } catch (e) {}
      this.engineOscillator = null;
    }
    if (this.audioCtx) {
      try { this.audioCtx.close(); } catch (e) {}
      this.audioCtx = null;
    }
  },

  runAnimationSequence: function() {
    const busActor = document.getElementById("bus-actor");
    const logoStage = document.getElementById("logo-reveal-stage");
    const roadMarkings = document.getElementById("road-markings");

    if (typeof gsap === 'undefined') {
      // Fallback if GSAP is still loading
      setTimeout(() => this.transitionToNextPage(), 4500);
      return;
    }

    const windowWidth = window.innerWidth;
    const busTravelDistance = windowWidth + 600;

    this.timeline = gsap.timeline({
      onComplete: () => {
        this.stopEngineAudio();
        // Wait 1.8 seconds after logo reveal, then transition
        setTimeout(() => this.transitionToNextPage(), 1800);
      }
    });

    // 1. Bus accelerates from offscreen left (-480px) and drives smoothly across to offscreen right
    this.timeline.fromTo(
      busActor,
      { x: -500 },
      {
        x: busTravelDistance,
        duration: 4.5,
        ease: "power1.inOut"
      }
    );

    // 2. Road markings velocity acceleration
    this.timeline.to(
      roadMarkings,
      {
        opacity: 1,
        duration: 0.5
      },
      0
    );

    // 3. Once bus exits the screen, trigger dramatic Logo Reveal
    this.timeline.to(
      logoStage,
      {
        opacity: 1,
        duration: 0.8,
        ease: "power2.out",
        onStart: () => {
          logoStage.classList.add("active");
        }
      },
      "-=0.6"
    );

    // 4. Stagger logo badge and typography
    this.timeline.from(
      ".logo-big-badge",
      {
        scale: 0.5,
        rotation: -10,
        opacity: 0,
        duration: 0.8,
        ease: "back.out(1.7)"
      },
      "-=0.4"
    );

    this.timeline.from(
      ".logo-big-title",
      {
        y: 20,
        opacity: 0,
        duration: 0.6,
        ease: "power2.out"
      },
      "-=0.5"
    );

    this.timeline.from(
      ".logo-tagline",
      {
        y: 15,
        opacity: 0,
        duration: 0.5,
        ease: "power2.out"
      },
      "-=0.3"
    );

    this.timeline.from(
      "#logo-continue-btn",
      {
        y: 10,
        opacity: 0,
        duration: 0.4,
        ease: "power2.out"
      },
      "-=0.2"
    );
  },

  transitionToNextPage: function() {
    // If language already selected previously, user can go straight to home.html or language.html
    const hasSelectedLang = localStorage.getItem("busmitra_lang");
    if (hasSelectedLang) {
      window.location.href = "home.html";
    } else {
      window.location.href = "language.html";
    }
  }
};

document.addEventListener("DOMContentLoaded", function() {
  if (document.getElementById("intro-stage")) {
    window.BUSMITRA_INTRO.init();
  }
});
