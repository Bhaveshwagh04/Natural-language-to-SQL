import streamlit as st
from langchain.llms import Ollama
import sqlite3
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as pl

database_path = 'abc_cesl_final_data_acsentsarthi.db'

prompt_template = """
You are an expert SQL developer and data visualization specialist. Your role is to accurately translate user questions into optimized SQL queries and recommend the best visualization type for effective data interpretation. The database, named `tml_cesl_final_data_acsentsarthi.db`, contains the following three key tables:

You are an expert in Natural Language Processing (NLP) to SQL query generation.
 
Your task is to convert a natural language request into an optimized SQL query. The query should strictly follow SQL syntax and best practices while handling missing fields and edge cases effectively.
 
Guidelines:
Understand the User's Intent
 
Carefully analyze the request to identify the required fields, filters, conditions, and operators.
Distinguish between search, aggregation, and filtering tasks.
SQL Query Construction
 
 1. Use standard SQL syntax without backticks (\\) around field names.
 2. Use SQL features such as DISTINCT, JOIN, LAG, LEAD and SUBQUERIES.
 3. If uniqueness is required, use **'GROUP BY'** or **'DISTINCT'**.
 4. Use SELECT statements to fetch relevant fields.
 5. Apply filtering conditions correctly using WHERE.
 6. Implement aggregations (e.g., AVG(), SUM(), COUNT(), MIN(), MAX()) following Elasticsearch SQL standards.
 7. The output should contain **only one** valid ELK SQL query without additional text.
 8. Use 'date_histogram' aggregation to group data by month.
 9. Return only aggregated results without individual documents.
 10. Optionally, allow filtering for a specific year.
 11. The output should be the ELK SQL query that starts with **SELECT...**
Question: {question}
Query Language:SQL
Answer:
 
[The output should be a single, valid SQL query in one line, without line breaks or additional text.]

"""

def get_ollama_response(question, prompt):
    llm = Ollama(model="mistral")  
    response = llm.invoke(f"{prompt}\nQuestion: {question}\nAnswer:")
    return response

def read_sql_query(sql, db):
    conn = sqlite3.connect(db)
    df = pd.read_sql_query(sql, conn)
    conn.close()
    return df

def get_sql_query_from_response(response):
    try:
        query_start = response.index('SELECT')  
        query_end = response.index(';') + 1  
        sql_query = response[query_start:query_end]  
        return sql_query
    except ValueError:
        st.error("Could not extract SQL query from the response.")
        st.write("Response:")
        st.write(response)
        return None

def determine_chart_type(df):
    """
    Determine the most suitable chart type based on the structure of the DataFrame.

    Parameters:
    df (pd.DataFrame): The input DataFrame containing data to be visualized.

    Returns:
    str: The suggested chart type. Returns None if no suitable chart type is found.

    Raises:
    ValueError: If the input is not a pandas DataFrame or if the DataFrame is empty.
    """
    if not isinstance(df, pd.DataFrame):
        raise ValueError("Input must be a pandas DataFrame.")
    if df.empty:
        raise ValueError("Input DataFrame is empty.")

    num_cols = df.select_dtypes(include=['int64', 'float64']).columns
    cat_cols = df.select_dtypes(include=['object', 'category']).columns

    # Check for Pie Chart: 1 categorical + 1 numerical, limited categories (&lt;=10)
    if len(df.columns) == 2 and len(num_cols) == 1 and len(cat_cols) == 1 and len(df) <= 10:
       return 'pie'

    # Check for Line Chart: Time-based or sequential data with at least one numerical column
    if len(df.columns) >= 2 and len(num_cols) > 0:
        time_columns = [col.lower() for col in df.columns]
        if any(word in time_columns for word in ['month', 'year', 'date', 'time', 'day']):
            return 'line'

    # Check for Scatter Plot: At least 2 numerical columns
    if len(num_cols) >= 2:
        return 'scatter'

    # Check for Histogram: Only 1 numerical column
    if len(df.columns) == 1 and len(num_cols) == 1:
        return 'histogram'

    # Check for Heatmap: Only numerical data with multiple columns
    if len(df.columns) > 1 and len(num_cols) == len(df.columns):
        return 'heatmap'

    # Check for Bubble Chart: At least 3 numerical columns
    if len(num_cols) >= 3:
        return 'bubble'

    # Check for Radar Chart: 1 categorical + multiple numerical columns
    if len(df.columns) > 2 and len(num_cols) > 1 and len(cat_cols) == 1:
        return 'radar'

    # Check for Bar Chart: 1 categorical + 1 numerical, or multiple categorical columns
    if (len(df.columns) == 2 and len(num_cols) == 1 and len(cat_cols) == 1) or 
        (len(df.columns) > 2 and len(cat_cols) > 0 and len(num_cols) > 0)):
        return 'bar'

    # Check for Area Chart: 1 categorical + 1 numerical, or multiple numerical columns
    if (len(df.columns) == 2 and len(num_cols) == 1 and len(cat_cols) == 1) or 
        (len(df.columns) > 2 and len(num_cols) > 0)):
        return 'area'

    # Check for Dot Plot: 1 categorical + 1 numerical
    if len(df.columns) == 2 and len(num_cols) == 1 and len(cat_cols) == 1:
        return 'dot'

    # Check for Treemap: 1 categorical + 1 numerical
    if len(df.columns) == 2 and len(num_cols) == 1 and len(cat_cols) == 1:
        return 'treemap'

    # Check for Gauge Chart: 1 categorical + 1 numerical, with few rows (&lt;=5)
    if len(df.columns) == 2 and len(num_cols) == 1 and len(cat_cols) == 1 and len(df) &lt;= 5:
        return 'gauge'

    # Default case
    return None

