from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_user, logout_user, login_required
import sqlalchemy as sa
from app import app, db
from app.forms import LoginForm, BatchFormulaForm, LiquorForm
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


@app.route('/create_liquor', methods=['GET', 'POST'])
@login_required
def create_liquor():
    form = LiquorForm()
    if form.validate_on_submit():
        try:
            liquor = Liquor(
                name=form.name.data,
                description=form.description.data,
                user_id=current_user.id
            )
            db.session.add(liquor)
            db.session.commit()
            flash(f'Liquor "{liquor.name}" created successfully!', 'success')
            return redirect(url_for('index'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating liquor: {str(e)}', 'error')
            return render_template('create_liquor.html', form=form)
    
    return render_template('create_liquor.html', form=form)


@app.route('/batch_formula', methods=['GET', 'POST'])
@login_required
def batch_formula():
    form = BatchFormulaForm()
    
    # Filter liquors to only show user's liquors
    form.liquor.choices = [(liquor.id, liquor.name) for liquor in Liquor.query.filter_by(user_id=current_user.id).all()]
    
    # Handle pre-selected liquor from URL parameter
    liquor_id = request.args.get('liquor', type=int)
    if liquor_id and request.method == 'GET':
        # Verify the liquor belongs to the current user
        liquor = Liquor.query.filter_by(id=liquor_id, user_id=current_user.id).first()
        if liquor:
            form.liquor.data = liquor_id
    
    if form.validate_on_submit():
        try:
            # Convert bottle volume to milliliters if needed
            bottle_volume_ml = form.bottle_volume.data
            if form.bottle_volume_unit.data == 'l':
                bottle_volume_ml = form.bottle_volume.data * 1000
            
            new_batch = Batch(
                description=form.batch_description.data,
                liquor_id=form.liquor.data,
                bottle_count=form.bottle_count.data or 0,
                bottle_volume=bottle_volume_ml,
                bottle_volume_unit='ml'  # Always store in ml
            )
            db.session.add(new_batch)
            db.session.flush()  # Get the ID without committing

            # Process ingredients from form data
            ingredients_added = False
            
            # Get ingredient data from request form
            ingredient_ids = request.form.getlist('ingredient_id')
            quantities = request.form.getlist('quantity')
            units = request.form.getlist('unit')
            
            for i in range(len(ingredient_ids)):
                if ingredient_ids[i] and quantities[i] and units[i]:
                    try:
                        batch_formula = BatchFormula(
                            batch_id=new_batch.id,
                            ingredient_id=int(ingredient_ids[i]),
                            quantity=float(quantities[i]),
                            unit=units[i]
                        )
                        db.session.add(batch_formula)
                        ingredients_added = True
                    except (ValueError, TypeError):
                        continue
            
            if not ingredients_added:
                db.session.rollback()
                flash('At least one ingredient must be added to the batch.', 'error')
                ingredients = Ingredient.query.all()
                return render_template('batch_formula.html', form=form, ingredients=ingredients)
            
            db.session.commit()
            flash('Batch formula added successfully!', 'success')
            # Redirect to the liquor's batches page instead of back to the form
            return redirect(url_for('liquor_batches', liquor_id=form.liquor.data))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating batch: {str(e)}', 'error')
            ingredients = Ingredient.query.all()
            return render_template('batch_formula.html', form=form, ingredients=ingredients)
    else:
        # Debug: Print form errors if validation fails
        if form.errors:
            print("Form errors:", form.errors)
            for field_name, errors in form.errors.items():
                for error in errors:
                    flash(f'Error in {field_name}: {error}', 'error')
    
    # Get all ingredients for the template
    ingredients = Ingredient.query.all()
    return render_template('batch_formula.html', form=form, ingredients=ingredients)


@app.route('/liquor/<int:liquor_id>/batches')
@login_required
def liquor_batches(liquor_id):
    """Display all batches for a specific liquor."""
    liquor = Liquor.query.filter_by(id=liquor_id, user_id=current_user.id).first_or_404()
    batches = Batch.query.filter_by(liquor_id=liquor_id).order_by(Batch.date.desc()).all()
    
    return render_template('liquor_batches.html', liquor=liquor, batches=batches)


@app.route('/batch/<int:batch_id>/edit_bottles', methods=['GET', 'POST'])
@login_required
def edit_batch_bottles(batch_id):
    """Edit bottle information for a specific batch."""
    batch = Batch.query.filter_by(id=batch_id).first_or_404()
    
    # Verify the batch belongs to the current user
    if batch.liquor.user_id != current_user.id:
        flash('You do not have permission to edit this batch.', 'error')
        return redirect(url_for('liquor_batches', liquor_id=batch.liquor_id))
    
    if request.method == 'POST':
        try:
            bottle_count = request.form.get('bottle_count', type=int)
            bottle_volume = request.form.get('bottle_volume', type=float)
            bottle_volume_unit = request.form.get('bottle_volume_unit', 'ml')
            
            if bottle_count is not None and bottle_volume is not None:
                # Convert to milliliters if needed
                bottle_volume_ml = bottle_volume
                if bottle_volume_unit == 'l':
                    bottle_volume_ml = bottle_volume * 1000
                
                batch.bottle_count = bottle_count
                batch.bottle_volume = bottle_volume_ml
                batch.bottle_volume_unit = 'ml'  # Always store in ml
                
                db.session.commit()
                flash('Bottle information updated successfully!', 'success')
            else:
                flash('Please provide valid bottle information.', 'error')
                
        except (ValueError, TypeError):
            flash('Invalid bottle information provided.', 'error')
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating bottle information: {str(e)}', 'error')
    
    return redirect(url_for('liquor_batches', liquor_id=batch.liquor_id))