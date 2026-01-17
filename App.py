import streamlit as st
import pandas as pd

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="NearBite - Healthy Local Fusion",
    page_icon="🥗",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- CUSTOM CSS FOR MOBILE UI ---
st.markdown("""
    <style>
    /* Main container styling */
    .main {
        background-color: #f8f9fa;
    }
    /* Style buttons to look more like app buttons */
    div.stButton > button:first-child {
        background-color: #22c55e;
        color: white;
        border-radius: 12px;
        border: none;
        height: 3em;
        width: 100%;
        font-weight: bold;
        transition: all 0.3s;
    }
    div.stButton > button:hover {
        background-color: #16a34a;
        color: white;
        transform: scale(0.98);
    }
    /* Card styling */
    .res-card {
        background-color: white;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        margin-bottom: 20px;
    }
    .price-tag {
        color: #1f2937;
        font-weight: 800;
        font-size: 1.1em;
    }
    .health-badge {
        background-color: #f0fdf4;
        color: #166534;
        padding: 2px 8px;
        border-radius: 6px;
        font-size: 0.8em;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# --- MOCK DATA ---
RESTAURANTS = [
    {
        "id": "r1",
        "name": "Dapur Sihat Machang",
        "cuisine": "Fusion",
        "description": "Traditional flavors with a nutritious modern twist.",
        "rating": 4.8,
        "menu": [
            {"id": "m1", "name": "Nasi Kerabu Quinoa", "price": 15.50, "cals": "310 kcal", "healthy": True},
            {"id": "m2", "name": "Zoodle Laksa", "price": 12.00, "cals": "240 kcal", "healthy": True},
            {"id": "m3", "name": "Tempeh Wrap", "price": 10.00, "cals": "350 kcal", "healthy": True}
        ]
    },
    {
        "id": "r2",
        "name": "Kelantan Fusion Kitchen",
        "cuisine": "Local",
        "description": "Authentic rural ingredients meet healthy prep methods.",
        "rating": 4.5,
        "menu": [
            {"id": "m4", "name": "Avocado Budu Salad", "price": 14.00, "cals": "220 kcal", "healthy": True},
            {"id": "m5", "name": "Grilled Fish Pesto", "price": 18.00, "cals": "400 kcal", "healthy": True}
        ]
    }
]

# --- SESSION STATE INITIALIZATION ---
if 'cart' not in st.session_state:
    st.session_state.cart = []
if 'page' not in st.session_state:
    st.session_state.page = "Home"
if 'selected_res' not in st.session_state:
    st.session_state.selected_res = None

# --- HELPER FUNCTIONS ---
def add_to_cart(item):
    st.session_state.cart.append(item)
    st.toast(f"Added {item['name']} to cart!")

def navigate_to(page, res=None):
    st.session_state.page = page
    st.session_state.selected_res = res

# --- UI COMPONENTS ---

# Top Bar / Navigation
cols = st.columns([4, 1])
with cols[0]:
    if st.session_state.page != "Home":
        if st.button("← Back", key="back_btn"):
            navigate_to("Home")
    else:
        st.title("NearBite")
with cols[1]:
    cart_count = len(st.session_state.cart)
    if st.button(f"🛒({cart_count})", key="cart_nav"):
        navigate_to("Cart")

# --- PAGE: HOME ---
if st.session_state.page == "Home":
    st.markdown("### 📍 Machang, Kelantan")
    st.info("Discover healthy local fusion nearby.")
    
    search = st.text_input("Search for cuisine...", placeholder="e.g. Nasi Kerabu")
    
    for res in RESTAURANTS:
        if search.lower() in res['name'].lower() or search.lower() in res['cuisine'].lower():
            with st.container():
                st.markdown(f"""
                <div class="res-card">
                    <span class="health-badge">{res['cuisine']}</span>
                    <h2 style='margin-top:10px;'>{res['name']}</h2>
                    <p style='color:gray;'>{res['description']}</p>
                    <p>⭐ {res['rating']} | 🥗 Healthy Certified</p>
                </div>
                """, unsafe_allow_html=True)
                if st.button(f"View Menu", key=f"view_{res['id']}"):
                    navigate_to("Details", res)

# --- PAGE: DETAILS ---
elif st.session_state.page == "Details":
    res = st.session_state.selected_res
    st.header(res['name'])
    st.write(res['description'])
    st.divider()
    
    st.subheader("Menu Items")
    for item in res['menu']:
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown(f"**{item['name']}**")
            st.caption(f"{item['cals']} | RM {item['price']:.2f}")
        with col2:
            if st.button("Add", key=f"add_{item['id']}"):
                add_to_cart(item)

# --- PAGE: CART ---
elif st.session_state.page == "Cart":
    st.header("Your Basket")
    
    if not st.session_state.cart:
        st.warning("Your basket is empty!")
        if st.button("Browse Food"):
            navigate_to("Home")
    else:
        total = 0
        for i, item in enumerate(st.session_state.cart):
            col1, col2 = st.columns([4, 1])
            with col1:
                st.write(f"{item['name']}")
                st.caption(f"RM {item['price']:.2f}")
            with col2:
                if st.button("❌", key=f"del_{i}"):
                    st.session_state.cart.pop(i)
                    st.rerun()
            total += item['price']
        
        st.divider()
        st.markdown(f"### Total: RM {total:.2f}")
        
        if st.button("Place Order"):
            st.success("Order placed successfully! 🚀")
            st.session_state.cart = []
            st.balloons()
