import streamlit as st
import pandas as pd
from datetime import datetime
from openpyxl import load_workbook

# Page configuration for layout
st.set_page_config(page_title="Product Catalog", layout="wide")

# Function to load data from Excel
@st.cache_data
def load_data(uploaded_file):
    try:
        data = pd.read_excel(uploaded_file, engine='openpyxl')
        if data.empty:
            st.error("The uploaded Excel file is empty.")
            st.stop()
        return data
    except Exception as e:
        st.error(f"An error occurred while loading the data: {e}")
        st.stop()

# File uploader
uploaded_file = st.sidebar.file_uploader("Upload Excel File", type=["xlsx"])
if not uploaded_file:
    st.stop()

# Load product data
products = load_data(uploaded_file)

# Ensure necessary columns are present
required_columns = ['Product Name', 'Category', 'Price', 'Discount', 'Stock', 'Rating', 'Features', 'Image URL', 'Launch Date', 'Product ID']
for col in required_columns:
    if col not in products.columns:
        st.error(f"Missing required column: {col}")
        st.stop()

# Data Cleaning
try:
    # Convert 'Price' column to numeric
    products['Price'] = pd.to_numeric(products['Price'].replace({'\\$': '', ',': ''}, regex=True), errors='coerce')

    # Convert 'Discount' column to numeric (assumes it's in decimal format)
    products['Discount'] = pd.to_numeric(products['Discount'], errors='coerce') * 100

    # Convert 'Launch Date' to datetime
    products['Launch Date'] = pd.to_datetime(products['Launch Date'], errors='coerce')

    # Fill missing or invalid dates with a fallback
    products['Launch Date'].fillna(pd.Timestamp('2000-01-01'), inplace=True)

    # Handle missing or invalid values in 'Rating' and 'Discount'
    products['Rating'].fillna(0, inplace=True)
    products['Discount'].fillna(0, inplace=True)

    # Convert 'Stock' column to indicate stock availability
    products['Stock'] = products['Stock'].apply(lambda x: 1 if str(x).lower() == 'in stock' else 0)
except Exception as e:
    st.error(f"An error occurred while processing the data: {e}")
    st.stop()

# App title and description
st.title("\U0001F6D2 Product Catalog")
st.subheader("Find the best products tailored to your needs.")
st.write("---")

# Sidebar filters
st.sidebar.header("Filter Products")

# Category Filter
categories = st.sidebar.multiselect('Category', options=sorted(products['Category'].dropna().unique()), default=sorted(products['Category'].dropna().unique()))

# Price Range Filter
price_range = st.sidebar.slider(
    'Price Range (₹)',
    min_value=int(products['Price'].min()),
    max_value=int(products['Price'].max()),
    value=(int(products['Price'].min()), int(products['Price'].max()))
)

# Discount Filter
discount_range = st.sidebar.slider(
    'Discount (%)',
    min_value=int(products['Discount'].min()),
    max_value=int(products['Discount'].max()),
    value=(int(products['Discount'].min()), int(products['Discount'].max()))
)

# Rating Filter
rating = st.sidebar.selectbox('Minimum Rating', options=[0, 1, 2, 3, 4, 5], index=5)

# Launch Date Filter
min_date = products['Launch Date'].min().date()
max_date = products['Launch Date'].max().date()
launch_date_range = st.sidebar.date_input('Launch Date Range', value=[min_date, max_date])

# Stock Availability Filter
in_stock = st.sidebar.checkbox('Only show in-stock products', value=True)

# Sort Options
sort_by = st.sidebar.selectbox('Sort by', ['Price', 'Rating', 'Discount'])

# Apply Filters button
if st.sidebar.button('Apply Filters'):
    # Apply filters to products
    filtered_products = products[
        (products['Category'].isin(categories)) &
        (products['Price'].between(price_range[0], price_range[1])) &
        (products['Discount'].between(discount_range[0], discount_range[1])) &
        (products['Rating'] >= rating) &
        (products['Launch Date'].between(pd.to_datetime(launch_date_range[0]), pd.to_datetime(launch_date_range[1]))) &
        ((products['Stock'] > 0) if in_stock else True)
    ]

    # Sort the filtered products
    filtered_products = filtered_products.sort_values(by=sort_by)

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

                # Add to wishlist button
                if st.button(f"Add {row['Product Name']} to Wishlist", key=row['Product ID']):
                    if 'wishlist' not in st.session_state:
                        st.session_state.wishlist = []
                    if row['Product Name'] not in st.session_state.wishlist:
                        st.session_state.wishlist.append(row['Product Name'])
                        st.success(f"{row['Product Name']} added to your Wishlist!")

            # Right column for product image
            with col2:
                if pd.notna(row['Image URL']) and row['Image URL'].startswith('http'):
                    st.image(row['Image URL'], caption=row['Product Name'], use_container_width=True)
                else:
                    st.text("No Image Available")

# Display Wishlist
if st.sidebar.button("View Wishlist"):
    st.sidebar.subheader("Your Wishlist")
    if 'wishlist' in st.session_state and st.session_state.wishlist:
        st.sidebar.write(st.session_state.wishlist)
    else:
        st.sidebar.write("Your wishlist is empty.")

# Footer
st.write("---")
st.markdown('<div style="text-align: center; font-size: small;">\u00a9 2025 Product Catalog. Created by Manjeet Reddy Mora.</div>', unsafe_allow_html=True)