def generate_chart(df, chart_type, title=None, x_axis_label=None, y_axis_label=None, color_scale=None, bin_size=None):
    """
    Generate a chart based on the chart type.
    
    Parameters:
    df (pd.DataFrame): The input DataFrame.
    chart_type (str): The chart type ('bar', 'pie', 'line', 'scatter', 'heatmap', 'histogram', 'boxplot', 'violinplot', 'densityplot', 'treemap', 'sunburst', 'waterfall', 'funnel', 'sankey').
    title (str): The chart title.
    x_axis_label (str): The x-axis label.
    y_axis_label (str): The y-axis label.
    color_scale (str): The color scale for heatmaps.
    bin_size (int): The bin size for histograms.
    """
    if chart_type is None:
        st.write("No suitable chart type determined for this data.")
        return
    
    if df.empty:
        st.write("The input DataFrame is empty.")
        return
    
    if chart_type == 'bar':
        fig = px.bar(df, x=df.columns[0], y=df.columns[1],
                     title=title if title else f"{df.columns[0]} vs. {df.columns[1]}",
                     template="plotly_white", color=df.columns[0])
        fig.update_xaxes(title=x_axis_label if x_axis_label else df.columns[0])
        fig.update_yaxes(title=y_axis_label if y_axis_label else df.columns[1])
    elif chart_type == 'pie':
        fig = px.pie(df, names=df.columns[0], values=df.columns[1],
                     title=title if title else f"Distribution of {df.columns[0]}",
                     template="plotly_white")
    elif chart_type == 'line':
        fig = px.line(df, x=df.columns[0], y=df.columns[1],
                      title=title if title else f"{df.columns[1]} Over {df.columns[0]}",
                      template="plotly_white", markers=True)
        fig.update_xaxes(title=x_axis_label if x_axis_label else df.columns[0])
        fig.update_yaxes(title=y_axis_label if y_axis_label else df.columns[1])
    elif chart_type == 'scatter':
        fig = px.scatter(df, x=df.columns[0], y=df.columns[1],
                         title=title if title else f"{df.columns[0]} vs. {df.columns[1]}",
                         template="plotly_white")
        fig.update_xaxes(title=x_axis_label if x_axis_label else df.columns[0])
        fig.update_yaxes(title=y_axis_label if y_axis_label else df.columns[1])
    elif chart_type == 'heatmap':
        fig = px.imshow(df.pivot_table(index=df.columns[0], columns=df.columns[1], values=df.columns[2]),
                         text_auto=True,
                         title=title if title else f"Heatmap of {df.columns[0]} vs. {df.columns[1]}",
                         template="plotly_white",
                         color_continuous_scale=color_scale if color_scale else "Viridis")
    elif chart_type == 'histogram':
        fig = px.histogram(df, x=df.columns[0],
                           title=title if title else f"Histogram of {df.columns[0]}",
                           template="plotly_white",
                           nbins=bin_size if bin_size else 10)
        fig.update_xaxes(title=x_axis_label if x_axis_label else df.columns[0])
    elif chart_type == 'boxplot':
        fig = px.box(df, x=df.columns[0], y=df.columns[1],
                     title=title if title else f"Boxplot of {df.columns[0]} vs. {df.columns[1]}",
                     template="plotly_white")
        fig.update_xaxes(title=x_axis_label if x_axis_label else df.columns[0])
        fig.update_yaxes(title=y_axis_label if y_axis_label else df.columns[1])
    elif chart_type == 'violinplot':
        fig = px.violin(df, x=df.columns[0], y=df.columns[1],
                        title=title if title else f"Violinplot of {df.columns[0]} vs. {df.columns[1]}",
                        template="plotly_white")
        fig.update_xaxes(title=x_axis_label if x_axis_label else df.columns[0])
        fig.update_yaxes(title=y_axis_label if y_axis_label else df.columns[1])
    elif chart_type == 'densityplot':
        fig = px.density_heatmap(df, x=df.columns[0], y=df.columns[1],
                                 title=title if title else f"Densityplot of {df.columns[0]} vs. {df.columns[1]}",
                                 template="plotly_white")
        fig.update_xaxes(title=x_axis_label if x_axis_label else df.columns[0])
        fig.update_yaxes(title=y_axis_label if y_axis_label else df.columns[1])
    elif chart_type == 'treemap':
        fig = px.treemap(df, names=df.columns[0], parents=df.columns[1], values=df.columns[2],
                         title=title if title else f"Treemap of {df.columns[0]} vs. {df.columns[1]}",
                         template="plotly_white")
    elif chart_type == 'sunburst':
        fig = px.sunburst(df, names=df.columns[0], parents=df.columns[1], values=df.columns[2],
                          title=title if title else f"Sunburst of {df.columns[0]} vs. {df.columns[1]}",
                          template="plotly_white")
    elif chart_type == 'waterfall':
        fig = px.waterfall(df, x=df.columns[0], y=df.columns[1],
                            title=title if title else f"Waterfall of {df.columns[0]} vs. {df.columns[1]}",
                            template="plotly_white")
        fig.update_xaxes(title=x_axis_label if x_axis_label else df.columns[0])
        fig.update_yaxes(title=y_axis_label if y_axis_label else df.columns[1])
    elif chart_type == 'funnel':
        fig = px.funnel(df, x=df.columns[0], y=df.columns[1],
                         title=title if title else f"Funnel of {df.columns[0]} vs. {df.columns[1]}",
                         template="plotly_white")
        fig.update_xaxes(title=x_axis_label if x_axis_label else df.columns[0])
        fig.update_yaxes(title=y_axis_label if y_axis_label else df.columns[1])
    elif chart_type == 'sankey':
        fig = px.sankey(df, source=df.columns[0], target=df.columns[1], value=df.columns[2],
                         title=title if title else f"Sankey of {df.columns[0]} vs. {df.columns[1]}",
                         template="plotly_white")
    
    fig.update_layout(plot_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig, use_container_width=True)

