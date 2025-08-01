from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, FloatField, TextAreaField, FieldList, FormField
from wtforms.validators import DataRequired, NumberRange, Length
from app import db
from app.models import Ingredient, Batch, Liquor


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=64)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class IngredientEntryForm(FlaskForm):
    ingredient = SelectField('Ingredient', coerce=int, validators=[DataRequired()])
    quantity = FloatField('Quantity', validators=[DataRequired(), NumberRange(min=0.1, message='Quantity must be greater than 0')])
    unit = SelectField('Unit', validators=[DataRequired()])

    def __init__(self, *args, **kwargs):
        super(IngredientEntryForm, self).__init__(*args, **kwargs)
        self.ingredient.choices = [(ingredient.id, ingredient.name) for ingredient in Ingredient.query.all()]
        self.unit.choices = [('grams', 'grams'), ('milliliters', 'milliliters'), ('pieces', 'pieces')]


class BatchFormulaForm(FlaskForm):
    batch_description = TextAreaField('Batch Description', validators=[DataRequired(), Length(min=10, max=500)])
    liquor = SelectField('Liquor', coerce=int, validators=[DataRequired()])
    ingredients = FieldList(FormField(IngredientEntryForm), min_entries=1, max_entries=10)
    submit = SubmitField('Submit')

    def __init__(self, *args, **kwargs):
        super(BatchFormulaForm, self).__init__(*args, **kwargs)
        self.liquor.choices = [(liquor.id, liquor.name) for liquor in Liquor.query.all()]
