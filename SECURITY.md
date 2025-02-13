# Security Policy

## Supported Versions

We actively support the latest major and minor releases of this Django application. Security patches and updates are provided for:

| Version | Supported       |
| ------- | --------------- |
| 1.x.x   | ❌ Not Supported |
| 2.x.x   | ✅ Supported     |
| 3.x.x   | ✅ Supported     |

If you are using an older version, we strongly recommend upgrading to a supported release.

## Reporting a Vulnerability

If you discover a security vulnerability in this application, please **do not disclose it publicly**. Instead, follow these steps:

1. **Email the security team** at [security@example.com](mailto\:security@example.com) with details of the vulnerability.
2. **Provide steps to reproduce** the issue, including any necessary code snippets or configurations.
3. **Wait for our response**—we will acknowledge receipt of the report within 48 hours.
4. **Allow time for a fix**—we aim to address critical vulnerabilities within 7-14 days.

We appreciate responsible disclosure and may publicly acknowledge contributors who report valid security issues.

## Security Best Practices

To keep your Django application secure, follow these best practices:

### 1. Keep Dependencies Updated

- Regularly update Django and third-party libraries using:
  ```bash
  pip install --upgrade django
  pip list --outdated
  ```
- Use [pip-audit](https://pypi.org/project/pip-audit/) to check for vulnerable dependencies:
  ```bash
  pip install pip-audit
  pip-audit
  ```

### 2. Use Environment Variables for Secrets

- Never store sensitive data (e.g., `SECRET_KEY`, database passwords) in source code.
- Use environment variables and `django-environ` for configuration:
  ```python
  import environ
  env = environ.Env()
  SECRET_KEY = env('DJANGO_SECRET_KEY')
  ```

### 3. Enable Security Middleware

Ensure these security middleware settings are enabled in `settings.py`:

```python
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True
SECURE_SSL_REDIRECT = True
```

### 4. Use Strong Authentication & Authorization

- Enforce strong passwords with Django’s built-in validators:
  ```python
  AUTH_PASSWORD_VALIDATORS = [
      {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
      {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
      {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
  ]
  ```
- Use Django's built-in authentication features like `django.contrib.auth` and [Django REST Framework JWT Authentication](https://django-rest-framework-simplejwt.readthedocs.io/en/latest/).

### 5. Perform Regular Security Audits

- Run Django security checks:
  ```bash
  python manage.py check --deploy
  ```
- Use `bandit` for static security analysis:
  ```bash
  pip install bandit
  bandit -r .
  ```
- Use automated tools like OWASP ZAP for penetration testing.

## Responsible Disclosure Policy

We encourage security researchers to test our application in accordance with ethical hacking guidelines. Please adhere to the following:

- Do not exploit vulnerabilities beyond necessary testing.
- Do not publicly disclose vulnerabilities before an official patch is released.
- Do not test on live production data; use test environments instead.

## Contact Information

For any security concerns, please reach out to our security team at:

- **Email:** [security@stemgon.com](mailto\:security@stemgon.com)
- **Website:** [https://stemgon.com/security](https://stemgon.com/security)

Thank you for helping us keep this Django application secure! 🔒

