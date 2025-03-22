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
    Generate a network graph visualization of the database schema.
    
    Args:
        df (pandas.DataFrame): Processed DataFrame containing the schema data.
        
    Returns:
        plotly.graph_objects.Figure: A Plotly figure for the network graph.
    """
    # Create a graph
    G = nx.Graph()
    
    # Add nodes for databases, tables, and columns
    for db in df['Database'].unique():
        G.add_node(db, type='database')
    
    for _, row in df.iterrows():
        table_node = f"{row['Database']}.{row['Table']}"
        column_node = f"{row['Database']}.{row['Table']}.{row['Column']}"
        
        # Add nodes if they don't exist
        if not G.has_node(table_node):
            G.add_node(table_node, type='table')
        
        if not G.has_node(column_node):
            G.add_node(column_node, type='column')
        
        # Add edges
        G.add_edge(row['Database'], table_node)
        G.add_edge(table_node, column_node)
    
    # Use a layout algorithm to position nodes
    pos = nx.spring_layout(G, seed=42)
    
    # Prepare node data for Plotly
    node_x = []
    node_y = []
    node_text = []
    node_color = []
    node_size = []
    
    for node in G.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
        
        # Set node properties based on type
        node_type = G.nodes[node].get('type', '')
        
        if node_type == 'database':
            node_text.append(f"Database: {node}")
            node_color.append('#FF5733')  # Red for databases
            node_size.append(30)
        elif node_type == 'table':
            db, table = node.split('.')
            node_text.append(f"Table: {table}<br>Database: {db}")
            node_color.append('#33A8FF')  # Blue for tables
            node_size.append(20)
        else:  # column
            db, table, column = node.split('.')
            node_text.append(f"Column: {column}<br>Table: {table}<br>Database: {db}")
            node_color.append('#33FF57')  # Green for columns
            node_size.append(10)
    
    # Create node trace
    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers',
        hoverinfo='text',
        text=node_text,
        marker=dict(
            showscale=False,
            color=node_color,
            size=node_size,
            line=dict(width=1, color='#888')
        )
    )
    
    # Create edge traces
    edge_x = []
    edge_y = []
    
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])
    
    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=0.5, color='#888'),
        hoverinfo='none',
        mode='lines'
    )
    
    # Create the figure
    fig = go.Figure(
        data=[edge_trace, node_trace],
        layout=go.Layout(
            title='Database Schema Relationship Graph',
            showlegend=False,
            hovermode='closest',
            margin=dict(b=20, l=5, r=5, t=40),
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            height=600
        )
    )
    
    # Add legend manually
    fig.add_trace(go.Scatter(
        x=[None], y=[None],
        mode='markers',
        marker=dict(size=15, color='#FF5733'),
        showlegend=True,
        name='Database'
    ))
    
    fig.add_trace(go.Scatter(
        x=[None], y=[None],
        mode='markers',
        marker=dict(size=15, color='#33A8FF'),
        showlegend=True,
        name='Table'
    ))
    
    fig.add_trace(go.Scatter(
        x=[None], y=[None],
        mode='markers',
        marker=dict(size=15, color='#33FF57'),
        showlegend=True,
        name='Column'
    ))
    
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
