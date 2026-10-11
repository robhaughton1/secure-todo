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
    return render_template(
        "login.html",
        error="Invalid username or password."
    ), 400
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
I modified the login request in Burp so the username or password exceeded the application's 16 character limit

### Security reasoning
The browser is controlled by the client, so input length restrictions cannot rely only on the visible HTML form. The server should enforce the application's accepted input boundaries as well.

### Server-side control

```python
if len(username) > 16 or len(password) > 16:
    return render_template(
        "login.html",
        error="Username or password cannot exceed 16 characters."
    ), 400
```

### Retest
I submitted oversized values through Burp instead of relying on the normal browser interface.

### Result
The server rejected the request with HTTP 400 and returned the expected validation message.

**Status:** Control verified.

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