st.set_page_config(page_title="SQL Query Retrieval App", layout="wide")

st.markdown("""
    &lt;h1 style="color: purple; text-align: center;">
        📊 DataQuery Pro: Insights at Your Command 📊
    &lt;/h1>
    """, unsafe_allow_html=True)

with st.container():
    st.subheader("What are you looking for?")
    
    col1, col2 = st.columns([3, 1], gap="small")
    
    with col1:
        question = st.text_input("Input your question here:", key="input", placeholder="Type here...")
    
    with col2:
        st.write("")  
        submit = st.button("Retrieve Data", help="Click to submit your question.")

if submit and question:
    response = get_ollama_response(question, prompt_template)
    st.write("Response:")
    st.write(response)
    sql_query = get_sql_query_from_response(response)
    
    if sql_query:
        st.code(sql_query, language='sql')
        df = read_sql_query(sql_query, database_path)
        
        if not df.empty:
            col_data, col_chart = st.columns(2)
            with col_data:
                st.subheader("Query Results:")
                st.dataframe(df)
            chart_type = determine_chart_type(df)
            
            if chart_type:
                with col_chart:
                    st.subheader("Visualization:")
                    generate_chart(df, chart_type)  
        else:
            st.write("No results found for the given query.")
    else:
        st.write("No valid SQL query could be extracted from the response.")