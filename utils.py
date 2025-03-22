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
    Generate a DFD-style squared visualization of the database schema.
    
    Args:
        df (pandas.DataFrame): Processed DataFrame containing the schema data.
        
    Returns:
        plotly.graph_objects.Figure: A Plotly figure for the DFD diagram.
    """
    # Get unique databases, tables, and create a structured hierarchy
    databases = df['Database'].unique()
    
    # Create figure
    fig = go.Figure()
    
    # Set up the layout grid based on the number of databases
    db_count = len(databases)
    
    # Define colors for the different entity types
    db_color = '#FF5733'    # Red for databases
    table_color = '#33A8FF'  # Blue for tables
    column_color = '#33FF57' # Green for columns
    
    # Set up the layout for a hierarchical DFD-style diagram
    # We'll place databases at the top, tables in the middle, and columns at the bottom
    
    # Calculate spacing and dimensions
    y_spacing = 1.0 / (db_count + 1)
    db_x_position = 0.5  # Center of the diagram
    db_width = 0.9 / db_count  # Width proportional to number of databases
    db_height = 0.1
    
    # Draw databases and their tables
    for db_idx, db_name in enumerate(databases):
        # Get tables for this database
        db_tables = df[df['Database'] == db_name]['Table'].unique()
        
        # Calculate the y position for the database
        db_y_pos = 0.9
        
        # Add database rectangle
        fig.add_shape(
            type="rect",
            x0=db_x_position - db_width/2 + (db_idx - db_count/2 + 0.5) * db_width,
            y0=db_y_pos - db_height/2,
            x1=db_x_position - db_width/2 + (db_idx - db_count/2 + 1.5) * db_width,
            y1=db_y_pos + db_height/2,
            line=dict(color="black", width=2),
            fillcolor=db_color,
            opacity=0.7
        )
        
        # Add database label
        fig.add_annotation(
            x=db_x_position + (db_idx - db_count/2 + 0.5) * db_width,
            y=db_y_pos,
            text=f"<b>{db_name}</b>",
            showarrow=False,
            font=dict(size=14, color="white")
        )
        
        # Draw tables for this database
        table_count = len(db_tables)
        table_width = db_width * 0.8  # Slightly narrower than the database
        table_height = 0.08
        table_y_level = 0.7  # Below the database level
        
        for table_idx, table_name in enumerate(db_tables):
            # Calculate x position for this table (centered under the database)
            table_x_center = db_x_position + (db_idx - db_count/2 + 0.5) * db_width
            table_x_offset = (table_idx - table_count/2 + 0.5) * (table_width * 1.2) / max(1, table_count)
            
            # Draw table rectangle
            fig.add_shape(
                type="rect",
                x0=table_x_center + table_x_offset - table_width/2,
                y0=table_y_level - table_height/2,
                x1=table_x_center + table_x_offset + table_width/2,
                y1=table_y_level + table_height/2,
                line=dict(color="black", width=1),
                fillcolor=table_color,
                opacity=0.7
            )
            
            # Add table label
            fig.add_annotation(
                x=table_x_center + table_x_offset,
                y=table_y_level,
                text=f"<b>{table_name}</b>",
                showarrow=False,
                font=dict(size=12, color="white")
            )
            
            # Draw connector line between database and table
            fig.add_shape(
                type="line",
                x0=table_x_center,
                y0=db_y_pos - db_height/2,
                x1=table_x_center + table_x_offset,
                y1=table_y_level + table_height/2,
                line=dict(color="black", width=1, dash="dot")
            )
            
            # Get columns for this table
            table_columns = df[(df['Database'] == db_name) & (df['Table'] == table_name)]['Column'].values
            column_count = len(table_columns)
            column_width = table_width * 0.7  # Narrower than the table
            column_height = 0.06
            column_y_level = 0.5  # Below the table level
            
            # Determine how many columns to show before grouping
            max_visible_columns = 5
            
            if column_count <= max_visible_columns:
                # Show all columns individually
                for col_idx, col_name in enumerate(table_columns):
                    # Calculate column position (arranged horizontally under the table)
                    col_x_center = table_x_center + table_x_offset
                    col_y_offset = (col_idx - column_count/2 + 0.5) * (column_height * 1.5)
                    
                    # Draw column rectangle
                    fig.add_shape(
                        type="rect",
                        x0=col_x_center - column_width/2,
                        y0=column_y_level + col_y_offset - column_height/2,
                        x1=col_x_center + column_width/2,
                        y1=column_y_level + col_y_offset + column_height/2,
                        line=dict(color="black", width=1),
                        fillcolor=column_color,
                        opacity=0.7
                    )
                    
                    # Add column label
                    fig.add_annotation(
                        x=col_x_center,
                        y=column_y_level + col_y_offset,
                        text=f"{col_name}",
                        showarrow=False,
                        font=dict(size=10, color="black")
                    )
                    
                    # Draw connector line between table and column
                    fig.add_shape(
                        type="line",
                        x0=table_x_center + table_x_offset,
                        y0=table_y_level - table_height/2,
                        x1=col_x_center,
                        y1=column_y_level + col_y_offset + column_height/2,
                        line=dict(color="black", width=1, dash="dot")
                    )
            else:
                # Group columns into a single box
                # Draw column rectangle
                fig.add_shape(
                    type="rect",
                    x0=table_x_center + table_x_offset - column_width/2,
                    y0=column_y_level - column_height,
                    x1=table_x_center + table_x_offset + column_width/2,
                    y1=column_y_level + column_height,
                    line=dict(color="black", width=1),
                    fillcolor=column_color,
                    opacity=0.7
                )
                
                # Add column label
                fig.add_annotation(
                    x=table_x_center + table_x_offset,
                    y=column_y_level,
                    text=f"{column_count} Columns",
                    showarrow=False,
                    font=dict(size=10, color="black")
                )
                
                # Draw connector line between table and column group
                fig.add_shape(
                    type="line",
                    x0=table_x_center + table_x_offset,
                    y0=table_y_level - table_height/2,
                    x1=table_x_center + table_x_offset,
                    y1=column_y_level + column_height,
                    line=dict(color="black", width=1, dash="dot")
                )
    
    # Add legend as shapes with text
    legend_shapes = [
        {"label": "Database", "color": db_color, "y": 0.05},
        {"label": "Table", "color": table_color, "y": 0.10},
        {"label": "Column", "color": column_color, "y": 0.15}
    ]
    
    for legend in legend_shapes:
        # Add legend box
        fig.add_shape(
            type="rect",
            x0=0.02,
            y0=legend["y"] - 0.02,
            x1=0.07,
            y1=legend["y"] + 0.02,
            line=dict(color="black", width=1),
            fillcolor=legend["color"],
            opacity=0.7
        )
        
        # Add legend label
        fig.add_annotation(
            x=0.12,
            y=legend["y"],
            text=legend["label"],
            showarrow=False,
            xanchor="left",
            font=dict(size=12, color="black")
        )
    
    # Set up the layout
    fig.update_layout(
        title='Database Schema DFD Diagram',
        showlegend=False,
        plot_bgcolor='white',
        height=700,
        xaxis=dict(
            showgrid=False, 
            zeroline=False, 
            showticklabels=False,
            range=[0, 1]
        ),
        yaxis=dict(
            showgrid=False, 
            zeroline=False, 
            showticklabels=False,
            range=[0, 1],
            scaleanchor="x",
            scaleratio=1
        ),
        margin=dict(l=20, r=20, t=40, b=20)
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
