from flask import url_for

from app.models import Batch, BatchFormula, Ingredient, Liquor, User


def test_batch_details_page(client, session):
    """Test that the batch details page loads correctly."""
    # Create a user
    user = User(username="batchdetailsuser", email="batchdetails@example.com")
    user.set_password("password123")
    session.add(user)
    session.commit()

    # Create a liquor
    liquor = Liquor(name="Test Liquor", description="A test liquor", user_id=user.id)
    session.add(liquor)
    session.commit()

    # Create an ingredient
    ingredient = Ingredient(name="Test Ingredient", description="A test ingredient")
    session.add(ingredient)
    session.commit()

    # Create a batch with formulas
    batch = Batch(description="Test batch for details", liquor_id=liquor.id)
    session.add(batch)
    session.commit()

    # Add a formula to the batch
    formula = BatchFormula(
        batch_id=batch.id, ingredient_id=ingredient.id, quantity=100.0, unit="ml"
    )
    session.add(formula)
    session.commit()

    # Log in the user
    with client.session_transaction() as sess:
        # Flask-Login uses a special session key to track user ID
        sess["_user_id"] = str(user.id)
        sess["_fresh"] = True

    # Test accessing the batch details page
    with client.application.test_request_context():
        response = client.get(url_for("main.batch_details", batch_id=batch.id))

    # Check that the response is successful
    assert response.status_code == 200
    assert b"Batch Details" in response.data
    assert b"Test batch for details" in response.data
    assert b"Test Ingredient" in response.data
    assert b"100.0" in response.data
    assert b"ml" in response.data


def test_batch_details_page_not_found(client, session):
    """Test that accessing a non-existent batch shows an error."""
    # Create a user
    user = User(username="batchdetailsuser2", email="batchdetails2@example.com")
    user.set_password("password123")
    session.add(user)
    session.commit()

    # Log in the user
    with client.session_transaction() as sess:
        sess["_user_id"] = str(user.id)
        sess["_fresh"] = True

    # Try to access a non-existent batch
    with client.application.test_request_context():
        response = client.get(url_for("main.batch_details", batch_id=999))

    # Should redirect to index with an error message
    assert response.status_code == 302


def test_batch_details_page_unauthorized(client, session):
    """Test that unauthorized users cannot access batch details."""
    # Create users
    user1 = User(username="batchdetailsuser1", email="batchdetails1@example.com")
    user1.set_password("password123")
    session.add(user1)
    session.commit()

    user2 = User(username="batchdetailsuser3", email="batchdetails3@example.com")
    user2.set_password("password123")
    session.add(user2)
    session.commit()

    # Create a liquor and batch for user1
    liquor = Liquor(
        name="Other Liquor", description="Another test liquor", user_id=user1.id
    )
    session.add(liquor)
    session.commit()

    batch = Batch(description="Other batch", liquor_id=liquor.id)
    session.add(batch)
    session.commit()

    # Try to access without logging in
    with client.application.test_request_context():
        response = client.get(url_for("main.batch_details", batch_id=batch.id))

    # Should redirect to login page
    assert response.status_code == 302

    # Log in as a different user (not the owner)
    with client.session_transaction() as sess:
        sess["_user_id"] = str(user2.id)  # Different user
        sess["_fresh"] = True

    # Try to access the batch details page
    with client.application.test_request_context():
        response = client.get(url_for("main.batch_details", batch_id=batch.id))

    # Should redirect to index with an error message
    assert response.status_code == 302
