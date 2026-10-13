export function initializeCompanion() {
  /* Companion messages are chosen on request, never timed or tied to progress. */
  const thought = document.querySelector('[data-companion-thought]');
  const companion = document.querySelector('[data-companion-message]');
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
      const fox = document.querySelector('[data-companion-fox]');
      if (fox) {
        fox.src = messageIndex % 2 ? fox.dataset.cheerful : fox.dataset.curious;
        fox.alt = messageIndex % 2 ? 'Your fox companion waving beside a cup of tea' : 'Your fox companion tilting its head over a journal';
        if (typeof fox.animate === 'function' && !window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
          fox.animate([{ transform: 'rotate(0)' }, { transform: 'rotate(-3deg) translateY(-3px)' }, { transform: 'rotate(0)' }], { duration: 650, easing: 'ease-out' });
        }
      }
    });
  }
}
