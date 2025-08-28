import pytest
from werkzeug.datastructures import MultiDict

from app.forms import (
    BatchFormulaForm,
    EditBottlesForm,
    LiquorForm,
    RegistrationForm,
)
from app.models import Ingredient, Liquor, User


@pytest.fixture
def form_test_data(session):
    """Fixture to create and commit necessary data for form tests."""
    user = User(username="formtester", email="formtester@test.com")
    user.set_password("password")

    liquor = Liquor(name="Test Cherry Liquor", description="A test liquor.", user=user)

    ingredient1 = Ingredient(name="Cherries")
    ingredient2 = Ingredient(name="Sugar")

    session.add_all([user, liquor, ingredient1, ingredient2])
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
            ("ingredients-0-ingredient_id", ingredients[0].id),
            ("ingredients-0-quantity", 500.0),
            ("ingredients-0-unit", "grams"),
            ("ingredients-1-ingredient_id", ingredients[1].id),
            ("ingredients-1-quantity", 250.0),
            ("ingredients-1-unit", "grams"),
        ]
    )

    # The form must be created within an application context to access db
    with app.test_request_context():
        form = BatchFormulaForm(user=user, formdata=form_data)
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
        # Instantiate with empty form data
        form = BatchFormulaForm(user=user, formdata=MultiDict())
        assert form.validate() is False

        # Check for expected errors
        assert "batch_description" in form.errors
        assert "This field is required." in form.errors["batch_description"]

        assert "liquor" in form.errors
        assert "Please select a liquor." in form.errors["liquor"]

        # The ingredients list will have an error on the first sub-form
        assert "ingredients" in form.errors
        assert "ingredient_id" in form.errors["ingredients"][0]


def test_batch_formula_form_invalid_quantity(app, form_test_data):
    """
    GIVEN a user and liquors in the database
    WHEN BatchFormulaForm is instantiated with an invalid ingredient quantity
    THEN the form should fail validation with a specific error message.
    """
    user = form_test_data["user"]
    with app.test_request_context():
        form = BatchFormulaForm(
            user=user, formdata=MultiDict([("ingredients-0-quantity", -100.0)])
        )
        assert form.validate() is False
        assert "quantity" in form.errors["ingredients"][0]
        assert "Quantity must be positive." in form.errors["ingredients"][0]["quantity"]


def test_registration_form_valid_data(app):
    """
    GIVEN a Flask application
    WHEN a RegistrationForm is submitted with valid, unique data
    THEN the form should validate successfully.
    """
    with app.test_request_context():
        form_data = MultiDict(
            [
                ("username", "newuser"),
                ("email", "new@example.com"),
                ("password", "a-secure-password"),
            ]
        )
        form = RegistrationForm(formdata=form_data)
        assert form.validate() is True


def test_registration_form_duplicate_username(app, form_test_data):
    """
    GIVEN a user already exists in the database
    WHEN a RegistrationForm is submitted with the same username
    THEN the form validation should fail with a specific error.
    """
    existing_user = form_test_data["user"]
    with app.test_request_context():
        form_data = MultiDict(
            [
                ("username", existing_user.username),  # Duplicate username
                ("email", "another@example.com"),
                ("password", "password123"),
            ]
        )
        form = RegistrationForm(formdata=form_data)
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
        form_data = MultiDict(
            [
                ("username", "anotheruser"),
                ("email", existing_user.email),  # Duplicate email
                ("password", "password123"),
            ]
        )
        form = RegistrationForm(formdata=form_data)
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
