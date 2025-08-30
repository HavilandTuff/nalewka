from flask_wtf import FlaskForm
from werkzeug.datastructures import MultiDict
from wtforms import (
    FieldList,
    FormField,
    IntegerField,
    StringField,
    SubmitField,
)
from wtforms.validators import DataRequired


class SimpleEntryForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    value = IntegerField("Value", validators=[DataRequired()])


class SimpleForm(FlaskForm):
    entries = FieldList(FormField(SimpleEntryForm), min_entries=1)
    submit = SubmitField("Submit")


def test_simple_form(app):
    with app.test_request_context():
        form_data = MultiDict(
            [
                ("entries-0-name", "entry1"),
                ("entries-0-value", 1),
            ]
        )
        form = SimpleForm(formdata=form_data)
        assert form.validate() is True
