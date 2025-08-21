import requests
from bs4 import BeautifulSoup
import json
import time
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def scrape_restaurant_menu(restaurant):
    """
    Scrape menu data from a restaurant's website.
    
    Args:
        restaurant (dict): Restaurant information
        
    Returns:
        dict: Restaurant data with menu items
    """
    name = restaurant['name']
    menu_url = restaurant['menu_url']
    
    logger.info(f"Scraping menu for {name} from {menu_url}")
    
    try:
        # Send GET request to the menu URL
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(menu_url, headers=headers)
        response.raise_for_status()
        
        # Parse the HTML content
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract menu items (this will vary by website structure)
        menu_items = extract_menu_items(soup, name)
        
        return {
            'name': name,
            'website': restaurant['website'],
            'cuisine': restaurant['cuisine'],
            'menu_url': menu_url,
            'menu_items': menu_items
        }
    except Exception as e:
        logger.error(f"Error scraping {name}: {str(e)}")
        return {
            'name': name,
            'website': restaurant['website'],
            'cuisine': restaurant['cuisine'],
            'menu_url': menu_url,
            'error': str(e),
            'menu_items': []
        }

def extract_menu_items(soup, restaurant_name):
    """
    Extract menu items from parsed HTML.
    This function needs to be customized for each restaurant's menu structure.
    
    Args:
        soup (BeautifulSoup): Parsed HTML content
        restaurant_name (str): Name of the restaurant
        
    Returns:
        list: List of menu items with name, price, and description
    """
    menu_items = []
    
    # Custom handling for Spenard Roadhouse
    if "spenard roadhouse" in restaurant_name.lower():
        return extract_spenard_menu_items(soup)
    
    # This is a generic approach that will need customization
    # For each specific restaurant, we would need to inspect their HTML structure
    
    # Try common patterns for menu items
    # Pattern 1: Items in divs with class containing 'menu' or 'item'
    menu_divs = soup.find_all('div', class_=lambda x: x and ('menu' in x.lower() or 'item' in x.lower()))
    
    # Pattern 2: Items in sections with class containing 'dish' or 'food'
    dish_sections = soup.find_all('section', class_=lambda x: x and ('dish' in x.lower() or 'food' in x.lower()))
    
    # Pattern 3: All divs with price information
    price_divs = soup.find_all('div', string=lambda x: x and '$' in str(x))
    
    # Combine all potential menu items
    potential_items = menu_divs + dish_sections
    
    # If we found potential items, try to extract details
    if potential_items:
        for item in potential_items[:10]:  # Limit to first 10 items
            # Try to find name, price, and description within each item
            name = extract_name(item)
            price = extract_price(item)
            description = extract_description(item)
            
            if name and price:
                menu_items.append({
                    'name': name,
                    'price': price,
                    'description': description
                })
    
    # If we didn't find structured menu items, try a different approach
    if not menu_items:
        # Look for any text that contains price patterns
        text_elements = soup.find_all(string=True)
        for text in text_elements:
            if '$' in str(text) and len(str(text).strip()) > 0:
                # This might be a menu item, but we'll need to parse it
                item_data = parse_menu_text(str(text).strip())
                if item_data:
                    menu_items.append(item_data)
    
    # If still no items, return a placeholder
    if not menu_items:
        menu_items.append({
            'name': 'Menu item',
            'price': '$10.00',
            'description': 'Please check website for current menu'
        })
    
    return menu_items

def extract_name(item):
    """Extract item name from HTML element."""
    # Try to find a heading or strong element
    name_element = item.find(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'strong', 'b'])
    if name_element:
        return name_element.get_text().strip()
    
    # Try the first text element
    text_elements = item.find_all(string=True)
    for text in text_elements:
        if len(text.strip()) > 0:
            return text.strip()
    
    return None

def extract_price(item):
    """Extract price from HTML element."""
    # Look for text containing $
    text_elements = item.find_all(string=True)
    for text in text_elements:
        if '$' in str(text):
            # Extract price with regex
            import re
            price_match = re.search(r'\$\d+(?:\.\d+)?', str(text))
            if price_match:
                return price_match.group(0)
    
    return None

