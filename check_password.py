from werkzeug.security import check_password_hash

from app import create_app, db
from app.models import User

app = create_app()

with app.app_context():
    user = db.session.query(User).filter_by(username="formtester").first()
    if user:
        print(f"User: {user.username}")
        print(f"Email: {user.email}")
        print(f"Password hash: {user.password_hash}")
        # Check common passwords
        common_passwords = ["password123", "password", "admin", "123456", "formtester"]
        for pwd in common_passwords:
            if user.password_hash and check_password_hash(user.password_hash, pwd):
                print(f"Password is: {pwd}")
                break
        else:
            print("Could not determine password")
    else:
        print("User not found")
