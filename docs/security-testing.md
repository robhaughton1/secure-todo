# Security Testing Notes

This document records security-focused testing performed during development of Secure Todo.

All testing described here was performed against the application's local development instance using accounts and data created for the project. The goal is to document what was tested, what behavior was observed, what control was added or verified, and the result of retesting.

## 1. Empty Login Fields / Client-Side Validation Bypass

### What I tested
The login form uses HTML `required` attributes, but browser-side validation should not be treated as a security boundary. I intercepted the login request with Burp Suite and submitted requests with an empty username or password.

### Original concern
A normal browser prevents an empty required field from being submitted, but a user can modify the HTTP request directly and bypass that client-side check.

### Server-side control
The Flask login route checks both values after reading them from the request:

```python
if not username or not password:
    return render_template("login.html", error="Invalid username or password."), 200
```

### Retest
I resent modified requests through Burp with an empty username and an empty password.

### Result
The server rejected the requests and returned the login page with a generic error rather than continuing to the home page.

**Status:** Control verified.

---

## 2. Missing Login Parameter

### What I tested
Using Burp, I removed the `username` or `password` parameter from the POST request entirely instead of sending the parameter with an empty value.

### Original concern
Direct dictionary-style access such as:

```python
request.form["username"]
```

expects the key to exist. A malformed request with the parameter removed can cause an exception before normal validation runs.

### Fix / control
The form values are read with `.get()` and a safe default:

```python
username = request.form.get("username", "").strip()
password = request.form.get("password", "")
```

If either parameter is missing, Flask receives an empty string and the same server-side validation handles it.

### Retest
I removed the parameters again in Burp and resent the requests.

### Result
The malformed request was handled by the application's validation instead of being accepted. Internal exception details are not needed in the client response.

**Status:** Control verified.

> Development note: Flask debug mode can expose detailed tracebacks when an unhandled exception occurs, so debug mode will only be on in local development!

---

## 3. Username and Password Length Validation

### What I tested
I modified the login request in Burp so the username or password exceeded the application's original 16 character limit.

### Security reasoning
The browser is controlled by the client, so input length restrictions cannot rely only on the visible HTML form. The server should enforce the application's accepted input boundaries as well.

### Original server-side control

```python
if len(username) > 16 or len(password) > 16:
    return render_template("login.html", error="Username or password cannot exceed 16 characters."), 400
```

### Retest
I submitted oversized values through Burp instead of relying on the normal browser interface.

### Result
The server rejected the oversized values rather than processing them normally.

**Status:** Control verified for the original boundary.

### Current boundary
The username maximum remains 16 characters. The password maximum has since been increased to 32 characters and is now validated separately:

```python
if len(username) > 16:
    return render_template("login.html", error="Username cannot exceed 16 characters."), 200

if len(password) > 32:
    return render_template("login.html", error="Password cannot exceed 32 characters."), 200
```

The new 32 character password boundary should be included in the next regression test.

---

## 4. Reflected XSS / Template Escaping Check

### What I tested
I submitted the following value as the username:

```html
<script>alert("XSS test")</script>
```

The submitted username was later rendered in the home template with Jinja:

```html
{{ username }}
```

### Security reasoning
User-controlled input should not become executable HTML or JavaScript simply because it is displayed in a page.

### Result
The browser displayed the submitted script text rather than executing it. No alert appeared.

Jinja's normal template escaping prevented the value from being interpreted as a script in this context.

**Status:** Control verified.

### Important note
This test does not prove that the entire application is free of XSS. Output handling must still be reviewed anywhere user-controlled data is inserted into HTML, JavaScript, URLs, attributes, or other contexts. User-controlled values should not be marked safe unless they are intentionally trusted and handled appropriately.

---

## 5. Username Enumeration Through Response Timing

### What I tested
I sent login requests through Burp using an invalid password while alternating between a known valid username and a username that did not exist.

### Original behavior
The two cases returned the same generic error message, but their response times were very different:

- Invalid username: approximately 2-6 ms
- Valid username with an invalid password: approximately 128-130 ms

The difference was large and repeatable enough to distinguish whether a username existed.

### Root cause
The original authentication condition used short-circuit evaluation:

```python
if not user or not check_password_hash(user.password_hash, password):
    return render_template("login.html", error="Invalid username or password."), 401
```

