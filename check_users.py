from app import create_app, db
from app.models import User

app = create_app()

with app.app_context():
    users = db.session.query(User).all()
    print("Users in the database:")
    for user in users:
        print(f"ID: {user.id}, Username: {user.username}, Email: {user.email}")
