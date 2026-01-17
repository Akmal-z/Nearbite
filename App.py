import streamlit as st
import pandas as pd
from datetime import datetime
import time

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="NearBite",
    page_icon="🥗",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- MOBILE-FRIENDLY CSS ---
st.markdown("""
    <style>
    /* Remove default padding for mobile feel */
    .block-container {
        padding-top: 1rem;
        padding-bottom: 5rem;
    }
    /* Card styling */
    .food-card {
        background-color: white;
        padding: 15px;
        border-radius: 12px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        margin-bottom: 10px;
        border: 1px solid #f0f0f0;
    }
    /* Bottom Navigation Bar */
    .bottom-nav {
        position: fixed;
        bottom: 0;
        left: 0;
        width: 100%;
        background-color: white;
        padding: 10px 0;
        box-shadow: 0 -2px 10px rgba(0,0,0,0.1);
        z-index: 999;
        text-align: center;
    }
    /* Button Styling */
    div.stButton > button {
        width: 100%;
        border-radius: 10px;
        font-weight: 600;
    }
    .primary-btn button {
        background-color: #22c55e !important;
        color: white !important;
        border: none;
    }
    .nav-btn {
        background: none;
        border: none;
        color: #555;
        font-size: 0.8rem;
    }
    /* Number Input Styling */
    div[data-testid="stNumberInput"] input {
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

# --- MOCK DATA ---
RESTAURANTS = [
    {
        "id": "r1",
        "name": "Dapur Sihat",
        "category": "Fusion",
        "menu": [
            {"id": "m1", "name": "Nasi Kerabu Quinoa", "price": 15.50, "cals": 310},
            {"id": "m2", "name": "Zoodle Laksa", "price": 12.00, "cals": 240},
        ]
    },
    {
        "id": "r2",
        "name": "Kelantan Fusion",
        "category": "Local",
        "menu": [
            {"id": "m3", "name": "Avocado Budu Salad", "price": 14.00, "cals": 220},
            {"id": "m4", "name": "Grilled Fish Pesto", "price": 18.00, "cals": 400},
        ]
    }
]

# --- SESSION STATE SETUP ---
if 'user' not in st.session_state:
    st.session_state.user = None  # None means not logged in
if 'cart' not in st.session_state:
    st.session_state.cart = []
if 'orders' not in st.session_state:
    st.session_state.orders = []  # List of confirmed orders
if 'page' not in st.session_state:
    st.session_state.page = "Login"

# --- FUNCTIONS ---
def login(username):
    st.session_state.user = username
    st.session_state.page = "Menu"

def logout():
    st.session_state.user = None
    st.session_state.cart = []
    st.session_state.page = "Login"

def add_to_cart(item, restaurant_name, quantity):
    # Check if item exists in cart to update quantity
    found = False
    for cart_item in st.session_state.cart:
        if cart_item['id'] == item['id']:
            cart_item['quantity'] += quantity
            found = True
            break
            
    if not found:
        # Add new item with metadata
        cart_item = item.copy()
        cart_item['restaurant'] = restaurant_name
        cart_item['added_at'] = datetime.now()
        cart_item['quantity'] = quantity
        st.session_state.cart.append(cart_item)
    
    st.toast(f"Added {quantity} x {item['name']}")

def get_cart_total():
    return sum(item['price'] * item['quantity'] for item in st.session_state.cart)

def confirm_order():
    if not st.session_state.cart:
        return
    
    new_order = {
        "id": f"ORD-{int(time.time())}",
        "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "items": st.session_state.cart.copy(),
        "total": get_cart_total(),
        "status": "Preparing"
    }
    st.session_state.orders.insert(0, new_order) # Add to top of list
    st.session_state.cart = [] # Clear cart
    st.session_state.page = "OrderSuccess"

# --- PAGES ---

def render_login():
    st.markdown("<h1 style='text-align: center;'>NearBite 🥗</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: gray;'>Healthy Local Fusion</p>", unsafe_allow_html=True)
    
    with st.container():
        st.write("")
        st.write("")
        username = st.text_input("Username", placeholder="Enter your name")
        password = st.text_input("Password", type="password", placeholder="Enter password")
        
        st.write("")
        if st.button("Log In", type="primary"):
            if username and password:
                login(username)
                st.rerun()
            else:
                st.error("Please enter credentials")

def render_menu():
    st.subheader(f"Hello, {st.session_state.user} 👋")
    st.caption("What are you craving today?")
    
    # Filter
    category = st.selectbox("Filter Cuisine", ["All", "Fusion", "Local"])
    
    for res in RESTAURANTS:
        if category == "All" or res['category'] == category:
            st.markdown(f"### {res['name']}")
            for item in res['menu']:
                with st.container():
                    # Layout: 2 parts description, 1 part quantity input, 1 part add button
                    col1, col2, col3 = st.columns([3, 1.2, 1.2])
                    with col1:
                        st.markdown(f"**{item['name']}**")
                        st.caption(f"RM {item['price']:.2f} • {item['cals']} kcal")
                    with col2:
                        qty = st.number_input("Qty", min_value=1, value=1, label_visibility="collapsed", key=f"qty_{item['id']}")
                    with col3:
                        if st.button("Add", key=f"add_{item['id']}"):
                            add_to_cart(item, res['name'], qty)
            st.divider()

def render_cart():
    st.subheader("Your Basket 🛒")
    
    if not st.session_state.cart:
        st.info("Your cart is empty.")
        if st.button("Browse Menu"):
            st.session_state.page = "Menu"
            st.rerun()
        return

    # List items with quantity
    for i, item in enumerate(st.session_state.cart):
        with st.container():
            col1, col2 = st.columns([4, 1])
            with col1:
                st.write(f"**{item['quantity']}x {item['name']}**")
                subtotal = item['price'] * item['quantity']
                st.caption(f"{item['restaurant']} • RM {subtotal:.2f}")
            with col2:
                if st.button("✖", key=f"remove_{i}"):
                    st.session_state.cart.pop(i)
                    st.rerun()
        st.markdown("---")

    total = get_cart_total()
    st.markdown(f"### Total: RM {total:.2f}")
    
    st.write("")
    if st.button("Proceed to Checkout", type="primary"):
        st.session_state.page = "Confirmation"
        st.rerun()

def render_confirmation():
    st.subheader("Confirm Order")
    st.write("Please review your order details.")
    
    with st.container():
        st.markdown("#### Order Summary")
        for item in st.session_state.cart:
            item_total = item['price'] * item['quantity']
            st.write(f"{item['quantity']}x {item['name']} (RM {item_total:.2f})")
        
        st.divider()
        st.markdown(f"**Grand Total: RM {get_cart_total():.2f}**")
    
    st.warning("⚠️ Payment will be collected upon delivery.")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Cancel"):
            st.session_state.page = "Cart"
            st.rerun()
    with col2:
        if st.button("Confirm Order", type="primary"):
            confirm_order()
            st.rerun()

def render_success():
    st.balloons()
    st.success("Order Placed Successfully!")
    st.markdown("""
        <div style="text-align: center; padding: 20px;">
            <h1>🎉</h1>
            <h3>Your food is being prepared!</h3>
            <p>You can track it in the 'Orders' tab.</p>
        </div>
    """, unsafe_allow_html=True)
    
    if st.button("Back to Home"):
        st.session_state.page = "Menu"
        st.rerun()

def render_orders():
    st.subheader("My Orders 📦")
    
    if not st.session_state.orders:
        st.info("No active orders.")
        return
        
    st.caption(f"Total Orders: {len(st.session_state.orders)}")
    
    for order in st.session_state.orders:
        with st.expander(f"{order['date']} - RM {order['total']:.2f} ({order['status']})"):
            st.write(f"**Order ID:** {order['id']}")
            for item in order['items']:
                st.write(f"- {item['quantity']}x {item['name']}")
            st.caption("Cash on Delivery")

# --- MAIN APP CONTROLLER ---

if st.session_state.page == "Login":
    render_login()

else:
    # --- NAVIGATION BAR (Mobile Style) ---
    # We use columns to simulate a bottom nav bar
    st.markdown("---")
    nav_col1, nav_col2, nav_col3, nav_col4 = st.columns(4)
    
    with nav_col1:
        if st.button("🏠\nMenu"):
            st.session_state.page = "Menu"
            st.rerun()
    with nav_col2:
        # Calculate total items count (sum of quantities)
        cart_count = sum(item['quantity'] for item in st.session_state.cart)
        label = f"🛒\nCart ({cart_count})"
        if st.button(label):
            st.session_state.page = "Cart"
            st.rerun()
    with nav_col3:
        if st.button("📦\nOrders"):
            st.session_state.page = "Orders"
            st.rerun()
    with nav_col4:
        if st.button("🚪\nLogout"):
            logout()
            st.rerun()

    # --- RENDER CURRENT PAGE CONTENT ---
    if st.session_state.page == "Menu":
        render_menu()
    elif st.session_state.page == "Cart":
        render_cart()
    elif st.session_state.page == "Confirmation":
        render_confirmation()
    elif st.session_state.page == "OrderSuccess":
        render_success()
    elif st.session_state.page == "Orders":
        render_orders()
