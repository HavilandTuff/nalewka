from app import create_app, db
from app.models import Batch, BatchFormula, Ingredient, Liquor, User

app = create_app()


def create_test_data():
    with app.app_context():
        # Create a user
        user = User(username="testuser", email="test@example.com")
        user.set_password("password123")
        db.session.add(user)
        db.session.commit()

        # Create a liquor
        liquor = Liquor(name="Test Liquor", user_id=user.id)
        db.session.add(liquor)
        db.session.commit()

        # Create ingredients
        ingredients = []
        for i in range(25):
            ingredient = Ingredient(
                name=f"Ingredient {i}", description=f"Description for ingredient {i}"
            )
            db.session.add(ingredient)
            ingredients.append(ingredient)
        db.session.commit()

        # Create a batch
        batch = Batch(description="Test Batch", liquor_id=liquor.id)
        db.session.add(batch)
        db.session.commit()

        # Create formulas
        for i in range(25):
            formula = BatchFormula(
                batch_id=batch.id,
                ingredient_id=ingredients[i].id,
                quantity=100.0 + i,
                unit="ml",
            )
            db.session.add(formula)
        db.session.commit()

        print("Test data created successfully!")


if __name__ == "__main__":
    create_test_data()
