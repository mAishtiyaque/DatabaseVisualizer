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
    similar to a nested table structure with databases containing tables,
    and tables containing columns.
    
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
    vertical_padding = 50  # Padding between database and tables (vertical)
    
    # Define dimensions
    db_height = 40  # Height of database box
    table_header_height = 30  # Height of table header
    row_height = 25  # Height of each column row
    table_width = 150  # Width of each table
    
    # Define colors
    db_color = '#99CCFF'  # Light blue for databases
    table_header_color = '#CCCCCC'  # Gray for table headers
    even_row_color = '#FFFFFF'  # White for even rows
    odd_row_color = '#F5F5F5'  # Light gray for odd rows
    border_color = '#000000'  # Black for borders
    db_name_color = '#000080'  # Navy for database names
    table_name_color = '#000000'  # Black for table names
    column_name_color = '#000000'  # Black for column names
    
    # Calculate total width needed
    total_width = 0
    db_widths = {}  # Store width for each database
    
    for db_name in databases:
        # Get tables for this database
        db_tables = df[df['Database'] == db_name]['Table'].unique()
        # Calculate width based on number of tables
        db_width = len(db_tables) * (table_width + table_padding) - table_padding
        db_widths[db_name] = max(150, db_width)  # Minimum width of 150px
        total_width += db_widths[db_name] + db_padding
    
    # Adjust for last padding
    total_width -= db_padding
    
    # Set initial x position
    current_x = 50  # Starting position
    
    # Calculate total height needed (will be updated as we go)
    max_height = 0
    
    # Draw each database and its tables
    for db_idx, db_name in enumerate(databases):
        # Get tables for this database
        db_tables = df[df['Database'] == db_name]['Table'].unique()
        
        # Draw database rectangle
        fig.add_shape(
            type="rect",
            x0=current_x,
            y0=50,
            x1=current_x + db_widths[db_name],
            y1=50 + db_height,
            line=dict(color=border_color, width=2),
            fillcolor=db_color
        )
        
        # Add database name
        fig.add_annotation(
            x=current_x + 20,
            y=50 + db_height/2,
            text=f"<b>{db_name}</b>",
            showarrow=False,
            font=dict(size=14, color=db_name_color),
            xanchor="left",
            yanchor="middle"
        )
        
        # Initial position for tables
        table_x = current_x
        
        # Draw tables for this database
        for table_idx, table_name in enumerate(db_tables):
            # Get columns for this table
            table_columns = df[(df['Database'] == db_name) & (df['Table'] == table_name)]['Column'].values
            
            # Calculate table height based on number of columns
            table_height = table_header_height + (len(table_columns) * row_height)
            
            # Calculate y position for this table (all tables start at the same y level)
            table_y = 50 + db_height + vertical_padding
            
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
            
            # Update the maximum height if needed
            current_height = table_y + table_height
            max_height = max(max_height, current_height)
            
            # Move to the next table position
            table_x += table_width + table_padding
        
        # Move x position for the next database
        current_x += db_widths[db_name] + db_padding
    
    # Add outer border for the entire diagram
    fig.add_shape(
        type="rect",
        x0=30,
        y0=30,
        x1=current_x - db_padding + 20,
        y1=max_height + 30,
        line=dict(color=border_color, width=3),
        fillcolor=None
    )
    
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
