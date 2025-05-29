from app import app # To get app context
from database import db, MenuItem

def populate_menu_items():
    menu_items_data = [
        # Appetizers
        {"name": "Crispy Calamari", "description": "Tender calamari rings, lightly battered and fried to a golden crisp. Served with a zesty marinara sauce.", "price": 12.99, "category": "Appetizer", "image_url": "images/calamari.jpg"},
        {"name": "Bruschetta", "description": "Grilled baguette slices topped with fresh diced tomatoes, garlic, basil, and a balsamic glaze.", "price": 9.50, "category": "Appetizer", "image_url": "images/bruschetta.jpg"},
        {"name": "Spinach Artichoke Dip", "description": "A creamy blend of spinach, artichoke hearts, and cheeses, served warm with tortilla chips.", "price": 11.00, "category": "Appetizer", "image_url": "images/spinach_dip.jpg"},

        # Entrees
        {"name": "Grilled Salmon", "description": "Fresh Atlantic salmon fillet, grilled to perfection, served with roasted asparagus and lemon-dill sauce.", "price": 25.00, "category": "Entree", "image_url": "images/salmon.jpg"},
        {"name": "Filet Mignon", "description": "A tender 8oz filet mignon, cooked to your liking, served with garlic mashed potatoes and a red wine reduction.", "price": 35.50, "category": "Entree", "image_url": "images/filet_mignon.jpg"},
        {"name": "Chicken Alfredo", "description": "Fettuccine pasta tossed in a creamy Alfredo sauce with grilled chicken breast and Parmesan cheese.", "price": 18.99, "category": "Entree", "image_url": "images/chicken_alfredo.jpg"},
        {"name": "Grilled Chicken Sandwich", "description": "A classic grilled chicken sandwich with lettuce, tomato, and mayonnaise on a toasted brioche bun. Served with fries.", "price": 14.50, "category": "Entree", "image_url": "images/chicken_sandwich.jpg"},
        {"name": "Margherita Pizza", "description": "Classic Neapolitan pizza with fresh mozzarella, San Marzano tomatoes, basil, and a drizzle of olive oil.", "price": 16.00, "category": "Entree", "image_url": "images/margherita_pizza.jpg"},


        # Desserts
        {"name": "Chocolate Lava Cake", "description": "Warm chocolate cake with a molten chocolate center, served with vanilla ice cream and a raspberry coulis.", "price": 8.99, "category": "Dessert", "image_url": "images/lava_cake.jpg"},
        {"name": "New York Cheesecake", "description": "Classic New York style cheesecake with a graham cracker crust, served with your choice of fruit topping.", "price": 7.50, "category": "Dessert", "image_url": "images/cheesecake.jpg"},

        # Drinks
        {"name": "Coca-Cola", "description": "Classic Coca-Cola.", "price": 2.99, "category": "Drink", "image_url": "images/coke.jpg"},
        {"name": "Fresh Orange Juice", "description": "Freshly squeezed orange juice.", "price": 4.50, "category": "Drink", "image_url": "images/orange_juice.jpg"},
        {"name": "Espresso", "description": "A single shot of rich espresso.", "price": 3.00, "category": "Drink", "image_url": "images/espresso.jpg"},
    ]

    with app.app_context():
        # Check if items already exist to avoid duplicates if script is run multiple times
        existing_items = MenuItem.query.count()
        if existing_items == 0:
            for item_data in menu_items_data:
                item = MenuItem(
                    name=item_data["name"],
                    description=item_data["description"],
                    price=item_data["price"],
                    category=item_data["category"],
                    image_url=item_data["image_url"]
                )
                db.session.add(item)
            db.session.commit()
            print(f"Added {len(menu_items_data)} menu items to the database.")
        else:
            print("Menu items table already populated.")

if __name__ == '__main__':
    populate_menu_items()
