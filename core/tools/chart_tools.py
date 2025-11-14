# core/tools/chart_tools.py
import pandas as pd
import plotly.express as px
from langchain_core.tools import tool
import logging

from typing import List, Dict

@tool
def generate_chart(data: List[Dict], chart_type: str, x: str, y: str, title: str) -> dict:
    """
    Generates a chart from a list of dictionaries.
    """
    logging.info(f"Generating {chart_type} chart with x='{x}', y='{y}', and title='{title}'")
    try:
        df = pd.DataFrame(data)
        if chart_type == "bar":
            fig = px.bar(df, x=x, y=y, title=title)
        elif chart_type == "line":
            fig = px.line(df, x=x, y=y, title=title)
        elif chart_type == "pie":
            fig = px.pie(df, names=x, values=y, title=title)
        else:
            return {"error": f"Invalid chart type: {chart_type}"}

        return {"type": "chart", "output": fig}
    except Exception as e:
        logging.error(f"Error generating chart: {e}", exc_info=True)
        return {"error": f"An unexpected error occurred while generating the chart: {e}"}

chart_tools = [
    generate_chart,
]
