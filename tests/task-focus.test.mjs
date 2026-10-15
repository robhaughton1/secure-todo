import test, { beforeEach, afterEach } from 'node:test';
import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';

// Test the real helper without a browser or a DOM dependency.
const source = await readFile(new URL('../static/js/task-focus.js', import.meta.url), 'utf8');
const { trackRequestFocus, focusConnected } = await import(`data:text/javascript,${encodeURIComponent(source)}`);
let doc, scope, input, outside, originalDocument;
const control = () => ({ isConnected: true, disabled: false, calls: 0,
  focus() { this.calls++; doc.activeElement = this; } });
const move = (target, type = 'focusin') => {
  if (type === 'focusin') doc.activeElement = target;
  const event = new Event(type);
  Object.defineProperty(event, 'target', { value: target });
  doc.dispatchEvent(event);
};
beforeEach(() => {
  originalDocument = globalThis.document;
  doc = new EventTarget();
  doc.body = control();
  input = control(); outside = control();
  scope = { contains: target => target === input };
  doc.activeElement = input;
  globalThis.document = doc;
});
afterEach(() => { globalThis.document = originalDocument; });

test('restores focus after disabling the initiating control blurs it', () => {
  const finish = trackRequestFocus(scope);
  move(doc.body);
  finish(input);
  assert.equal(input.calls, 1);
});
test('does not claim focus when the request started elsewhere', () => {
  doc.activeElement = outside;
  const finish = trackRequestFocus(scope);
  doc.activeElement = doc.body;
  finish(input);
  assert.equal(input.calls, 0);
});
test('does not steal focus after the user tabs to another control', () => {
  const finish = trackRequestFocus(scope);
  move(outside);
  finish(input);
  assert.equal(input.calls, 0);
  assert.equal(doc.activeElement, outside);
});
test('respects a click on a non-focusable area while waiting', () => {
  const finish = trackRequestFocus(scope);
  move(doc.body, 'pointerdown');
  doc.activeElement = doc.body;
  finish(input);
  assert.equal(input.calls, 0);
});
test('never focuses a disconnected or disabled target', () => {
  input.isConnected = false;
  assert.equal(focusConnected(input), false);
  input.isConnected = true; input.disabled = true;
  assert.equal(focusConnected(input), false);
  assert.equal(focusConnected(undefined), false);
  assert.equal(input.calls, 0);
});
test('confirmed deletion can hand focus to a surviving control', () => {
  doc.activeElement = doc.body;
  const finish = trackRequestFocus(scope, true);
  input.isConnected = false;
  finish(outside);
  assert.equal(outside.calls, 1);
  assert.equal(input.calls, 0);
});
test('confirmed deletion respects focus moved during the request', () => {
  const finish = trackRequestFocus(scope, true);
  move(outside);
  finish(input);
  assert.equal(input.calls, 0);
});