When the username did not exist, `not user` evaluated to true and Python skipped `check_password_hash()`. When the username did exist, the application performed the intentionally expensive scrypt password verification.

This created a timing side channel even though the visible error message was generic.

### Remediation
A dummy scrypt hash is generated once when the application starts:

```python
DUMMY_HASH = generate_password_hash('random-dummy-password-hash')
```

The login path now performs one password hash verification whether or not the user exists:

```python
if not user:
    password_valid = check_password_hash(DUMMY_HASH, password)
else:
    password_valid = check_password_hash(user.password_hash, password)

if not user or not password_valid:
    return render_template("login.html", error="Invalid username or password."), 401
```

A nonexistent user still cannot authenticate because the final decision requires the user to exist. The dummy hash only makes the expensive verification work more comparable between the two paths.

### Retest
I repeated the same timing test in Burp after applying the remediation.

### Result
Observed response times after remediation:

- Valid username with an invalid password: 126 ms
- Invalid username: 133 ms

The previous large and reliable timing difference was no longer present in the retest.

**Status:** Remediated and retested.

---

## 6. Previously Issued Session Cookie Remains Valid After Logout

### What I tested
I authenticated to the local Fernward application using a test account, captured a valid Flask `session` cookie in Burp Suite, logged out using `POST /logout`, and replayed the previously captured cookie in a `GET /dashboard` request using Burp Repeater.

### Expected behavior
If logout is intended to immediately revoke the current authentication credential, replaying a cookie issued before logout should not restore access to a protected endpoint.

### Observed behavior
The normal logout response instructed the browser to delete the session cookie, including an expiration date of `Thu, 01 Jan 1970 00:00:00 GMT`. However, replaying the previously issued, unmodified signed cookie after logout returned `HTTP/1.1 200 OK` and the dashboard HTML. The expired `Set-Cookie` directive removes the browser's copy but does not revoke a captured copy on the server.

A separate tampering test changed the encoded user ID without generating a valid signature. Flask rejected that modified cookie, and the dashboard request redirected to login. **That is expected secure behavior, not a signature bypass.**

### Root cause
Fernward currently uses Flask's default client-side, cryptographically signed sessions. The server can verify the cookie's signature and age, but it does not maintain an individual server-side session record to revoke when the user logs out. `session.clear()` causes the browser to discard its cookie; it does not invalidate other copies of the previously signed cookie.

### Security impact and scope
Someone who already obtained a valid, unexpired session cookie could potentially replay it after the legitimate user logs out. This finding **does not** show that an attacker can forge a signed cookie, guess the secret key, or access another account without first obtaining a valid credential. Testing was performed on local development accounts.

### Evidence
- Burp Suite: `POST /logout` response clearing the browser cookie (observed during testing).
- Burp Suite Repeater: replay of the earlier valid cookie to `GET /dashboard`, receiving `200 OK` and dashboard HTML.
- Burp Suite: modified/invalid cookie rejected with a redirect to login (separate control verification).

#### Screenshots

**Burp interception during the session test:**

![Burp interception showing dashboard request and captured session cookie](evidence/Screenshot%202026-10-12%20174309.png)

**Replayed cookie accepted by the dashboard:**

![Burp Repeater GET dashboard with session cookie returning HTTP 200 and dashboard HTML](evidence/image%2820261012-214611%29.png)

The Repeater screenshot demonstrates that the supplied cookie was accepted. The logout-then-replay ordering was observed during manual testing; capture both requests in one sequence if independently verifiable evidence is needed.

### Planned remediation
Consider server-side session records with revocable opaque session identifiers, or a server-validated session identifier/version that can be invalidated on logout. Require authentication checks to consult revocation state. Retest that a cookie captured before logout no longer grants dashboard access afterward, while a newly authenticated session still works.

**Status:** Confirmed local session-replay behavior; remediation pending.

---

## Current Testing Approach

For security sensitive features, the development process is:

1. Build the feature.
2. Identify the trust boundary and user controlled inputs.
3. Test normal behavior in the browser.
4. Use Burp Suite to modify requests and bypass client side assumptions.
5. Observe how the server handles malformed or unexpected input.
6. Fix or strengthen the control when needed.
7. Retest the same request to verify the behavior.
8. Record meaningful findings and security decisions here.

Minor programming mistakes and ordinary development errors will not be documented as security findings unless they reveal a meaningful security behavior or lead to a security control being added
