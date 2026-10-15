/* Retain focus only while a pending request still owns the user's attention. */
export function focusConnected(control) {
  if (!control?.isConnected || control.disabled) return false;
  control.focus();
  return true;
}

export function trackRequestFocus(scope, owned = scope.contains(document.activeElement)) {
  const movedOutside = event => {
    // Disabling a focused control can temporarily move focus to the body.
    if (event.type === 'focusin' && event.target === document.body) return;
    if (!scope.contains(event.target)) owned = false;
  };
  document.addEventListener('focusin', movedOutside);
  document.addEventListener('pointerdown', movedOutside);
  return control => {
    document.removeEventListener('focusin', movedOutside);
    document.removeEventListener('pointerdown', movedOutside);
    if (owned && (document.activeElement === document.body || scope.contains(document.activeElement))) {
      focusConnected(control);
    }
  };
}
