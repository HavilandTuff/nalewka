from typing import Any

from app.models import Liquor, User


def test_new_user_password_hashing(session: Any) -> None:
    """
    GIVEN a User model
    WHEN a new User is created
    THEN check the username, email, and password fields are defined correctly
    """
    # Check if user already exists to avoid conflicts
    existing_user = session.query(User).filter_by(username="testuser").first()
    if existing_user:
        # Also delete any associated liquors to avoid foreign key constraints
        liquors = session.query(Liquor).filter_by(user_id=existing_user.id).all()
        for liquor in liquors:
            session.delete(liquor)
        session.delete(existing_user)
        session.commit()

    user = User(username="testuser", email="unique_test@example.com")
    user.set_password("password123")

    session.add(user)
    session.commit()

    assert user.id is not None
    assert user.password_hash != "password123"
    assert user.check_password("password123")
    assert not user.check_password("wrongpassword")
