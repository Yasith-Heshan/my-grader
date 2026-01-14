import requests

LOGIN_URL = "http://localhost:8000/api/auth/login"
ME_URL = "http://localhost:8000/api/auth/me"

creds = {"email": "teacher@example.com", "password": "teacher123", "role": "teacher"}

r = requests.post(LOGIN_URL, json=creds)
print("LOGIN STATUS", r.status_code)
print("LOGIN BODY", r.text)

if r.status_code == 200:
    token = r.json().get("token")
    headers = {"Authorization": f"Bearer {token}"}
    m = requests.get(ME_URL, headers=headers)
    print("ME STATUS", m.status_code)
    print("ME BODY", m.text)
else:
    print("Login failed; cannot call /me")
