// Function to format currency
function formatCurrency(amount) {
    return '$' + amount.toFixed(2);
}

// Function to format rating
function formatRating(rating) {
    return rating.toFixed(1) + '/5';
}

// Function to create a dish card element
function createDishCard(dish) {
    const dishCard = document.createElement('div');
    dishCard.className = 'dish-card';
    
    dishCard.innerHTML = `
        <div class="dish-header">
            <div>
                <div class="dish-name">${dish.name}</div>
                <div class="restaurant-name">${dish.restaurant_name}</div>
            </div>
            <div class="dish-price">${dish.price}</div>
        </div>
        <div class="dish-description">${dish.description}</div>
        <div class="dish-metrics">
            <div class="metric value-rating">
                <div class="metric-label">Value Rating</div>
                <div class="metric-value">${dish.value_rating.toFixed(3)}</div>
            </div>
            <div class="metric perceived-value">
                <div class="metric-label">Perceived Value</div>
                <div class="metric-value">${dish.perceived_value.toFixed(3)}</div>
            </div>
            <div class="metric overall-rating">
                <div class="metric-label">Overall Rating</div>
                <div class="metric-value">${formatRating(dish.overall_rating)}</div>
            </div>
            <div class="metric cost-to-make">
                <div class="metric-label">Cost to Make</div>
                <div class="metric-value">${formatCurrency(dish.cost_to_make)}</div>
            </div>
        </div>
    `;
    
    return dishCard;
}

// Function to create a restaurant card element
function createRestaurantCard(restaurant) {
    const restaurantCard = document.createElement('div');
    restaurantCard.className = 'restaurant-card';
    
    // Create dish list HTML
    let dishListHTML = '';
    restaurant.menu_items.forEach(dish => {
        dishListHTML += `
            <div class="dish-card">
                <div class="dish-header">
                    <div class="dish-name">${dish.name}</div>
                    <div class="dish-price">${dish.price}</div>
                </div>
                <div class="dish-description">${dish.description}</div>
                <div class="dish-metrics">
                    <div class="metric value-rating">
                        <div class="metric-label">Value Rating</div>
                        <div class="metric-value">${dish.value_rating.toFixed(3)}</div>
                    </div>
                    <div class="metric perceived-value">
                        <div class="metric-label">Perceived Value</div>
                        <div class="metric-value">${dish.perceived_value.toFixed(3)}</div>
                    </div>
                </div>
            </div>
        `;
    });
    
    restaurantCard.innerHTML = `
        <div class="restaurant-header">
            <div class="restaurant-name">${restaurant.name}</div>
            <div class="restaurant-cuisine">${restaurant.cuisine}</div>
        </div>
        <div class="restaurant-info">
            <div class="restaurant-rating">
                <span>Rating:</span>
                <span class="restaurant-rating-value">${restaurant.menu_items && restaurant.menu_items.length > 0 ? formatRating(restaurant.menu_items[0].overall_rating) : 'No rating available'}</span>
            </div>
            <div class="restaurant-website">
                <a href="${restaurant.website}" target="_blank">Website</a>
            </div>
            <div class="restaurant-menu-link">
                <a href="${restaurant.menu_url}" target="_blank">View Menu</a>
            </div>
        </div>
        <div class="restaurant-dishes">
            <h4>Menu Items</h4>
            <div class="dish-list">
                ${dishListHTML || '<p>No menu items available</p>'}
            </div>
        </div>
    `;
    
    return restaurantCard;
}

// Function to load and display best value dishes
async function loadBestValueDishes() {
    try {
        const response = await fetch('./data/processed_menu_data.json');
        const restaurants = await response.json();
        
        // Extract all dishes from all restaurants
        const allDishes = [];
        restaurants.forEach(restaurant => {
            if (restaurant.menu_items && restaurant.menu_items.length > 0) {
                restaurant.menu_items.forEach(dish => {
                    // Add restaurant name to dish object for display
                    const dishWithRestaurant = {
                        ...dish,
                        restaurant_name: restaurant.name,
                        cuisine: restaurant.cuisine
                    };
                    allDishes.push(dishWithRestaurant);
                });
            }
        });
        
        // Create best value data structure similar to the old format
        const bestValueData = {
            by_value_rating: [...allDishes].sort((a, b) => b.value_rating - a.value_rating),
            by_perceived_value: [...allDishes].sort((a, b) => b.perceived_value - a.perceived_value)
        };
        
        const dishesContainer = document.getElementById('dishes-container');
        dishesContainer.innerHTML = ''; // Clear existing content
        
        // Display top 5 dishes by perceived value
        bestValueData.by_perceived_value.slice(0, 5).forEach(dish => {
            const dishCard = createDishCard(dish);
            dishesContainer.appendChild(dishCard);
        });
        
        // Add event listener for sorting
        document.getElementById('sort-by').addEventListener('change', (event) => {
            sortDishes(bestValueData, event.target.value);
        });
    } catch (error) {
        console.error('Error loading best value dishes:', error);
        document.getElementById('dishes-container').innerHTML = '<p>Error loading dish data. Please try again later.</p>';
    }
}

// Function to sort dishes
function sortDishes(bestValueData, sortBy) {
    const dishesContainer = document.getElementById('dishes-container');
    dishesContainer.innerHTML = ''; // Clear existing content
    
    let sortedDishes;
    
    switch (sortBy) {
        case 'value_rating':
            sortedDishes = [...bestValueData.by_value_rating];
            break;
        case 'price':
            sortedDishes = [...bestValueData.by_perceived_value].sort((a, b) => a.price_numeric - b.price_numeric);
            break;
        case 'rating':
            sortedDishes = [...bestValueData.by_perceived_value].sort((a, b) => b.overall_rating - a.overall_rating);
            break;
        case 'perceived_value':
        default:
            sortedDishes = [...bestValueData.by_perceived_value];
            break;
    }
    
    // Display sorted dishes (top 10)
    sortedDishes.slice(0, 10).forEach(dish => {
        const dishCard = createDishCard(dish);
        dishesContainer.appendChild(dishCard);
    });
}

// Function to load and display restaurants
async function loadRestaurants() {
    try {
        const response = await fetch('./data/processed_menu_data.json');
        const restaurants = await response.json();
        
        const restaurantsContainer = document.getElementById('restaurants-container');
        restaurantsContainer.innerHTML = ''; // Clear existing content
        
        restaurants.forEach(restaurant => {
            const restaurantCard = createRestaurantCard(restaurant);
            restaurantsContainer.appendChild(restaurantCard);
        });
    } catch (error) {
        console.error('Error loading restaurants:', error);
        document.getElementById('restaurants-container').innerHTML = '<p>Error loading restaurant data. Please try again later.</p>';
    }
}

// Function to set the last updated date
function setLastUpdated() {
    const lastUpdatedElement = document.getElementById('last-updated');
    const now = new Date();
    lastUpdatedElement.textContent = now.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });
}

// Initialize the page when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    loadBestValueDishes();
    loadRestaurants();
    setLastUpdated();
});
