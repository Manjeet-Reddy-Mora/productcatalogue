import streamlit as st
import pandas as pd
from datetime import datetime

# Page configuration for layout
st.set_page_config(page_title="Product Catalog", layout="wide")

# Load data from Excel
@st.cache_data
def load_data(file_path):
    try:
        data = pd.read_excel(file_path, engine='openpyxl')
        if data.empty:
            st.error("The Excel file is empty.")
            st.stop()
        return data
    except Exception as e:
        st.error(f"An error occurred while loading the data: {e}")
        st.stop()

# File path to the product catalog (update with your file's path or URL)
file_path = 'products.xlsx'

# Load product data
products = load_data(file_path)

# Ensure necessary columns are present
required_columns = ['Product Name', 'Category', 'Price', 'Discount', 'Stock', 'Rating', 'Features', 'Image URL', 'Launch Date', 'Product ID']
for col in required_columns:
    if col not in products.columns:
        st.error(f"Missing column: {col}")
        st.stop()

# Convert 'Launch Date' to datetime
products['Launch Date'] = pd.to_datetime(products['Launch Date'])

# App title and description
st.title("🛍️ Product Catalog")
st.subheader("Find the best products tailored to your needs.")
st.write("---")

# Sidebar filters
st.sidebar.header("Filter Products")

# Category Filter
categories = st.sidebar.multiselect('Category', options=sorted(products['Category'].unique()), default=sorted(products['Category'].unique()))

# Price Range Filter
price_range = st.sidebar.slider('Price Range (₹)', 
                                 min_value=int(products['Price'].min()), 
                                 max_value=int(products['Price'].max()), 
                                 value=(int(products['Price'].min()), int(products['Price'].max())))

# Discount Filter
discount_range = st.sidebar.slider('Discount (%)', 
                                    min_value=int(products['Discount'].min()), 
                                    max_value=int(products['Discount'].max()), 
                                    value=(int(products['Discount'].min()), int(products['Discount'].max())))

# Rating Filter
rating = st.sidebar.selectbox('Rating', options=[1, 2, 3, 4, 5], index=4)

# Launch Date Filter
launch_date_range = st.sidebar.date_input('Launch Date Range', 
                                          value=[products['Launch Date'].min().date(), products['Launch Date'].max().date()])

# Stock Availability Filter
in_stock = st.sidebar.checkbox('Only show in-stock products', value=True)

# Sort Options
sort_by = st.sidebar.selectbox('Sort by', ['Price', 'Rating', 'Discount'])

# Apply Filters button
apply_filters = st.sidebar.button('Apply Filters')

# Save Wishlist in session state
if 'wishlist' not in st.session_state:
    st.session_state.wishlist = []

# Function to add product to wishlist
def add_to_wishlist(product_name):
    if product_name not in st.session_state.wishlist:
        st.session_state.wishlist.append(product_name)
        st.success(f"{product_name} added to your Wishlist!")

# Apply filters
if apply_filters:
    # Filter products based on selections
    filtered_products = products[
        (products['Category'].isin(categories)) &
        (products['Price'].between(price_range[0], price_range[1])) &
        (products['Discount'].between(discount_range[0], discount_range[1])) &
        (products['Rating'] >= rating) &
        (products['Launch Date'].between(pd.to_datetime(launch_date_range[0]), pd.to_datetime(launch_date_range[1]))) &
        ((products['Stock'] > 0) if in_stock else True)
    ].sort_values(by=sort_by)

    # Display filtered products
    if filtered_products.empty:
        st.write("No products match your criteria.")
    else:
        st.subheader("Available Products")

        for _, row in filtered_products.iterrows():
            st.write("---")
            col1, col2 = st.columns([2, 1])

            # Left column for product details
            with col1:
                st.markdown(f"### {row['Product Name']}")
                st.markdown(f"**Category:** {row['Category']}")
                st.markdown(f"**Price:** ₹{row['Price']}")
                st.markdown(f"**Discount:** {row['Discount']}%")
                st.markdown(f"**Rating:** {row['Rating']} stars")
                st.markdown(f"**Features:** {row['Features']}")
                st.markdown(f"**Stock Available:** {'Yes' if row['Stock'] > 0 else 'Out of Stock'}")

                # Wishlist button
                if st.button(f"Add {row['Product Name']} to Wishlist"):
                    add_to_wishlist(row['Product Name'])

            # Right column for product image
            with col2:
                if pd.notna(row['Image URL']):
                    st.image(row['Image URL'], caption=row['Product Name'], use_container_width=True)

        st.write("---")

# Display Wishlist
if st.sidebar.button("View Wishlist"):
    st.sidebar.write("**Your Wishlist:**")
    st.sidebar.write(st.session_state.wishlist)

# Footer
st.write("---")
st.markdown('<div style="text-align: center; font-size: small;">© 2024 Product Catalog. All rights reserved.</div>', unsafe_allow_html=True)

