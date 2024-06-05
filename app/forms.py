from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, FloatField, TextAreaField
from wtforms.validators import DataRequired
from app import db
from app.models import Ingredient, Batch, Liquor


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class SelectIngredient(SelectField):
    def __int__(self, *args, **kwargs):
        super(SelectIngredient, self).__init__(*args, **kwargs)
        self.choices = [(ingredient.id, ingredient.name) for ingredient in Ingredient.query.all()]


class BatchFormulaForm(FlaskForm):
    batch_description = TextAreaField('Batch Description', validators=[DataRequired()])
    liquor = SelectField('Liquor', coerce=int, validators=[DataRequired()])
    ingredient = SelectField('Ingredient', coerce=int, validators=[DataRequired()])
    quantity = FloatField('Quantity (grams)', validators=[DataRequired()])
    submit = SubmitField('Submit')

    def __init__(self, *args, **kwargs):
        super(BatchFormulaForm, self).__init__(*args, **kwargs)
        self.liquor.choices = [(liquor.id, liquor.name) for liquor in Liquor.query.all()]
        self.ingredient.choices = [(ingredient.id, ingredient.name) for ingredient in Ingredient.query.all()]
