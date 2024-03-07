from .models import *
from faker import Faker
import random, os
from django.conf import settings

fake = Faker()

def create_restaurants():
    names = ["Taj Mahal Indian Restaurant", "Spice Route", "Curry House", "Masala Kitchen", "Namaste India"]
    image_folder_path = os.path.join(settings.BASE_DIR, 'media/restaurant_images')
    image_files = os.listdir(image_folder_path)
    num_images = len(image_files)
    for i, name in enumerate(names):
        address = fake.address()
        description = fake.text(max_nb_chars=200)
        rating = round(random.uniform(3, 5), 1)
        image_file_name = image_files[i % num_images]  # Ensure cycling through available images
        image_path = f'restaurant_images/{image_file_name}'  # Relative path to the image
        restaurant = Restaurant.objects.create(
            name=name, 
            address=address, 
            description=description, 
            rating=rating, 
            image=image_path)
        restaurant.save()

def create_categories():
    Names=["Fish",'Rice','Chicken','Mutton','Veg','Paratha','Non-veg',]
    for category_name in Names:
        category = Category.objects.create(catagory=category_name)
        category.save()


def create_foods(num_per_restaurant):
    if not Category.objects.exists():
        create_categories()  # Create categories if none exist

    if not Restaurant.objects.exists():
        create_restaurants()  # Create restaurants if none exist

    restaurants = Restaurant.objects.all()
    categories = Category.objects.all()

    food_names = {
        "Fish": ["Grilled Fish", "Fish Curry", "Fish Fry", "Fish Tikka", "Fish Tandoori", "Fish Masala", "Fish Biriyani", "Fish Cutlet", "Fish Kebab", "Fish Pakora"],
        "Rice": ["Biryani", "Fried Rice", "Pulao", "Vegetable Rice", "Lemon Rice", "Coconut Rice", "Tamarind Rice", "Tomato Rice", "Mushroom Rice", "Peas Pulao"],
        "Chicken": ["Chicken Tikka", "Butter Chicken", "Chicken Curry", "Chicken Kebab", "Chicken Biryani", "Chicken Shawarma", "Chicken Tandoori", "Chicken 65", "Chicken Manchurian", "Chicken Lollipop"],
        "Mutton": ["Mutton Curry", "Mutton Biryani", "Mutton Korma", "Mutton Rogan Josh", "Mutton Fry", "Mutton Stew", "Mutton Chops", "Mutton Pulao", "Mutton Kabab", "Mutton Paya"],
        "Veg": ["Paneer Tikka", "Veg Biryani", "Mixed Veg Curry", "Vegetable Stir Fry", "Aloo Gobi", "Palak Paneer", "Vegetable Korma", "Bhindi Masala", "Dal Fry", "Chana Masala"],
        "Paratha": ["Aloo Paratha", "Gobi Paratha", "Paneer Paratha", "Methi Paratha", "Onion Paratha", "Palak Paratha", "Cheese Paratha", "Mooli Paratha", "Sweet Paratha", "Kheema Paratha"],
        "Non-veg": ["Egg Curry", "Egg Fried Rice", "Egg Bhurji", "Chicken Lollipop", "Egg Biryani", "Chicken Fry", "Chicken Pulao", "Egg Masala", "Chicken Roast", "Chicken Liver Fry"]
    }

    for restaurant in restaurants:
        for _ in range(num_per_restaurant):
            category = random.choice(categories)
            name = random.choice(food_names[category.catagory])
            cost = round(random.uniform(5, 50), 2)
            # Relative path to the image folder
            image_folder = 'food_images'
            default_image = os.path.join(image_folder, f"{category.catagory}.jpg")
            food = Food.objects.create(restaurant=restaurant, name=name, catagory=category, cost=cost, image=default_image)
            food.save()


def reset():
    Food.objects.all().delete()
    Category.objects.all().delete()
    Restaurant.objects.all().delete()
  
def create_all(food):
    create_restaurants()
    create_categories()
    create_foods(food)