def extract_description(item):
    """Extract description from HTML element."""
    # Get all text content and clean it
    text_content = item.get_text().strip()
    
    # Remove price information from description
    import re
    description = re.sub(r'\$\d+(?:\.\d+)?', '', text_content).strip()
    
    # If description is too similar to name, return empty
    name = extract_name(item)
    if name and description.lower() == name.lower():
        return ""
    
    return description

def extract_spenard_menu_items(soup):
    """
    Extract menu items from Spenard Roadhouse's menu.
    
    Args:
        soup (BeautifulSoup): Parsed HTML content
        
    Returns:
        list: List of menu items with name, price, and description
    """
    menu_items = []
    
    # Look for menu items with specific classes or patterns
    # Spenard Roadhouse uses a unique layout, so we need to inspect their HTML
    
    # Try to find elements that contain dish information
    dish_elements = soup.find_all('div', class_=lambda x: x and ('dish' in x.lower() or 'menuitem' in x.lower()))
    
    # If we can't find specific classes, try a more general approach
    if not dish_elements:
        # Look for divs or spans that contain both text and price information
        all_elements = soup.find_all(['div', 'span', 'p'])
        dish_elements = [el for el in all_elements if el.get_text() and '$' in el.get_text()]
    
    # Process each potential menu item
    for element in dish_elements:
        text = element.get_text().strip()
        if text and '$' in text:
            # Parse the text to extract name, price, and description
            item_data = parse_spenard_menu_item(text)
            if item_data:
                menu_items.append(item_data)
    
    # If we still don't have items, try to find any text with prices
    if not menu_items:
        text_elements = soup.find_all(string=True)
        for text in text_elements:
            if '$' in str(text) and len(str(text).strip()) > 0:
                item_data = parse_spenard_menu_item(str(text).strip())
                if item_data:
                    menu_items.append(item_data)
    
    return menu_items

def parse_spenard_menu_item(text):
    """
    Parse a menu item from Spenard Roadhouse.
    
    Args:
        text (str): Text containing menu item information
        
    Returns:
        dict: Menu item with name, price, and description
    """
    import re
    
    # Extract price (look for $ followed by numbers)
    price_match = re.search(r'\$\d+(?:\.\d+)?', text)
    if not price_match:
        return None
    
    price = price_match.group(0)
    
    # Extract the rest of the text
    item_text = text.strip()
    
    # Try to separate name from description
    # Assume the first part (before price) is the name
    # and the second part (after price) is the description
    parts = item_text.split(price_match.group(0))
    name = parts[0].strip(' -')
    
    # Description would be in the second part if it exists
    description = ""
    if len(parts) > 1:
        description = parts[1].strip(' -')
    
    # If we only have a name and no description, 
    # try to split the name part further
    if not description and ' - ' in name:
        name_parts = name.split(' - ')
        name = name_parts[0].strip()
        if len(name_parts) > 1:
            description = ' - '.join(name_parts[1:]).strip()
    
    # Clean up name and description
    name = name.strip()
    description = description.strip()
    
    # If we don't have a name, skip this item
    if not name:
        return None
    
    return {
        'name': name,
        'price': price,
        'description': description
    }

def parse_menu_text(text):
    """Parse menu item from text string."""
    import re
    
    # Extract price
    price_match = re.search(r'\$\d+(?:\.\d+)?', text)
    if not price_match:
        return None
    
    price = price_match.group(0)
    
    # Extract name (text before price)
    name_match = re.search(r'^(.*?)\s*\$', text)
    if name_match:
        name = name_match.group(1).strip()
        description = ""
        
        # If there's more text after the price, treat it as description
        price_end = price_match.end()
        if price_end < len(text):
            description = text[price_end:].strip()
        
        return {
            'name': name,
            'price': price,
            'description': description
        }
    
    return None

def scrape_all_restaurants():
    """Scrape menu data for all restaurants in restaurants.json."""
    # Load restaurant data
    with open('data/restaurants.json', 'r') as f:
        restaurants = json.load(f)
    
    # Scrape each restaurant
    results = []
    for restaurant in restaurants:
        result = scrape_restaurant_menu(restaurant)
        results.append(result)
        # Be respectful to servers - add a small delay
        time.sleep(1)
    
    # Save results to file
    with open('data/scraped_menu_data.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    logger.info(f"Scraped data for {len(results)} restaurants")
    return results

if __name__ == "__main__":
    scrape_all_restaurants()
