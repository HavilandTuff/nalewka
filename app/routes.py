from flask import render_template, flash, redirect, url_for
from flask_login import current_user, login_user, logout_user
import sqlalchemy as sa
from app import app, db
from app.forms import LoginForm, BatchFormulaForm
from app.models import User, Batch, Ingredient, BatchFormula, Liquor


@app.route('/')
@app.route('/index')
def index():
    user = {'username': 'Karol'}
    liquors = [
        {"name": "Wiśniówka", "description": "Z wiśni."},
        {"name": "Cytrynówka", "description": "Z cytryn."}
    ]
    return render_template('index.html', user=user, liquors=liquors)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.scalar(
            sa.select(User).where(User.username == form.username.data))
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        return redirect(url_for('index'))
    return render_template('login.html', title='Sign In', form=form)


@app.route('/logout')
def logout():
    logout_user()
    flash("You've been logged out.")
    return redirect(url_for('index'))


@app.route('/batch_formula', methods=['GET', 'POST'])
def batch_formula():
    form = BatchFormulaForm()
    if form.validate_on_submit():
        new_batch = Batch(
            description=form.batch_description.data,
            liquor_id=form.liquor.data
        )
        db.session.add(new_batch)
        db.session.commit()

        batch_formula = BatchFormula(
            batch_id=new_batch.id,
            ingredient_id=form.ingredient.data,
            quantity=form.quantity.data
        )
        db.session.add(batch_formula)
        db.session.commit()

        flash('Batch formula added successfully!', 'success')
        return redirect(url_for('batch_formula'))
    return render_template('batch_formula.html', form=form)