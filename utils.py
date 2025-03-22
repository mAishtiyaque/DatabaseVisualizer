import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import networkx as nx

def process_csv(df):
    """
    Process the CSV data to extract databases, tables, and columns.
    
    Args:
        df (pandas.DataFrame): DataFrame containing the CSV data.
        
    Returns:
        tuple: Lists of unique databases, tables, columns, and processed DataFrame.
    """
    # Ensure column names are correct (case-insensitive)
    df.columns = [col.capitalize() for col in df.columns]
    
    # Rename columns if they don't match expected names
    column_mapping = {
        'Database': 'Database',
        'Table': 'Table',
        'Column': 'Column'
    }
    
    # Apply mapping for expected column names
    df = df.rename(columns={col: column_mapping[col] for col in df.columns if col in column_mapping})
    
    # Get unique values
    databases = df['Database'].unique().tolist()
    tables = df['Table'].unique().tolist()
    columns = df['Column'].unique().tolist()
    
    # Create a processed DataFrame
    df_processed = df.copy()
    
    return databases, tables, columns, df_processed

def generate_network_graph(df):
    """
    Generate a table-based visualization of the database schema,
    with each database in its own bordered section and database name in a small box
    at the top left outside of the rectangle, similar to the example image.
    
    Args:
        df (pandas.DataFrame): Processed DataFrame containing the schema data.
        
    Returns:
        plotly.graph_objects.Figure: A Plotly figure for the table-based schema diagram.
    """
    # Create a new blank figure with a white background
    fig = go.Figure()
    
    # Get unique databases and their tables
    databases = df['Database'].unique()
    
    # Define spacing and positioning parameters
    db_padding = 50  # Padding between databases (horizontal)
    table_padding = 20  # Padding between tables (horizontal)
    vertical_padding = 20  # Padding between database and tables (vertical)
    
    # Define dimensions
    db_name_width = 30  # Width of database name box
    db_name_height = 30  # Height of database name box
    table_header_height = 30  # Height of table header
    row_height = 25  # Height of each column row
    table_width = 150  # Width of each table
    
    # Define colors
    db_border_color = '#000080'  # Navy blue for database borders
    db_name_color = '#000080'  # Navy for database name background
    db_name_text_color = '#FFFFFF'  # White for database name text
    table_header_color = '#CCCCCC'  # Gray for table headers
    even_row_color = '#FFFFFF'  # White for even rows
    odd_row_color = '#F5F5F5'  # Light gray for odd rows
    border_color = '#000000'  # Black for borders
    table_name_color = '#000000'  # Black for table names
    column_name_color = '#000000'  # Black for column names
    
    # Set initial positions
    current_x = 80  # Starting position (moved right to make room for DB name box)
    
    # Calculate total height needed (will be updated as we go)
    max_height = 0
    db_max_heights = {}  # Track the maximum height of each database section
    
    # First pass: Calculate widths and heights for each database
    db_widths = {}  # Store width for each database
    
    for db_name in databases:
        # Get tables for this database
        db_tables = df[df['Database'] == db_name]['Table'].unique()
        
        # Calculate width based on number of tables
        db_width = len(db_tables) * (table_width + table_padding) - table_padding
        db_widths[db_name] = max(150, db_width)  # Minimum width of 150px
        
        # Calculate maximum height for this database
        max_table_height = 0
        for table_name in db_tables:
            # Get columns for this table
            table_columns = df[(df['Database'] == db_name) & (df['Table'] == table_name)]['Column'].values
            # Calculate table height
            table_height = table_header_height + (len(table_columns) * row_height)
            max_table_height = max(max_table_height, table_height)
        
        # Store the maximum height for this database section
        db_max_heights[db_name] = max_table_height + vertical_padding + 20  # Extra padding
    
    # Second pass: Draw the visualization
    for db_idx, db_name in enumerate(databases):
        # Get tables for this database
        db_tables = df[df['Database'] == db_name]['Table'].unique()
        
        # Top position for this database section
        db_top = 50
        
        # Bottom position determined by the maximum table height in this database
        db_bottom = db_top + db_max_heights[db_name] + vertical_padding
        
        # Left and right positions for the database border
        db_left = current_x
        db_right = current_x + db_widths[db_name] + table_padding
        
        # Draw database name box (small box at top left OUTSIDE the main rectangle)
        fig.add_shape(
            type="rect",
            x0=db_left - db_name_width,  # Outside to the left
            y0=db_top,
            x1=db_left,  # Up to the main rectangle's left edge
            y1=db_top + db_name_height,
            line=dict(color=border_color, width=1),
            fillcolor=db_name_color
        )
        
        # Add database name in the small box
        fig.add_annotation(
            x=db_left - db_name_width/2,
            y=db_top + db_name_height/2,
            text=f"<b>{db_name}</b>",
            showarrow=False,
            font=dict(size=14, color=db_name_text_color),
            xanchor="center",
            yanchor="middle"
        )
        
        # Draw database border (the outer rectangle)
        fig.add_shape(
            type="rect",
            x0=db_left,
            y0=db_top,
            x1=db_right,
            y1=db_bottom,
            line=dict(color=db_border_color, width=2),
            fillcolor=None
        )
        
        # Initial position for tables
        table_x = db_left + 20  # Start a bit to the right of the left border
        
        # Draw tables for this database
        for table_idx, table_name in enumerate(db_tables):
            # Get columns for this table
            table_columns = df[(df['Database'] == db_name) & (df['Table'] == table_name)]['Column'].values
            
            # Calculate table height based on number of columns
            table_height = table_header_height + (len(table_columns) * row_height)
            
            # Calculate y position for this table (all tables start at the same y level)
            table_y = db_top + vertical_padding
            
            # Draw table header
            fig.add_shape(
                type="rect",
                x0=table_x,
                y0=table_y,
                x1=table_x + table_width,
                y1=table_y + table_header_height,
                line=dict(color=border_color, width=1),
                fillcolor=table_header_color
            )
            
            # Add table name
            fig.add_annotation(
                x=table_x + 10,
                y=table_y + table_header_height/2,
                text=f"<b>{table_name}</b>",
                showarrow=False,
                font=dict(size=12, color=table_name_color),
                xanchor="left",
                yanchor="middle"
            )
            
            # Add table columns
            for col_idx, col_name in enumerate(table_columns):
                # Calculate row position
                row_y = table_y + table_header_height + (col_idx * row_height)
                
                # Determine row color (alternating)
                row_color = even_row_color if col_idx % 2 == 0 else odd_row_color
                
                # Draw row background
                fig.add_shape(
                    type="rect",
                    x0=table_x,
                    y0=row_y,
                    x1=table_x + table_width,
                    y1=row_y + row_height,
                    line=dict(color=border_color, width=1),
                    fillcolor=row_color
                )
                
                # Add column name
                fig.add_annotation(
                    x=table_x + 10,
                    y=row_y + row_height/2,
                    text=f"{col_name}",
                    showarrow=False,
                    font=dict(size=10, color=column_name_color),
                    xanchor="left",
                    yanchor="middle"
                )
                
                # Add data type or other info column (e.g., "INT")
                # This is based on your example image which shows column types
                fig.add_shape(
                    type="line",
                    x0=table_x + table_width*0.7,
                    y0=row_y,
                    x1=table_x + table_width*0.7,
                    y1=row_y + row_height,
                    line=dict(color=border_color, width=1)
                )
                
                # Add placeholder for data type
                data_type = "INT"  # Default placeholder type
                fig.add_annotation(
                    x=table_x + table_width*0.85,
                    y=row_y + row_height/2,
                    text=data_type,
                    showarrow=False,
                    font=dict(size=9, color=column_name_color),
                    xanchor="center",
                    yanchor="middle"
                )
            
            # Update maximum height for this database if needed
            current_table_bottom = table_y + table_height
            db_bottom = max(db_bottom, current_table_bottom + vertical_padding)
            
            # Move to the next table position
            table_x += table_width + table_padding
        
        # Update the overall maximum height
        max_height = max(max_height, db_bottom)
        
        # Move x position for the next database
        current_x = db_right + db_padding
    
    # Set up the layout
    fig.update_layout(
        title='Database Schema Visualization',
        plot_bgcolor='white',
        height=max_height + 60,
        width=current_x,
        xaxis=dict(
            showgrid=False, 
            zeroline=False, 
            showticklabels=False,
            range=[0, current_x]
        ),
        yaxis=dict(
            showgrid=False, 
            zeroline=False, 
            showticklabels=False,
            range=[0, max_height + 60],
            scaleanchor="x",
            scaleratio=1
        ),
        margin=dict(l=40, r=40, t=40, b=40),
        showlegend=False
    )
    
    return fig

