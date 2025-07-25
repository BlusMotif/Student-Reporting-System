from werkzeug.security import generate_password_hash

# In-memory user store: username -> {password_hash, role}
users = {
    "admin": {
        "password": generate_password_hash("adminpass"),
        "role": "admin"
    }
}
