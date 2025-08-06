from app.models import User

def test_new_user_password_hashing(session):
    """
    GIVEN a User model
    WHEN a new User is created
    THEN check the username, email, and password fields are defined correctly
    """
    user = User(username='testuser', email='test@example.com')
    user.set_password('password123')
    
    session.add(user)
    session.commit()

    assert user.id is not None
    assert user.password_hash != 'password123'
    assert user.check_password('password123')
    assert not user.check_password('wrongpassword')