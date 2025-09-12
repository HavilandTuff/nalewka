from functools import wraps
from typing import Any, Callable

from flask import (
    Blueprint,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import current_user, login_required, login_user, logout_user

from app.forms import (
    BatchFormulaForm,
    EditBottlesForm,
    IngredientForm,
    LiquorForm,
    LoginForm,
    RegistrationForm,
)
from app.models import Ingredient, Liquor, User
from app.repositories import (
    BatchRepository,
    IngredientRepository,
    LiquorRepository,
    UserRepository,
)
from app.services import create_batch_with_ingredients, update_batch_bottles

user_repository = UserRepository()
liquor_repository = LiquorRepository()
batch_repository = BatchRepository()
ingredient_repository = IngredientRepository()

# Create a Blueprint object
main_bp = Blueprint("main", __name__)

# Note: The error handlers should be registered on the blueprint or app factory
# For simplicity, we'll assume they are registered in the app factory.


def handle_db_errors(f: Callable) -> Callable:
    """Decorator to handle database errors consistently"""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            # db.session.rollback() is now handled in the service layer
            flash(f"A database error occurred: {str(e)}", "error")
            return redirect(url_for("main.index"))

    return decorated_function


def user_owns_liquor(liquor_id: int, user_id: int) -> bool:
    """Helper function remains useful for checks before rendering a form."""
    return liquor_repository.user_owns_liquor(liquor_id, user_id)


@main_bp.route("/")
@main_bp.route("/index")
def index() -> Any:
    liquors = []
    if current_user.is_authenticated:
        try:
            liquors = liquor_repository.get_all_for_user(current_user.id)
        except Exception as e:
            flash(f"Error loading liquors: {str(e)}", "error")
    return render_template("index.html", liquors=liquors)


@main_bp.route("/login", methods=["GET", "POST"])
def login() -> Any:
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        if username and password:
            user = user_repository.get_by_username(username)
            if user is None or not user.check_password(password):
                flash("Invalid username or password", "error")
                return redirect(url_for("main.login"))
            login_user(user, remember=form.remember_me.data)
            next_page = request.args.get("next")
            if not next_page or not next_page.startswith("/"):
                next_page = url_for("main.index")
            flash(f"Welcome back, {user.username}!", "success")
            return redirect(next_page)
    return render_template("login.html", title="Sign In", form=form)


@main_bp.route("/register", methods=["GET", "POST"])
def register() -> Any:
    # This route remains largely the same, but DB interactions could also be moved.
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))
    form = RegistrationForm(user_repository=user_repository)
    if form.validate_on_submit():
        username = form.username.data
        email = form.email.data
        password = form.password.data
        if username and email and password:
            try:
                user = User(username=username, email=email)
                user.set_password(password)
                user_repository.add(user)
                user_repository.commit()
                flash("Registration successful! Please log in.", "success")
                return redirect(url_for("main.login"))
            except Exception:
                user_repository.rollback()
                flash("Registration failed. Please try again.", "error")
    return render_template("register.html", title="Register", form=form)


@main_bp.route("/logout")
@login_required
def logout() -> Any:
    logout_user()
    flash("You've been logged out.", "info")
    return redirect(url_for("main.index"))


@main_bp.route("/create_liquor", methods=["GET", "POST"])
@login_required
@handle_db_errors
def create_liquor() -> Any:
    # This route is simple enough to leave as is for now.
    form = LiquorForm()
    if form.validate_on_submit():
        liquor = Liquor(
            name=form.name.data,
            description=form.description.data,
            user_id=current_user.id,
        )
        liquor_repository.add(liquor)
        liquor_repository.commit()
        flash(f'Liquor "{liquor.name}" created successfully!', "success")
        return redirect(url_for("main.index"))
    return render_template("create_liquor.html", form=form)


