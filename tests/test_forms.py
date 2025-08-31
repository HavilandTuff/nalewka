import pytest
import sqlalchemy as sa
from werkzeug.datastructures import MultiDict

from app.forms import (
    BatchFormulaForm,
    EditBottlesForm,
    LiquorForm,
    RegistrationForm,
)
from app.models import Ingredient, Liquor, User
from app.repositories import (
    IngredientRepository,
    LiquorRepository,
    UserRepository,
)


@pytest.fixture
def form_test_data(session):
    """Fixture to create and commit necessary data for form tests."""
    user = session.scalar(sa.select(User).where(User.username == "formtester"))
    if not user:
        user = User(username="formtester", email="formtester@test.com")
        user.set_password("password")
        session.add(user)
        session.flush()  # Flush to assign an ID to the user before creating liquor

    liquor = Liquor(name="Test Cherry Liquor", description="A test liquor.", user=user)
    session.add(liquor)  # Add liquor to session immediately
    session.flush()  # Flush to assign an ID to the liquor

    # Check if ingredients already exist, otherwise create them
    ingredient1 = session.scalar(
        sa.select(Ingredient).where(Ingredient.name == "Cherries")
    )
    if not ingredient1:
        ingredient1 = Ingredient(name="Cherries")
        session.add(ingredient1)

    ingredient2 = session.scalar(
        sa.select(Ingredient).where(Ingredient.name == "Sugar")
    )
    if not ingredient2:
        ingredient2 = Ingredient(name="Sugar")
        session.add(ingredient2)

    session.commit()
    return {"user": user, "liquor": liquor, "ingredients": [ingredient1, ingredient2]}


def test_batch_formula_form_valid_data(app, form_test_data):
    """
    GIVEN a user, liquors, and ingredients in the database
    WHEN BatchFormulaForm is instantiated with valid POST data
    THEN the form should validate successfully.
    """
    user = form_test_data["user"]
    liquor = form_test_data["liquor"]
    ingredients = form_test_data["ingredients"]

    # Simulate form data from a POST request
    form_data = MultiDict(
        [
            ("batch_description", "A great test batch"),
            ("liquor", liquor.id),
            ("bottle_count", 10),
            ("bottle_volume", 500),
            ("bottle_volume_unit", "ml"),
            ("ingredients-0-ingredient", ingredients[0].id),
            ("ingredients-0-quantity", 500.0),
            ("ingredients-0-unit", "g"),
            ("ingredients-1-ingredient", ingredients[1].id),
            ("ingredients-1-quantity", 250.0),
            ("ingredients-1-unit", "g"),
        ]
    )

    # The form must be created within an application context to access db
    with app.test_request_context():
        liquor_repository = LiquorRepository()
        ingredient_repository = IngredientRepository()
        form = BatchFormulaForm(
            user_id=user.id,
            formdata=form_data,
            liquor_repository=liquor_repository,
            ingredient_repository=ingredient_repository,
        )

        # Manually populate the FormField
        form.ingredients.process(form_data)

        for entry in form.ingredients.entries:
            entry.form.ingredient.choices = [
                (i.id, i.name) for i in ingredient_repository.get_all()
            ]

        assert form.validate() is True
        assert not form.errors


def test_batch_formula_form_missing_required_fields(app, form_test_data):
    """
    GIVEN a user and liquors in the database
    WHEN BatchFormulaForm is instantiated with missing required data
    THEN the form should fail validation with appropriate error messages.
    """
    user = form_test_data["user"]

    with app.test_request_context():
        liquor_repository = LiquorRepository()
        ingredient_repository = IngredientRepository()
        # Instantiate with empty form data
        form = BatchFormulaForm(
            user_id=user.id,
            formdata=MultiDict(),
            liquor_repository=liquor_repository,
            ingredient_repository=ingredient_repository,
        )
        for entry in form.ingredients.entries:
            entry.form.ingredient.choices = [
                (i.id, i.name) for i in ingredient_repository.get_all()
            ]
        assert form.validate() is False

        # Check for expected errors
        assert "batch_description" in form.errors
        assert "This field is required." in form.errors["batch_description"]

        assert "liquor" in form.errors
        assert "This field is required." in form.errors["liquor"]

        # The ingredients list will have an error on the first sub-form
        assert "ingredients" in form.errors


