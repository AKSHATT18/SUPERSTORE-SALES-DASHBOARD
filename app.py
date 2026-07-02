import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import requests
from streamlit_option_menu import option_menu

# Page configuration
st.set_page_config(
    page_title="Superstore Sales Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        padding: 0rem 1rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
    </style>
    """, unsafe_allow_html=True)

# Initialize session state
if 'data' not in st.session_state:
    st.session_state.data = None
if 'filtered_data' not in st.session_state:
    st.session_state.filtered_data = None

# Sidebar Navigation
with st.sidebar:
    st.title("🏪 Superstore Dashboard")
    st.divider()
    
    selected = option_menu(
        menu_title="Navigation",
        options=["Dashboard", "Sales Analysis", "Product Performance", "Shipping Analysis", "Location Analysis", "Data Export"],
        icons=["graph-up", "bar-chart", "box", "truck", "map", "download"],
        menu_icon="cast",
        default_index=0
    )

# Load sample data function
@st.cache_data
def load_sample_data():
    """Load sample superstore data"""
    data = {
        'Order ID': ['ORD-001', 'ORD-002', 'ORD-003', 'ORD-004', 'ORD-005'],
        'Order Date': pd.date_range('2024-01-01', periods=5),
        'Sales': [500, 1200, 800, 1500, 950],
        'Quantity': [2, 4, 3, 5, 2],
        'Profit': [100, 300, 150, 400, 200],
        'Category': ['Technology', 'Furniture', 'Office Supplies', 'Technology', 'Furniture'],
        'Region': ['West', 'East', 'Central', 'South', 'West'],
        'Ship Mode': ['Standard', 'Second Class', 'First Class', 'Standard', 'Same Day'],
        'Customer Name': ['John Doe', 'Jane Smith', 'Bob Johnson', 'Alice Brown', 'Charlie Wilson']
    }
    return pd.DataFrame(data)

# Load data
if st.session_state.data is None:
    st.session_state.data = load_sample_data()

data = st.session_state.data

# ===== DASHBOARD PAGE =====
if selected == "Dashboard":
    st.title("📊 Sales Dashboard Overview")
    
    # Key Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_sales = data['Sales'].sum()
        st.metric("Total Sales", f"${total_sales:,.2f}", delta="↑ 12%")
    
    with col2:
        total_profit = data['Profit'].sum()
        st.metric("Total Profit", f"${total_profit:,.2f}", delta="↑ 8%")
    
    with col3:
        total_orders = len(data)
        st.metric("Total Orders", total_orders, delta="↑ 5")
    
    with col4:
        avg_order = data['Sales'].mean()
        st.metric("Avg Order Value", f"${avg_order:,.2f}", delta="→ 0%")
    
    st.divider()
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        # Sales by Category
        sales_by_category = data.groupby('Category')['Sales'].sum().reset_index()
        fig_category = px.pie(sales_by_category, values='Sales', names='Category', 
                             title="Sales by Category", hole=0.4)
        st.plotly_chart(fig_category, use_container_width=True)
    
    with col2:
        # Sales by Region
        sales_by_region = data.groupby('Region')['Sales'].sum().reset_index()
        fig_region = px.bar(sales_by_region, x='Region', y='Sales', 
                           title="Sales by Region", color='Sales',
                           color_continuous_scale='Blues')
        st.plotly_chart(fig_region, use_container_width=True)
    
    # Sales Trend
    sales_trend = data.groupby('Order Date')['Sales'].sum().reset_index()
    fig_trend = px.line(sales_trend, x='Order Date', y='Sales', 
                       title="Sales Trend Over Time", markers=True)
    st.plotly_chart(fig_trend, use_container_width=True)

# ===== SALES ANALYSIS PAGE =====
elif selected == "Sales Analysis":
    st.title("📈 Sales Analysis")
    
    col1, col2 = st.columns([1, 3])
    
    with col1:
        st.subheader("Filters")
        selected_category = st.multiselect("Category", data['Category'].unique(), default=data['Category'].unique())
        selected_region = st.multiselect("Region", data['Region'].unique(), default=data['Region'].unique())
    
    with col2:
        # Filter data
        filtered = data[(data['Category'].isin(selected_category)) & (data['Region'].isin(selected_region))]
        
        # Profit by Category
        profit_data = filtered.groupby('Category')[['Sales', 'Profit']].sum().reset_index()
        fig = px.bar(profit_data, x='Category', y=['Sales', 'Profit'], 
                    title="Sales vs Profit by Category", barmode='group')
        st.plotly_chart(fig, use_container_width=True)
    
    # Sales metrics
    st.divider()
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Filtered Sales", f"${filtered['Sales'].sum():,.2f}")
    with col2:
        st.metric("Filtered Profit", f"${filtered['Profit'].sum():,.2f}")
    with col3:
        profit_margin = (filtered['Profit'].sum() / filtered['Sales'].sum() * 100) if filtered['Sales'].sum() > 0 else 0
        st.metric("Profit Margin", f"{profit_margin:.1f}%")

# ===== PRODUCT PERFORMANCE PAGE =====
elif selected == "Product Performance":
    st.title("📦 Product Performance")
    
    product_stats = data.groupby('Category').agg({
        'Sales': 'sum',
        'Profit': 'sum',
        'Quantity': 'sum'
    }).reset_index().sort_values('Sales', ascending=False)
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig = px.bar(product_stats, x='Category', y='Sales', 
                    title="Sales by Product Category", color='Profit',
                    color_continuous_scale='Viridis')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        fig = px.scatter(product_stats, x='Quantity', y='Profit', size='Sales',
                        hover_name='Category', title="Product Performance Scatter",
                        color='Sales', color_continuous_scale='Blues')
        st.plotly_chart(fig, use_container_width=True)
    
    st.divider()
    st.subheader("Product Statistics Table")
    st.dataframe(product_stats, use_container_width=True)

# ===== SHIPPING ANALYSIS PAGE =====
elif selected == "Shipping Analysis":
    st.title("🚚 Shipping Analysis")
    
    shipping_stats = data.groupby('Ship Mode').agg({
        'Sales': 'sum',
        'Quantity': 'count',
        'Order ID': 'count'
    }).reset_index().rename(columns={'Order ID': 'Number of Orders'})
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig = px.pie(shipping_stats, values='Sales', names='Ship Mode',
                    title="Sales Distribution by Shipping Mode")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        fig = px.bar(shipping_stats, x='Ship Mode', y='Number of Orders',
                    title="Orders by Shipping Mode", color='Number of Orders',
                    color_continuous_scale='Plasma')
        st.plotly_chart(fig, use_container_width=True)
    
    st.divider()
    st.subheader("Shipping Statistics")
    st.dataframe(shipping_stats, use_container_width=True)

# ===== LOCATION ANALYSIS PAGE =====
elif selected == "Location Analysis":
    st.title("🗺️ Location Analysis")
    
    location_stats = data.groupby('Region').agg({
        'Sales': 'sum',
        'Profit': 'sum',
        'Order ID': 'count'
    }).reset_index().rename(columns={'Order ID': 'Orders'}).sort_values('Sales', ascending=False)
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig = px.bar(location_stats, x='Region', y='Sales',
                    title="Sales by Region", color='Profit',
                    color_continuous_scale='Reds')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        fig = px.scatter(location_stats, x='Orders', y='Profit', size='Sales',
                        hover_name='Region', title="Region Performance",
                        color='Sales', color_continuous_scale='Blues')
        st.plotly_chart(fig, use_container_width=True)
    
    st.divider()
    st.subheader("Location Statistics")
    st.dataframe(location_stats, use_container_width=True)

# ===== DATA EXPORT PAGE =====
elif selected == "Data Export":
    st.title("📥 Data Export")
    
    st.subheader("Export Options")
    
    col1, col2 = st.columns(2)
    
    with col1:
        export_format = st.selectbox("Select Format", ["CSV", "Excel"])
    
    with col2:
        if st.button("📥 Download Data", key="download_btn"):
            if export_format == "CSV":
                csv = data.to_csv(index=False)
                st.download_button(
                    label="Download CSV",
                    data=csv,
                    file_name=f"superstore_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
            else:
                st.info("Excel export requires openpyxl library. Use CSV for now.")
    
    st.divider()
    st.subheader("Data Preview")
    st.dataframe(data, use_container_width=True)
    
    st.divider()
    st.subheader("Summary Statistics")
    st.dataframe(data.describe(), use_container_width=True)

# Footer
st.divider()
col1, col2, col3 = st.columns(3)
with col1:
    st.caption("© 2024 Akshat Upadhyay")
with col2:
    st.caption("📧 akshattup2004@gmail.com")
with col3:
    st.caption("🔗 [GitHub](https://github.com/AKSHATT18)")