# === REFACTORED ROUTE ===
@main_bp.route("/batch_formula", methods=["GET", "POST"])
@login_required
def batch_formula() -> Any:
    form = BatchFormulaForm(
        liquor_repository=liquor_repository,
        ingredient_repository=ingredient_repository,
        user_id=current_user.id,
    )

    liquor_id = request.args.get("liquor", type=int)
    if liquor_id and request.method == "GET":
        if user_owns_liquor(liquor_id, current_user.id):
            form.liquor.data = liquor_id

    if form.validate_on_submit():
        # Delegate all business logic to the service function
        new_batch, error = create_batch_with_ingredients(
            form.data, form.liquor.data, current_user.id
        )

        if error:
            flash(f"Error creating batch: {error}", "error")
        else:
            if new_batch is not None:
                flash(
                    (
                        "Batch formula created successfully with "
                        f"{len(new_batch.formulas)} ingredients!"
                    ),
                    "success",
                )
                return redirect(
                    url_for("main.liquor_batches", liquor_id=new_batch.liquor_id)
                )

    return render_template("batch_formula.html", form=form)


@main_bp.route("/liquor/<int:liquor_id>/batches")
@login_required
@handle_db_errors
def liquor_batches(liquor_id: int) -> Any:
    liquor = liquor_repository.get(liquor_id)
    if not liquor or liquor.user_id != current_user.id:
        flash("Liquor not found or access denied.", "error")
        return redirect(url_for("main.index"))

    batches = batch_repository.get_all_for_liquor(liquor_id)
    return render_template("liquor_batches.html", liquor=liquor, batches=batches)


# === REFACTORED ROUTE ===
@main_bp.route("/batch/<int:batch_id>/edit_bottles", methods=["GET", "POST"])
@login_required
def edit_batch_bottles(batch_id: int) -> Any:
    batch = batch_repository.get(batch_id)
    if not batch:
        flash("Batch not found.", "error")
        return redirect(url_for("main.index"))
    if batch.liquor.user_id != current_user.id:
        flash("You do not have permission to edit this batch.", "error")
        return redirect(url_for("main.liquor_batches", liquor_id=batch.liquor_id))

    form = EditBottlesForm(obj=batch)  # Pre-populate form from the object

    if form.validate_on_submit():
        # Delegate logic to the service function
        updated_batch, error = update_batch_bottles(
            batch_id, current_user.id, form.data
        )

        if error:
            flash(f"Error updating bottle information: {error}", "error")
        else:
            if updated_batch is not None:
                flash("Bottle information updated successfully!", "success")
                return redirect(
                    url_for("main.liquor_batches", liquor_id=updated_batch.liquor_id)
                )

    # Pre-populate form on GET request for better user experience
    if request.method == "GET":
        form.bottle_count.data = batch.bottle_count or 0
        if batch.bottle_volume:
            form.bottle_volume.data = batch.bottle_volume
            form.bottle_volume_unit.data = "ml"

    return render_template("edit_bottles.html", form=form, batch=batch)


@main_bp.route("/batch/<int:batch_id>/details")
@handle_db_errors
@login_required
def batch_details(batch_id: int) -> Any:
    batch = batch_repository.get(batch_id)
    if not batch or batch.liquor.user_id != current_user.id:
        flash("Batch or permission not found.", "error")
        return redirect(url_for("main.index"))
    return render_template("batch_details.html", batch=batch)


@main_bp.route("/add_ingredient", methods=["POST"])
@login_required
def add_ingredient() -> Any:
    """API endpoint to add a new ingredient"""
    form = IngredientForm()
    if form.validate_on_submit():
        # Check if ingredient already exists
        existing_ingredient = ingredient_repository.get_by_name(form.name.data)
        if existing_ingredient:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": "An ingredient with this name already exists.",
                    }
                ),
                400,
            )

        ingredient = Ingredient(name=form.name.data, description=form.description.data)
        ingredient_repository.add(ingredient)
        ingredient_repository.commit()

        # Return the new ingredient data
        return jsonify(
            {
                "success": True,
                "ingredient": {"id": ingredient.id, "name": ingredient.name},
            }
        )

    # Return form errors
    return jsonify({"success": False, "errors": form.errors}), 400
