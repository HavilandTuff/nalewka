import json

from app.models import Batch, Ingredient, Liquor, User


def test_batch_formulas_pagination(client, session):
    """Test that the batch formulas endpoint returns paginated results."""
    # Create a user
    user = User(username="pagination_test_user", email="pagination_test@example.com")
    user.set_password("password123")
    session.add(user)
    session.commit()

    # Create a liquor
    liquor = Liquor(name="Test Liquor", user_id=user.id)
    session.add(liquor)
    session.commit()

    # Create ingredients
    ingredients = []
    for i in range(5):
        ingredient = Ingredient(name=f"Ingredient {i}")
        session.add(ingredient)
        ingredients.append(ingredient)
    session.commit()

    # Create a batch
    batch = Batch(description="Test Batch", liquor_id=liquor.id)
    session.add(batch)
    session.commit()

    # Create formulas
    from app.models import BatchFormula

    for i in range(15):  # Create 15 formulas
        formula = BatchFormula(
            batch_id=batch.id,
            ingredient_id=ingredients[i % len(ingredients)].id,
            quantity=100.0 + i,
            unit="ml",
        )
        session.add(formula)
    session.commit()

    # Log in the user
    response = client.post(
        "/api/v1/auth/login",
        data=json.dumps(
            {"username": "pagination_test_user", "password": "password123"}
        ),
        content_type="application/json",
    )
    assert response.status_code == 200
    data = json.loads(response.data)
    auth_token = data["auth_token"]

    # Test getting batch formulas with default pagination (page 1, 10 items)
    response = client.get(
        f"/api/v1/batches/{batch.id}/formulas",
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    assert response.status_code == 200
    data = json.loads(response.data)

    # Check that we have the paginated response structure
    assert "data" in data
    assert "pagination" in data
    assert len(data["data"]) == 10  # Default per_page is 10
    assert data["pagination"]["page"] == 1
    assert data["pagination"]["per_page"] == 10
    assert data["pagination"]["total"] == 15
    assert data["pagination"]["pages"] == 2

    # Test getting batch formulas with custom pagination (page 2, 5 items)
    response = client.get(
        f"/api/v1/batches/{batch.id}/formulas?page=2&per_page=5",
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    assert response.status_code == 200
    data = json.loads(response.data)

    # Check that we have the paginated response structure
    assert "data" in data
    assert "pagination" in data
    assert len(data["data"]) == 5
    assert data["pagination"]["page"] == 2
    assert data["pagination"]["per_page"] == 5
    assert data["pagination"]["total"] == 15
    assert data["pagination"]["pages"] == 3
