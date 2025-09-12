import json

from app.models import Batch, Ingredient, Liquor, User


def test_batch_formulas_api(client, session):
    """Test the batch formulas API endpoints."""
    # Check if user already exists to avoid conflicts
    existing_user = session.query(User).filter_by(username="testuser_formulas").first()
    if existing_user:
        # Delete any associated data to avoid foreign key constraints
        batches = (
            session.query(Batch).join(Liquor).filter_by(user_id=existing_user.id).all()
        )
        for batch in batches:
            # Delete formulas first due to foreign key constraints
            for formula in batch.formulas:
                session.delete(formula)
            session.delete(batch)

        liquors = session.query(Liquor).filter_by(user_id=existing_user.id).all()
        for liquor in liquors:
            session.delete(liquor)

        session.delete(existing_user)
        session.commit()

    # Check if ingredients already exist
    ingredient1 = session.query(Ingredient).filter_by(name="Ingredient 1").first()
    if ingredient1:
        session.delete(ingredient1)

    ingredient2 = session.query(Ingredient).filter_by(name="Ingredient 2").first()
    if ingredient2:
        session.delete(ingredient2)

    session.commit()

    # Create a user
    user = User(username="testuser_formulas", email="test_formulas@example.com")
    user.set_password("password123")
    session.add(user)
    session.commit()

    # Create a liquor
    liquor = Liquor(name="Test Liquor", user_id=user.id)
    session.add(liquor)
    session.commit()

    # Create ingredients
    ingredient1 = Ingredient(name="Ingredient 1")
    ingredient2 = Ingredient(name="Ingredient 2")
    session.add_all([ingredient1, ingredient2])
    session.commit()

    # Create a batch
    batch = Batch(description="Test Batch", liquor_id=liquor.id)
    session.add(batch)
    session.commit()

    # Log in the user
    response = client.post(
        "/api/v1/auth/login",
        data=json.dumps({"username": "testuser_formulas", "password": "password123"}),
        content_type="application/json",
    )
    assert response.status_code == 200
    data = json.loads(response.data)
    auth_token = data["auth_token"]

    # Test creating a batch formula
    response = client.post(
        f"/api/v1/batches/{batch.id}/formulas",
        data=json.dumps(
            {
                "ingredient_id": ingredient1.id,
                "quantity": 100.0,
                "unit": "ml",
            }
        ),
        content_type="application/json",
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    assert response.status_code == 201
    data = json.loads(response.data)
    assert data["ingredient_id"] == ingredient1.id
    assert data["quantity"] == 100.0
    assert data["unit"] == "ml"
    formula_id = data["id"]

    # Test getting batch formulas
    response = client.get(
        f"/api/v1/batches/{batch.id}/formulas",
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data) == 1
    assert data[0]["id"] == formula_id
    assert data[0]["ingredient_id"] == ingredient1.id
    assert data[0]["ingredient_name"] == "Ingredient 1"
    assert data[0]["quantity"] == 100.0
    assert data[0]["unit"] == "ml"

    # Test updating a batch formula
    response = client.put(
        f"/api/v1/formulas/{formula_id}",
        data=json.dumps(
            {
                "ingredient_id": ingredient2.id,
                "quantity": 200.0,
                "unit": "g",
            }
        ),
        content_type="application/json",
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["id"] == formula_id
    assert data["ingredient_id"] == ingredient2.id
    assert data["ingredient_name"] == "Ingredient 2"
    assert data["quantity"] == 200.0
    assert data["unit"] == "g"

    # Test deleting a batch formula
    response = client.delete(
        f"/api/v1/formulas/{formula_id}",
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    assert response.status_code == 204

    # Verify formula was deleted
    response = client.get(
        f"/api/v1/batches/{batch.id}/formulas",
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data) == 0
