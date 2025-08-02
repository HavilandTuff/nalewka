from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, FloatField, TextAreaField, FieldList, FormField
from wtforms.validators import DataRequired, NumberRange, Length, Email
from app import db
from app.models import Ingredient, Batch, Liquor


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=64)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class LiquorForm(FlaskForm):
    name = StringField('Liquor Name', validators=[DataRequired(), Length(min=2, max=128)])
    description = TextAreaField('Description', validators=[Length(max=1000)])
    submit = SubmitField('Create Liquor')


class BatchFormulaForm(FlaskForm):
    batch_description = TextAreaField('Batch Description', validators=[DataRequired(), Length(min=10, max=500)])
    liquor = SelectField('Liquor', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Submit')

    def __init__(self, *args, **kwargs):
        super(BatchFormulaForm, self).__init__(*args, **kwargs)
        # Initialize liquor choices
        self.liquor.choices = [(liquor.id, liquor.name) for liquor in Liquor.query.all()]
