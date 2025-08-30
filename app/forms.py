from flask_wtf import FlaskForm
from wtforms import (
    BooleanField,
    FieldList,
    FloatField,
    FormField,
    IntegerField,
    PasswordField,
    SelectField,
    StringField,
    SubmitField,
    TextAreaField,
)
from wtforms.validators import DataRequired, Email, Length, NumberRange, ValidationError


class LoginForm(FlaskForm):
    username = StringField(
        "Username", validators=[DataRequired(), Length(min=3, max=64)]
    )
    password = PasswordField("Password", validators=[DataRequired(), Length(min=6)])
    remember_me = BooleanField("Remember Me")
    submit = SubmitField("Sign In")


class RegistrationForm(FlaskForm):
    username = StringField(
        "Username",
        validators=[
            DataRequired(),
            Length(
                min=3, max=64, message="Username must be between 3 and 64 characters"
            ),
        ],
    )
    email = StringField(
        "Email",
        validators=[
            DataRequired(),
            Email(message="Please enter a valid email address"),
        ],
    )
    password = PasswordField(
        "Password",
        validators=[
            DataRequired(),
            Length(min=6, message="Password must be at least 6 characters long"),
        ],
    )
    submit = SubmitField("Register")

    def __init__(self, *args, user_repository, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        self.user_repository = user_repository

    def validate_username(self, username):
        if self.user_repository.get_by_username(username.data):
            raise ValidationError(
                "Username already exists. Please choose a different one."
            )

    def validate_email(self, email):
        if self.user_repository.get_by_email(email.data):
            raise ValidationError(
                "Email already registered. Please use a different email."
            )


class LiquorForm(FlaskForm):
    name = StringField(
        "Liquor Name", validators=[DataRequired(), Length(min=2, max=128)]
    )
    description = TextAreaField("Description", validators=[Length(max=1000)])
    submit = SubmitField("Create Liquor")


class IngredientEntryForm(FlaskForm):
    ingredient = SelectField("Ingredient", coerce=int, validators=[DataRequired()])
    quantity = FloatField(
        "Quantity",
        validators=[
            DataRequired(),
            NumberRange(min=0.01, message="Quantity must be greater than 0"),
        ],
    )
    unit = SelectField(
        "Unit",
        choices=[
            ("ml", "Milliliters"),
            ("l", "Liters"),
            ("g", "Grams"),
            ("kg", "Kilograms"),
            ("oz", "Ounces"),
            ("cup", "Cups"),
            ("tsp", "Teaspoons"),
            ("tbsp", "Tablespoons"),
        ],
        validators=[DataRequired()],
    )


class BatchFormulaForm(FlaskForm):
    batch_description = TextAreaField(
        "Batch Description",
        validators=[
            DataRequired(),
            Length(
                min=10,
                max=500,
                message="Description must be between 10 and 500 characters",
            ),
        ],
    )
    liquor = SelectField("Liquor", coerce=int, validators=[DataRequired()])

    bottle_count = IntegerField(
        "Number of Bottles",
        validators=[NumberRange(min=0, message="Bottle count must be 0 or greater")],
    )
    bottle_volume = FloatField(
        "Bottle Volume",
        validators=[
            NumberRange(min=0.1, message="Bottle volume must be greater than 0")
        ],
    )
    bottle_volume_unit = SelectField(
        "Volume Unit", choices=[("ml", "Milliliters"), ("l", "Liters")], default="ml"
    )

    ingredients = FieldList(
        FormField(IngredientEntryForm), min_entries=1, max_entries=20
    )

    submit = SubmitField("Create Batch")

    def __init__(
        self, *args, user_id, liquor_repository, ingredient_repository, **kwargs
    ):
        super(BatchFormulaForm, self).__init__(*args, **kwargs)
        self.liquor.choices = [(0, "Select a liquor...")] + [
            (liquor.id, liquor.name)
            for liquor in liquor_repository.get_all_for_user(user_id)
        ]
        ingredient_choices = [(0, "Select an ingredient...")] + [
            (ingredient.id, ingredient.name)
            for ingredient in ingredient_repository.get_all()
        ]
        for entry in self.ingredients.entries:
            entry.ingredient.choices = ingredient_choices

    def validate_ingredients(self, field):
        print("Validating ingredients")
        valid_ingredients = 0
        for ingredient_form in field.entries:
            if (
                ingredient_form.form.ingredient.data
                and ingredient_form.form.quantity.data
                and ingredient_form.form.unit.data
            ):
                valid_ingredients += 1

        if valid_ingredients == 0:
            raise ValidationError("At least one ingredient must be added to the batch.")


class EditBottlesForm(FlaskForm):
    bottle_count = IntegerField(
        "Number of Bottles",
        validators=[
            DataRequired(),
            NumberRange(min=0, message="Bottle count must be 0 or greater"),
        ],
    )
    bottle_volume = FloatField(
        "Bottle Volume",
        validators=[
            DataRequired(),
            NumberRange(min=0.1, message="Bottle volume must be greater than 0"),
        ],
    )
    bottle_volume_unit = SelectField(
        "Volume Unit", choices=[("ml", "Milliliters"), ("l", "Liters")], default="ml"
    )
    submit = SubmitField("Update Bottles")
