import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from pandas.api.types import (
    is_categorical_dtype,
    is_datetime64_any_dtype,
    is_numeric_dtype,
    is_object_dtype
)

def process_file(uploaded_file):
    try:
        file_extension = uploaded_file.name.split('.')[-1].lower()
        
        if file_extension == "csv":
            df = pd.read_csv(uploaded_file, parse_dates=True, infer_datetime_format=True)
        elif file_extension in ["xls", "xlsx"]:
            df = pd.read_excel(uploaded_file, parse_dates=True)
        else:
            st.error("Unsupported file format")
            return None
        
        for col in df.columns:
            if is_object_dtype(df[col]):
                try:
                    df[col] = pd.to_numeric(df[col], errors='ignore')
                except:
                    pass
        
        return df
    
    except Exception as e:
        st.error(f"Error reading file: {str(e)}")
        return None

def analyze_data(df):
    date_cols = [col for col in df.columns if is_datetime64_any_dtype(df[col])]
    numeric_cols = [col for col in df.columns if is_numeric_dtype(df[col])]
    cat_cols = [col for col in df.columns if is_categorical_dtype(df[col]) or 
                (is_object_dtype(df[col]) and df[col].nunique() < 20)]
    
    return date_cols, numeric_cols, cat_cols

def create_visualizations(df, date_cols, numeric_cols, cat_cols):
    st.header("📊 Custom Visualization Builder")
    
    config_col, viz_col = st.columns([1, 3])
    
    with config_col:
        chart_type = st.selectbox(
            "Select Chart Type",
            ["Scatter", "Line", "Bar", "Histogram", 
             "Box", "Violin", "Heatmap", "3D Scatter",
             "Bubble", "Parallel Categories"]
        )
        
        x_axis = st.selectbox(
            "X-axis",
            df.columns,
            index=0
        )
        
        y_axis = None
        if chart_type not in ["Histogram", "Heatmap", "Parallel Categories"]:
            y_axis = st.selectbox(
                "Y-axis",
                df.columns,
                index=min(1, len(df.columns)-1)
            )
        
        color_dim = st.selectbox(
            "Color by (optional)",
            ["None"] + list(df.columns)
        )
        
        size_dim = None
        if chart_type in ["Scatter", "Bubble", "3D Scatter"]:
            size_dim = st.selectbox(
                "Size by (optional)",
                ["None"] + numeric_cols
            )
        
        z_axis = None
        if chart_type == "3D Scatter":
            z_axis = st.selectbox(
                "Z-axis",
                numeric_cols
            )
        
        aggregation = "raw"
        if chart_type in ["Line", "Bar"] and not is_numeric_dtype(df[x_axis]):
            aggregation = st.selectbox(
                "Aggregation",
                ["count", "sum", "mean", "median"]
            )
        
        nbins = 20
        if chart_type == "Histogram":
            nbins = st.slider("Number of bins", 5, 100, 20)
        
        size_max = 50
        if chart_type == "Bubble":
            size_max = st.slider("Max bubble size", 10, 100, 50)
        
        color_scale = st.selectbox(
            "Color Scale",
            px.colors.named_colorscales(),
            index=px.colors.named_colorscales().index("viridis")
        )
    
    with viz_col:
        try:
            fig = None
            
            if chart_type == "Scatter":
                fig = px.scatter(
                    df,
                    x=x_axis,
                    y=y_axis,
                    color=None if color_dim == "None" else color_dim,
                    size=None if size_dim == "None" else size_dim,
                    color_continuous_scale=color_scale
                )
                
            elif chart_type == "Line":
                if aggregation != "raw":
                    agg_df = df.groupby(x_axis)[y_axis].agg(aggregation).reset_index()
                    fig = px.line(
                        agg_df,
                        x=x_axis,
                        y=y_axis,
                        color=None if color_dim == "None" else color_dim,
                        color_discrete_sequence=px.colors.qualitative.Plotly
                    )
                else:
                    fig = px.line(
                        df,
                        x=x_axis,
                        y=y_axis,
                        color=None if color_dim == "None" else color_dim,
                        color_discrete_sequence=px.colors.qualitative.Plotly
                    )
                    
            elif chart_type == "Bar":
                if aggregation != "raw":
                    agg_df = df.groupby(x_axis)[y_axis].agg(aggregation).reset_index()
                    fig = px.bar(
                        agg_df,
                        x=x_axis,
                        y=y_axis,
                        color=None if color_dim == "None" else color_dim,
                        color_discrete_sequence=px.colors.qualitative.Plotly
                    )
                else:
                    fig = px.bar(
                        df,
                        x=x_axis,
                        y=y_axis,
                        color=None if color_dim == "None" else color_dim,
                        color_discrete_sequence=px.colors.qualitative.Plotly
                    )
                    
            elif chart_type == "Histogram":
                fig = px.histogram(
                    df,
                    x=x_axis,
                    nbins=nbins,
                    color=None if color_dim == "None" else color_dim,
                    marginal="box",
                    color_discrete_sequence=px.colors.qualitative.Plotly
                )
                
            elif chart_type == "Box":
                fig = px.box(
                    df,
                    x=x_axis,
                    y=y_axis,
                    color=None if color_dim == "None" else color_dim,
                    color_discrete_sequence=px.colors.qualitative.Plotly
                )
                
            elif chart_type == "Violin":
                fig = px.violin(
                    df,
                    x=x_axis,
                    y=y_axis,
                    color=None if color_dim == "None" else color_dim,
                    box=True,
                    color_discrete_sequence=px.colors.qualitative.Plotly
                )
                
            elif chart_type == "Heatmap":
                heatmap_df = df.groupby([x_axis, y_axis]).size().reset_index(name='count')
                fig = px.density_heatmap(
                    heatmap_df,
                    x=x_axis,
                    y=y_axis,
                    z='count',
                    color_continuous_scale=color_scale
                )
                
            elif chart_type == "3D Scatter":
                fig = px.scatter_3d(
                    df,
                    x=x_axis,
                    y=y_axis,
                    z=z_axis,
                    color=None if color_dim == "None" else color_dim,
                    size=None if size_dim == "None" else size_dim,
                    color_continuous_scale=color_scale
                )
                
            elif chart_type == "Bubble":
                fig = px.scatter(
                    df,
                    x=x_axis,
                    y=y_axis,
                    size=size_dim,
                    color=None if color_dim == "None" else color_dim,
                    size_max=size_max,
                    hover_name=df.index,
                    color_continuous_scale=color_scale
                )
                
            elif chart_type == "Parallel Categories":
                fig = px.parallel_categories(
                    df,
                    dimensions=[x_axis, y_axis] + ([color_dim] if color_dim != "None" else []),
                    color_continuous_scale=color_scale
                )
            
            if fig:
                fig.update_layout(
                    height=600,
                    margin=dict(l=20, r=20, t=40, b=20),
                    showlegend=True
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("Could not generate visualization with current parameters")
                
        except Exception as e:
            st.error(f"Error generating visualization: {str(e)}")
            st.warning("Try different axis selections or check data types")

def main():
    st.set_page_config(page_title="Smart Data Analyzer", layout="wide")
    st.title("📊 Smart Data Analyzer")
    
    uploaded_file = st.file_uploader("Upload CSV or Excel file", type=["csv", "xlsx", "xls"])
    
    if uploaded_file:
        df = process_file(uploaded_file)
        if df is not None:
            date_cols, numeric_cols, cat_cols = analyze_data(df)
            
            with st.expander("🔍 Data Preview", expanded=True):
                st.dataframe(df.head(100), use_container_width=True)
                st.markdown(f"""
                - **Total Rows**: {df.shape[0]}
                - **Total Columns**: {df.shape[1]}
                - **Numeric Columns**: {len(numeric_cols)}
                - **Categorical Columns**: {len(cat_cols)}
                """)
            
            create_visualizations(df, date_cols, numeric_cols, cat_cols)
            
            st.download_button("Download Analysis Report",
                              data=df.describe(include='all').to_csv(),
                              file_name="data_report.csv")

if __name__ == "__main__":
    main()