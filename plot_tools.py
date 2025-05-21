import plotly.io as pio
import plotly.graph_objects as go
import pandas as pd
import json

# Keep the existing plot_bar function for now, it might be removed or refactored later.
def plot_bar(x, y, title="A Figure Specified By Python Dictionary"):

    fig = dict(
        {
            "data": [{"type": "bar", "x": [1, 2, 3], "y": [1, 3, 2]}],
            "layout": {"title": {"text": "A Figure Specified By Python Dictionary"}},
        }
    )
    pio.show(fig, renderer="browser")

class PlotlyMCP:
    def __init__(self, plot_desc_path='plot_desc.json', plot_examples_path='plot_examples.json'):
        # Load descriptions and examples in the constructor
        try:
            with open(plot_desc_path, 'r', encoding='utf-8') as f:
                self.plot_descriptions = json.load(f)
        except FileNotFoundError:
            self.plot_descriptions = {}
            print(f"Warning: Description file not found at {plot_desc_path}")
        except json.JSONDecodeError:
            self.plot_descriptions = {}
            print(f"Warning: Could not decode JSON from {plot_desc_path}")

        try:
            with open(plot_examples_path, 'r', encoding='utf-8') as f:
                self.plot_examples = json.load(f)
        except FileNotFoundError:
            self.plot_examples = []
            print(f"Warning: Examples file not found at {plot_examples_path}")
        except json.JSONDecodeError:
            self.plot_examples = []
            print(f"Warning: Could not decode JSON from {plot_examples_path}")

    def get_plot_description(self, plot_type: str):
        return self.plot_descriptions.get(plot_type, f"Description not available for plot type: {plot_type}")

    def get_example(self, plot_type: str):
        for example in self.plot_examples:
            if example.get('type') == plot_type:
                return example
        return f"Example not available for plot type: {plot_type}"

    def visualize(self, data, plot_type: str = None, **kwargs):
        if not isinstance(data, dict) or 'columns' not in data or 'data' not in data:
            print("Error: Invalid data format. Expected a dict with 'columns' and 'data' keys.")
            return None
        
        try:
            df = pd.DataFrame(data['data'], columns=data['columns'])
        except Exception as e:
            print(f"Error converting data to DataFrame: {e}")
            return None

        if df.empty:
            print("Error: DataFrame is empty.")
            return None

        if plot_type is None:
            plot_type = self.recommend_plot_type(df) # recommend_plot_type is basic for now

        fig = go.Figure()

        if plot_type == 'bar':
            if len(df.columns) < 2:
                print("Error: Bar chart requires at least two columns.")
                return None
            fig.add_trace(go.Bar(x=df.iloc[:, 0], y=df.iloc[:, 1]))
        elif plot_type == 'scatter':
            if len(df.columns) < 2:
                print("Error: Scatter plot requires at least two columns.")
                return None
            fig.add_trace(go.Scatter(x=df.iloc[:, 0], y=df.iloc[:, 1], mode='markers'))
        elif plot_type == 'line':
            if len(df.columns) < 2:
                print("Error: Line chart requires at least two columns.")
                return None
            fig.add_trace(go.Scatter(x=df.iloc[:, 0], y=df.iloc[:, 1], mode='lines+markers'))
        else:
            print(f"Plot type '{plot_type}' is not yet supported.")
            return None

        # Customization
        if 'title' in kwargs:
            fig.update_layout(title_text=kwargs['title'])
        if 'x_label' in kwargs:
            fig.update_layout(xaxis_title=kwargs['x_label'])
        if 'y_label' in kwargs:
            fig.update_layout(yaxis_title=kwargs['y_label'])
        
        return fig

    def recommend_plot_type(self, df: pd.DataFrame):
        # Basic placeholder implementation
        # The input 'df' is a pandas DataFrame, already converted by 'visualize'
        # For now, always recommend 'bar'.
        # More sophisticated logic will be in Phase 2.
        return 'bar'
