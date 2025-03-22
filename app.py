import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from utils import process_csv, generate_network_graph, generate_stats

# Set page configuration
st.set_page_config(
    page_title="Database Schema Visualizer",
    page_icon="📊",
    layout="wide"
)

# App title and description
st.title("Database Schema Visualizer")
st.markdown("Upload a CSV file with database structure to visualize the relationships between databases, tables, and columns.")

# File upload
uploaded_file = st.file_uploader("Choose a CSV file", type=["csv"])

# Sample file format information
with st.expander("CSV File Format"):
    st.markdown("""
    Your CSV file should have the following format:
    
    | Database | Table | Column |
    |----------|-------|--------|
    | DatabaseA | Table1 | Column1 |
    | DatabaseA | Table1 | Column2 |
    | DatabaseA | Table2 | Column1 |
    | ... | ... | ... |
    
    Make sure your CSV file has headers named 'Database', 'Table', and 'Column'.
    """)

# Process the uploaded file
if uploaded_file is not None:
    try:
        # Read the CSV file
        df = pd.read_csv(uploaded_file)
        
        # Validate the CSV structure
        required_columns = ["Database", "Table", "Column"]
        if not all(col in df.columns for col in required_columns):
            st.error("The CSV file must contain 'Database', 'Table', and 'Column' headers. Please check your file format and try again.")
        else:
            # Process the data
            databases, tables, columns, df_processed = process_csv(df)
            
            # Create tabs for different visualizations
            tab1, tab2, tab3 = st.tabs(["Schema Diagram", "Statistics", "Raw Data"])
            
            with tab1:
                st.header("Schema Visualization")
                
                # Sidebar for filters in tab1
                with st.sidebar:
                    st.header("Filters")
                    
                    # Database filter
                    selected_db = st.multiselect(
                        "Select Databases",
                        options=databases,
                        default=databases
                    )
                    
                    # Table filter (depends on selected databases)
                    if selected_db:
                        available_tables = df_processed[df_processed['Database'].isin(selected_db)]['Table'].unique().tolist()
                        selected_tables = st.multiselect(
                            "Select Tables",
                            options=available_tables,
                            default=available_tables
                        )
                    else:
                        selected_tables = []
                
                # Filter data based on selections
                filtered_df = df_processed.copy()
                if selected_db:
                    filtered_df = filtered_df[filtered_df['Database'].isin(selected_db)]
                if selected_tables:
                    filtered_df = filtered_df[filtered_df['Table'].isin(selected_tables)]
                
                if not filtered_df.empty:
                    # Generate and display the network graph
                    fig = generate_network_graph(filtered_df)
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning("No data to display with the current filters.")
            
            with tab2:
                st.header("Database Statistics")
                
                # Generate and display statistics
                stats_df, db_count_fig, table_count_fig, column_dist_fig = generate_stats(df_processed)
                
                # Display summary statistics
                st.subheader("Summary")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Databases", len(databases))
                with col2:
                    st.metric("Tables", len(tables))
                with col3:
                    st.metric("Columns", len(columns))
                
                # Display detailed statistics
                st.subheader("Detailed Statistics")
                st.dataframe(stats_df)
                
                # Display charts
                st.subheader("Tables per Database")
                st.plotly_chart(db_count_fig, use_container_width=True)
                
                st.subheader("Columns per Table")
                st.plotly_chart(table_count_fig, use_container_width=True)
                
                st.subheader("Column Distribution")
                st.plotly_chart(column_dist_fig, use_container_width=True)
            
            with tab3:
                st.header("Raw Data")
                st.dataframe(df_processed)
                
    except Exception as e:
        st.error(f"An error occurred while processing the file: {e}")
else:
    # Display sample data if no file is uploaded
    st.info("Upload a CSV file to visualize the database schema.")
    
    # If there's sample data from the attached file, show it
    try:
        sample_df = pd.read_csv("attached_assets/DB.csv")
        st.subheader("Sample Data Preview")
        st.dataframe(sample_df)
        
        # Show a sample visualization with the attached data
        st.subheader("Sample Visualization")
        databases, tables, columns, sample_processed = process_csv(sample_df)
        fig = generate_network_graph(sample_processed)
        st.plotly_chart(fig, use_container_width=True)
        
    except Exception as e:
        pass
