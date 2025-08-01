from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_user, logout_user, login_required
import sqlalchemy as sa
from app import app, db
from app.forms import LoginForm, BatchFormulaForm
from app.models import User, Batch, Ingredient, BatchFormula, Liquor


@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500


@app.route('/')
@app.route('/index')
def index():
    if current_user.is_authenticated:
        liquors = Liquor.query.filter_by(user_id=current_user.id).all()
    else:
        liquors = []
    return render_template('index.html', liquors=liquors)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.scalar(
            sa.select(User).where(User.username == form.username.data))
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password', 'error')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or not next_page.startswith('/'):
            next_page = url_for('index')
        flash(f'Welcome back, {user.username}!', 'success')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        if not username or not email or not password:
            flash('All fields are required', 'error')
            return render_template('register.html')
        
        if len(username) < 3:
            flash('Username must be at least 3 characters long', 'error')
            return render_template('register.html')
        
        if len(password) < 6:
            flash('Password must be at least 6 characters long', 'error')
            return render_template('register.html')
        
        # Check if user already exists
        existing_user = db.session.scalar(sa.select(User).where(User.username == username))
        if existing_user:
            flash('Username already exists', 'error')
            return render_template('register.html')
        
        existing_email = db.session.scalar(sa.select(User).where(User.email == email))
        if existing_email:
            flash('Email already registered', 'error')
            return render_template('register.html')
        
        # Create new user
        user = User(username=username, email=email)
        user.set_password(password)
        
        try:
            db.session.add(user)
            db.session.commit()
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            flash('Registration failed. Please try again.', 'error')
            return render_template('register.html')
    
    return render_template('register.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("You've been logged out.", 'info')
    return redirect(url_for('index'))


@app.route('/batch_formula', methods=['GET', 'POST'])
@login_required
def batch_formula():
    form = BatchFormulaForm()
    
    # Filter liquors to only show user's liquors
    form.liquor.choices = [(liquor.id, liquor.name) for liquor in Liquor.query.filter_by(user_id=current_user.id).all()]
    
    if form.validate_on_submit():
        try:
            new_batch = Batch(
                description=form.batch_description.data,
                liquor_id=form.liquor.data
            )
            db.session.add(new_batch)
            db.session.flush()  # Get the ID without committing

            # Loop through each ingredient entry in the form
            ingredients_added = False
            for ingredient_form in form.ingredients:
                # Only add if ingredient is selected and quantity is provided
                if ingredient_form.ingredient.data and ingredient_form.quantity.data:
                    batch_formula = BatchFormula(
                        batch_id=new_batch.id,
                        ingredient_id=ingredient_form.ingredient.data,
                        quantity=ingredient_form.quantity.data,
                        unit=ingredient_form.unit.data
                    )
                    db.session.add(batch_formula)
                    ingredients_added = True
            
            if not ingredients_added:
                db.session.rollback()
                flash('At least one ingredient must be added to the batch.', 'error')
                return render_template('batch_formula.html', form=form)
            
            db.session.commit()
            flash('Batch formula added successfully!', 'success')
            return redirect(url_for('batch_formula'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating batch: {str(e)}', 'error')
            return render_template('batch_formula.html', form=form)
    
    return render_template('batch_formula.html', form=form)