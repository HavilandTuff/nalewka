import click
from dotenv import load_dotenv

from app import create_app, db
from app.models import Batch, BatchFormula, Ingredient, Liquor, User

load_dotenv()

# Create the application instance using the factory
app = create_app()


# ----------------------------------------------------------------
# MOVED FROM manage.py - This is the seeding function
# ----------------------------------------------------------------
def create_sample_data():
    """Create sample data for testing."""
    print("Creating sample data...")

    # Create sample user
    user = User(username="admin", email="admin@example.com")
    user.set_password("password123")
    db.session.add(user)
    db.session.flush()

    # Create sample liquors
    liquors_data = [
        {"name": "Wiśniówka", "description": "Traditional Polish cherry liqueur"},
        {"name": "Cytrynówka", "description": "Refreshing lemon liqueur"},
        {"name": "Nalewka z Malin", "description": "Sweet raspberry liqueur"},
    ]
    liquors = [Liquor(user_id=user.id, **data) for data in liquors_data]
    db.session.add_all(liquors)
    db.session.flush()

    # Create sample ingredients
    ingredients_data = [
        {"name": "Cherries", "description": "Fresh cherries"},
        {"name": "Lemons", "description": "Fresh lemons"},
        {"name": "Raspberries", "description": "Fresh raspberries"},
        {"name": "Sugar", "description": "Granulated sugar"},
        {"name": "Honey", "description": "Natural honey"},
        {"name": "Vodka", "description": "High-quality vodka"},
    ]
    ingredients = [Ingredient(**data) for data in ingredients_data]
    db.session.add_all(ingredients)
    db.session.flush()

    # Create sample batches
    batches_data = [
        {"description": "First batch of Wiśniówka", "liquor_id": liquors[0].id},
        {"description": "Summer batch of Cytrynówka", "liquor_id": liquors[1].id},
    ]
    batches = [Batch(**data) for data in batches_data]
    db.session.add_all(batches)
    db.session.flush()

    # Create sample batch formulas
    formulas = [
        BatchFormula(
            batch_id=batches[0].id,
            ingredient_id=ingredients[0].id,
            quantity=1000,
            unit="grams",
        ),
        BatchFormula(
            batch_id=batches[0].id,
            ingredient_id=ingredients[3].id,
            quantity=300,
            unit="grams",
        ),
        BatchFormula(
            batch_id=batches[0].id,
            ingredient_id=ingredients[5].id,
            quantity=1500,
            unit="milliliters",
        ),
        BatchFormula(
            batch_id=batches[1].id,
            ingredient_id=ingredients[1].id,
            quantity=500,
            unit="grams",
        ),
        BatchFormula(
            batch_id=batches[1].id,
            ingredient_id=ingredients[4].id,
            quantity=200,
            unit="grams",
        ),
        BatchFormula(
            batch_id=batches[1].id,
            ingredient_id=ingredients[5].id,
            quantity=1000,
            unit="milliliters",
        ),
    ]
    db.session.add_all(formulas)

    try:
        db.session.commit()
        print("✅ Sample data created successfully!")
        print("👤 User: admin / password123")
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error creating sample data: {e}")


# --- Flask Shell Context ---
@app.shell_context_processor
def make_shell_context():
    return {
        "db": db,
        "User": User,
        "Liquor": Liquor,
        "Ingredient": Ingredient,
        "Batch": Batch,
        "BatchFormula": BatchFormula,
    }


# --- Flask CLI Commands ---
@app.cli.command("init-db")
def init_db_command():
    """Initialize the database."""
    with app.app_context():
        db.create_all()
    click.echo("✅ Database initialized!")


@app.cli.command("reset-db")
@click.confirmation_option(
    prompt="Are you sure you want to reset the database? This will delete all data."
)
def reset_db_command():
    """Reset the database (drops all tables and recreates them)."""
    with app.app_context():
        db.drop_all()
        db.create_all()
    click.echo("🔄 Database reset complete!")


@app.cli.command("seed-data")
def seed_data_command():
    """Populate the database with sample data."""
    with app.app_context():
        # This now calls the function defined inside this file
        create_sample_data()
    click.echo("🌱 Sample data seeded successfully.")
