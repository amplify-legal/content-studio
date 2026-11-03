/* Closed-form damped springs, used as GSAP eases.
   Method: https://github.com/Kimeur/motion-launch-videos, shared/reference/springs.md (MIT), and the
   "Springs - make motion feel expensive" step of a public motion course (2026-09-27).
   A spring with damping ratio z and natural frequency w is a pure function of time,
   so a seek to any frame is exact. The tween's duration is the settle time
   (16 / (z * w)), where the residual is under 2e-6 of the move and the ease snaps to 1.
   This file lives beside the looks pages (looks.html, anim_looks.html, tutorial.html), which load it from this
   folder; content/taste/motion-craft.md says which spring goes where. */
(function () {
  function make(z, w) {
    var settle = 16 / (z * w);
    var wd = z < 1 ? w * Math.sqrt(1 - z * z) : 0;
    function S(t) {
      if (t <= 0) return 0;
      if (t >= settle) return 1;
      if (z < 1) return 1 - Math.exp(-z * w * t) * (Math.cos(wd * t) + (z * w / wd) * Math.sin(wd * t));
      return 1 - (1 + w * t) * Math.exp(-w * t);
    }
    return { z: z, w: w, dur: settle, S: S, ease: function (p) { return S(p * settle); } };
  }
  // House set. Entrances may overshoot a hair, exits and opacity never do,
  // type never visibly overshoots (the course's step 08: "Tiny overshoot on UI, none on type").
  window.SPR = {
    make: make,
    TYPE: make(0.9, 16),   // lands ~0.39 s, overshoot 0.15 %
    UI: make(0.78, 14),    // lands ~0.28 s, overshoot ~2 %
    CARD: make(0.85, 10),  // lands ~0.49 s, overshoot 0.6 %: containers, travel
    FADE: make(1, 22),     // critically damped, 95 % at ~0.22 s
    EXIT: make(1, 18),     // no bounce on the way out
    MASK: make(1, 19.5)    // wipes
  };
  // tween helper: fromTo with the spring as ease and its settle time as duration
  window.spr = function (tl, target, from, to, spring, at) {
    var vars = Object.assign({}, to, { duration: spring.dur, ease: spring.ease, immediateRender: false });
    return tl.fromTo(target, from, vars, at);
  };
})();
