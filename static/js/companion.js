export function initializeCompanion() {
  /* Companion messages are chosen on request, never timed or tied to progress. */
  const thought = document.querySelector('[data-companion-thought]');
  const companion = document.querySelector('[data-companion-message]');
  const fox = document.querySelector('[data-companion-fox]');
  const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
  let reaction;
  if (thought && companion) {
    const messages = [
      'I’ll keep you company.',
      'Take a break when you need one.',
      'Tea first, or a fresh page?',
      'Keep a note for later.'
    ];
    let messageIndex = 0;
    thought.hidden = false;
    thought.addEventListener('click', () => {
      messageIndex = (messageIndex + 1) % messages.length;
      companion.textContent = messages[messageIndex];
      if (fox) {
        fox.src = messageIndex % 2 ? fox.dataset.cheerful : fox.dataset.curious;
        fox.alt = messageIndex % 2 ? 'Your fox companion waving beside a cup of tea' : 'Your fox companion tilting its head over a journal';
        reaction?.cancel();
        if (typeof fox.animate === 'function' && !reducedMotion.matches) {
          reaction = fox.animate([{ transform: 'rotate(0)' }, { transform: 'rotate(-3deg) translateY(-3px)' }, { transform: 'rotate(0)' }], { duration: 650, easing: 'ease-out' });
        }
      }
    });
    reducedMotion.addEventListener('change', event => { if (event.matches) reaction?.cancel(); });
  }
}