def test_batch_formula_form_invalid_quantity(app, form_test_data):
    """
    GIVEN a user and liquors in the database
    WHEN BatchFormulaForm is instantiated with an invalid ingredient quantity
    THEN the form should fail validation with a specific error message.
    """
    user = form_test_data["user"]
    with app.test_request_context():
        liquor_repository = LiquorRepository()
        ingredient_repository = IngredientRepository()
        form = BatchFormulaForm(
            user_id=user.id,
            formdata=MultiDict([("ingredients-0-quantity", -100.0)]),
            liquor_repository=liquor_repository,
            ingredient_repository=ingredient_repository,
        )
        for entry in form.ingredients.entries:
            entry.form.ingredient.choices = [
                (i.id, i.name) for i in ingredient_repository.get_all()
            ]
        assert form.validate() is False
        assert "quantity" in form.errors["ingredients"][0]
        assert (
            "Quantity must be greater than 0"
            in form.errors["ingredients"][0]["quantity"]
        )


def test_batch_formula_form_no_ingredients(app, form_test_data):
    """
    GIVEN a user and liquors in the database
    WHEN BatchFormulaForm is instantiated with no ingredients
    THEN the form should fail validation with an appropriate error message.
    """
    user = form_test_data["user"]
    liquor = form_test_data["liquor"]

    # Simulate form data from a POST request with no ingredients
    form_data = MultiDict(
        [
            ("batch_description", "A great test batch"),
            ("liquor", liquor.id),
            ("bottle_count", 10),
            ("bottle_volume", 500),
            ("bottle_volume_unit", "ml"),
        ]
    )

    with app.test_request_context():
        liquor_repository = LiquorRepository()
        ingredient_repository = IngredientRepository()
        form = BatchFormulaForm(
            user_id=user.id,
            formdata=form_data,
            liquor_repository=liquor_repository,
            ingredient_repository=ingredient_repository,
        )
        for entry in form.ingredients.entries:
            entry.form.ingredient.choices = [
                (i.id, i.name) for i in ingredient_repository.get_all()
            ]
        assert form.validate() is False
        assert "ingredients" in form.errors


def test_registration_form_valid_data(app):
    """
    GIVEN a Flask application
    WHEN a RegistrationForm is submitted with valid, unique data
    THEN the form should validate successfully.
    """
    with app.test_request_context():
        user_repository = UserRepository()
        form_data = MultiDict(
            [
                ("username", "newuser"),
                ("email", "new@example.com"),
                ("password", "a-secure-password"),
            ]
        )
        form = RegistrationForm(formdata=form_data, user_repository=user_repository)
        assert form.validate() is True


def test_registration_form_duplicate_username(app, form_test_data):
    """
    GIVEN a user already exists in the database
    WHEN a RegistrationForm is submitted with the same username
    THEN the form validation should fail with a specific error.
    """
    existing_user = form_test_data["user"]
    with app.test_request_context():
        user_repository = UserRepository()
        form_data = MultiDict(
            [
                ("username", existing_user.username),  # Duplicate username
                ("email", "another@example.com"),
                ("password", "password123"),
            ]
        )
        form = RegistrationForm(formdata=form_data, user_repository=user_repository)
        assert form.validate() is False
        assert "username" in form.errors
        assert "Username already exists" in form.errors["username"][0]


def test_registration_form_duplicate_email(app, form_test_data):
    """
    GIVEN a user already exists in the database
    WHEN a RegistrationForm is submitted with the same email
    THEN the form validation should fail with a specific error.
    """
    existing_user = form_test_data["user"]
    with app.test_request_context():
        user_repository = UserRepository()
        form_data = MultiDict(
            [
                ("username", "anotheruser"),
                ("email", existing_user.email),  # Duplicate email
                ("password", "password123"),
            ]
        )
        form = RegistrationForm(formdata=form_data, user_repository=user_repository)
        assert form.validate() is False
        assert "email" in form.errors
        assert "Email already registered" in form.errors["email"][0]


def test_liquor_form_valid(app):
    """
    GIVEN a Flask application
    WHEN a LiquorForm is submitted with valid data
    THEN the form should validate successfully.
    """
    with app.test_request_context():
        form = LiquorForm(formdata=MultiDict([("name", "My Newest Liquor")]))
        assert form.validate() is True
        assert not form.errors


def test_edit_bottles_form_invalid_range(app):
    """
    GIVEN a Flask application
    WHEN an EditBottlesForm is submitted with out-of-range data
    THEN the form validation should fail.
    """
    with app.test_request_context():
        form = EditBottlesForm(
            formdata=MultiDict([("bottle_count", -1), ("bottle_volume", 0)])
        )
        assert form.validate() is False
        assert "bottle_count" in form.errors
        assert "bottle_volume" in form.errors