def generate_stats(df):
    """
    Generate statistics about the database schema.
    
    Args:
        df (pandas.DataFrame): Processed DataFrame containing the schema data.
        
    Returns:
        tuple: Statistics DataFrame and three Plotly figures.
    """
    # Count tables per database
    db_table_counts = df.groupby('Database')['Table'].nunique().reset_index()
    db_table_counts.columns = ['Database', 'Number of Tables']
    
    # Count columns per table
    table_counts = df.groupby(['Database', 'Table'])['Column'].count().reset_index()
    table_counts.columns = ['Database', 'Table', 'Number of Columns']
    
    # Count columns per database
    db_column_counts = df.groupby('Database')['Column'].count().reset_index()
    db_column_counts.columns = ['Database', 'Number of Columns']
    
    # Combine statistics
    stats_df = pd.merge(db_table_counts, db_column_counts, on='Database')
    
    # Create figures
    
    # Tables per database
    db_count_fig = px.bar(
        db_table_counts,
        x='Database',
        y='Number of Tables',
        title='Number of Tables per Database',
        color='Database'
    )
    
    # Columns per table
    table_count_fig = px.bar(
        table_counts,
        x='Table',
        y='Number of Columns',
        color='Database',
        title='Number of Columns per Table',
        barmode='group'
    )
    
    # Column distribution
    col_dist = df.groupby(['Database', 'Table']).size().reset_index(name='Count')
    column_dist_fig = px.histogram(
        col_dist,
        x='Count',
        color='Database',
        title='Distribution of Column Counts per Table',
        labels={'Count': 'Number of Columns', 'frequency': 'Number of Tables'},
        marginal='box'
    )
    
    return stats_df, db_count_fig, table_count_fig, column_dist_fig
