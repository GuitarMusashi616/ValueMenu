import json
import re

def parse_price(price_str):
    """
    Parse price string and return numeric value.
    
    Args:
        price_str (str): Price string (e.g., "$12.95")
        
    Returns:
        float: Numeric price value
    """
    # Remove dollar sign and any whitespace
    price_str = price_str.replace('$', '').strip()
    
    try:
        return float(price_str)
    except ValueError:
        return 0.0

def estimate_cost_to_make(price):
    """
    Estimate cost to make based on menu price.
    For restaurants, food costs typically range from 25-35% of menu price.
    
    Args:
        price (float): Menu price
        
    Returns:
        float: Estimated cost to make
    """
    # Use 30% as average food cost percentage
    return price * 0.30

def calculate_value_rating(price, cost_to_make):
    """
    Calculate value rating based on price and cost to make.
    
    Args:
        price (float): Menu price
        cost_to_make (float): Estimated cost to make
        
    Returns:
        float: Value rating (higher is better value)
    """
    if price <= 0:
        return 0.0
    
    # Value rating = (Price - Cost to Make) / Price
    # Higher values indicate better value (more profit margin)
    return (price - cost_to_make) / price

def calculate_perceived_value(overall_rating, price, cost_to_make):
    """
    Calculate perceived value based on overall rating, price, and cost to make.
    
    Args:
        overall_rating (float): Overall rating (1-5 scale)
        price (float): Menu price
        cost_to_make (float): Estimated cost to make
        
    Returns:
        float: Perceived value rating
    """
    if overall_rating <= 0 or price <= 0:
        return 0.0
    
    # Perceived value = Overall Rating / (Price + Cost to Make)
    # Higher values indicate better perceived value
    return overall_rating / (price + cost_to_make)

def process_restaurant_data(restaurant_data, overall_ratings=None):
    """
    Process restaurant data to add value metrics to menu items.
    
    Args:
        restaurant_data (dict): Restaurant data with menu items
        overall_ratings (dict): Optional dictionary of overall ratings by restaurant name
        
    Returns:
        dict: Processed restaurant data with value metrics
    """
    if overall_ratings is None:
        overall_ratings = {}
    
    # Get overall rating for this restaurant (default to 4.0 if not provided)
    restaurant_name = restaurant_data['name']
    overall_rating = overall_ratings.get(restaurant_name, 4.0)
    
    # Process each menu item
    processed_items = []
    for item in restaurant_data['menu_items']:
        # Parse price
        price = parse_price(item['price'])
        
        # Estimate cost to make
        cost_to_make = estimate_cost_to_make(price)
        
        # Calculate value rating
        value_rating = calculate_value_rating(price, cost_to_make)
        
        # Calculate perceived value
        perceived_value = calculate_perceived_value(overall_rating, price, cost_to_make)
        
        # Add metrics to item
        processed_item = item.copy()
        processed_item['price_numeric'] = price
        processed_item['cost_to_make'] = round(cost_to_make, 2)
        processed_item['value_rating'] = round(value_rating, 3)
        processed_item['perceived_value'] = round(perceived_value, 3)
        processed_item['overall_rating'] = overall_rating
        
        processed_items.append(processed_item)
    
    # Add processed items back to restaurant data
    processed_restaurant = restaurant_data.copy()
    processed_restaurant['menu_items'] = processed_items
    
    return processed_restaurant

def process_all_restaurants():
    """
    Process all restaurant data to calculate value metrics.
    """
    # Load scraped menu data
    with open('data/scraped_menu_data.json', 'r') as f:
        restaurants = json.load(f)
    
    # Define overall ratings for each restaurant (1-5 scale)
    overall_ratings = {
        "Snow City Cafe": 4.5,
        "Ginger": 4.7,
        "The Midnight Sun Brewing Company": 4.3,
        "Bear Tooth Theatrepub": 4.2,
        "Moose's Tooth Pub and Pizzeria": 4.6
    }
    
    # Process each restaurant
    processed_restaurants = []
    for restaurant in restaurants:
        processed_restaurant = process_restaurant_data(restaurant, overall_ratings)
        processed_restaurants.append(processed_restaurant)
    
    # Save processed data
    with open('data/processed_menu_data.json', 'w') as f:
        json.dump(processed_restaurants, f, indent=2)
    
    print(f"Processed data for {len(processed_restaurants)} restaurants")
    return processed_restaurants

def find_best_value_items():
    """
    Find the best value items across all restaurants.
    """
    # Load processed menu data
    with open('data/processed_menu_data.json', 'r') as f:
        restaurants = json.load(f)
    
    # Collect all menu items
    all_items = []
    for restaurant in restaurants:
        for item in restaurant['menu_items']:
            # Add restaurant name to item
            item_with_restaurant = item.copy()
            item_with_restaurant['restaurant_name'] = restaurant['name']
            item_with_restaurant['cuisine'] = restaurant['cuisine']
            all_items.append(item_with_restaurant)
    
    # Sort by different metrics
    best_value_by_price = sorted(all_items, key=lambda x: x['value_rating'], reverse=True)
    best_value_by_perceived = sorted(all_items, key=lambda x: x['perceived_value'], reverse=True)
    
    # Save best value items
    best_value_data = {
        'by_value_rating': best_value_by_price[:10],  # Top 10 by value rating
        'by_perceived_value': best_value_by_perceived[:10]  # Top 10 by perceived value
    }
    
    with open('data/best_value_items.json', 'w') as f:
        json.dump(best_value_data, f, indent=2)
    
    print("Best value items saved to data/best_value_items.json")
    return best_value_data

if __name__ == "__main__":
    # Process restaurant data
    process_all_restaurants()
    
    # Find best value items
    find_best_value_items()
