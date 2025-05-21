import unittest
from unittest.mock import patch, mock_open, MagicMock
import json
import pandas as pd
import plotly.graph_objects as go
from plot_tools import PlotlyMCP

class TestPlotlyMCP(unittest.TestCase):

    def setUp(self):
        # This setup creates an MCP instance with non-existent default files,
        # so it will test the "file not found" path by default for constructor tests.
        # For other tests, we often mock/set attributes directly.
        with patch('builtins.print') as mock_print: # Suppress warnings during setup
            self.mcp_no_files = PlotlyMCP(plot_desc_path='dummy_desc.json', plot_examples_path='dummy_examples.json')
        
        # For tests that need a "clean" MCP or one with specific loaded data
        self.sample_desc_data = {"bar": "A bar chart.", "scatter": "A scatter plot."}
        self.sample_examples_data = [
            {"type": "bar", "data": {"columns": ["X", "Y"], "data": [["A",1]]}, "layout": {}},
            {"type": "scatter", "data": {"columns": ["X", "Y"], "data": [[1,2]]}, "layout": {}}
        ]

    # 1. __init__ method (Constructor) tests
    @patch('builtins.open', new_callable=mock_open)
    @patch('json.load')
    def test_init_load_success(self, mock_json_load, mock_file_open):
        # Mock file content for descriptions and examples
        # Side_effect allows different return values for consecutive calls to json.load
        mock_json_load.side_effect = [
            self.sample_desc_data,  # First call to json.load (for descriptions)
            self.sample_examples_data  # Second call to json.load (for examples)
        ]
        
        # Configure mock_open to handle two different files
        # This is a bit simplified; real multi-file mocking can be more complex
        # For this test, we assume json.load is what matters most.
        mock_file_open.side_effect = [
            mock_open(read_data=json.dumps(self.sample_desc_data)).return_value,
            mock_open(read_data=json.dumps(self.sample_examples_data)).return_value
        ]

        mcp = PlotlyMCP(plot_desc_path='plot_desc.json', plot_examples_path='plot_examples.json')
        
        mock_file_open.assert_any_call('plot_desc.json', 'r', encoding='utf-8')
        mock_file_open.assert_any_call('plot_examples.json', 'r', encoding='utf-8')
        self.assertEqual(json.load.call_count, 2)
        
        self.assertEqual(mcp.plot_descriptions, self.sample_desc_data)
        self.assertEqual(mcp.plot_examples, self.sample_examples_data)

    @patch('builtins.print')
    def test_init_file_not_found(self, mock_print):
        mcp = PlotlyMCP(plot_desc_path='non_existent_desc.json', plot_examples_path='non_existent_examples.json')
        self.assertEqual(mcp.plot_descriptions, {})
        self.assertEqual(mcp.plot_examples, [])
        mock_print.assert_any_call("Warning: Description file not found at non_existent_desc.json")
        mock_print.assert_any_call("Warning: Examples file not found at non_existent_examples.json")

    @patch('builtins.open', new_callable=mock_open, read_data='invalid json')
    @patch('json.load', side_effect=json.JSONDecodeError("Error", "doc", 0))
    @patch('builtins.print')
    def test_init_json_decode_error_desc(self, mock_print, mock_json_load, mock_file_open):
        # Test for description file
        with patch('builtins.open', mock_open(read_data='invalid json'), create=True) as m1:
            # Make examples file valid to isolate the error
            with patch('builtins.open', mock_open(read_data=json.dumps(self.sample_examples_data)), create=True) as m2:
                 # json.load should be called twice, first fails, second succeeds
                mock_json_load.side_effect = [json.JSONDecodeError("Error", "doc", 0), self.sample_examples_data]
                
                # Re-assign mock_open to handle two different files correctly
                def open_side_effect(path, *args, **kwargs):
                    if path == 'bad_desc.json':
                        return m1.return_value
                    elif path == 'good_examples.json':
                        return m2.return_value
                    raise FileNotFoundError
                mock_file_open.side_effect = open_side_effect

                mcp = PlotlyMCP(plot_desc_path='bad_desc.json', plot_examples_path='good_examples.json')
                self.assertEqual(mcp.plot_descriptions, {})
                self.assertEqual(mcp.plot_examples, self.sample_examples_data) # Examples should load
                mock_print.assert_any_call("Warning: Could not decode JSON from bad_desc.json")

    @patch('builtins.open', new_callable=mock_open)
    @patch('json.load')
    @patch('builtins.print')
    def test_init_json_decode_error_examples(self, mock_print, mock_json_load, mock_file_open):
        # Test for examples file
        # Descriptions load fine, examples file is invalid json
        mock_json_load.side_effect = [
            self.sample_desc_data, 
            json.JSONDecodeError("Error", "doc", 0)
        ]
        
        def open_side_effect(path, *args, **kwargs):
            if path == 'good_desc.json':
                return mock_open(read_data=json.dumps(self.sample_desc_data)).return_value
            elif path == 'bad_examples.json':
                return mock_open(read_data='invalid json').return_value
            raise FileNotFoundError
        mock_file_open.side_effect = open_side_effect

        mcp = PlotlyMCP(plot_desc_path='good_desc.json', plot_examples_path='bad_examples.json')
        self.assertEqual(mcp.plot_descriptions, self.sample_desc_data) # Descriptions should load
        self.assertEqual(mcp.plot_examples, [])
        mock_print.assert_any_call("Warning: Could not decode JSON from bad_examples.json")

    # 2. get_plot_description method tests
    def test_get_plot_description_valid(self):
        self.mcp_no_files.plot_descriptions = self.sample_desc_data
        self.assertEqual(self.mcp_no_files.get_plot_description('bar'), 'A bar chart.')

    def test_get_plot_description_invalid(self):
        self.mcp_no_files.plot_descriptions = {} # Ensure it's empty
        self.assertEqual(self.mcp_no_files.get_plot_description('pie'), 'Description not available for plot type: pie')

    # 3. get_example method tests
    def test_get_example_valid(self):
        self.mcp_no_files.plot_examples = self.sample_examples_data
        expected_example = self.sample_examples_data[0] # bar example
        self.assertEqual(self.mcp_no_files.get_example('bar'), expected_example)

    def test_get_example_invalid(self):
        self.mcp_no_files.plot_examples = [] # Ensure it's empty
        self.assertEqual(self.mcp_no_files.get_example('pie'), 'Example not available for plot type: pie')

    # 4. recommend_plot_type method tests
    def test_recommend_plot_type(self):
        sample_df = pd.DataFrame({'col1': [1, 2], 'col2': [3, 4]})
        # No need to mock anything, just use the instance from setUp
        self.assertEqual(self.mcp_no_files.recommend_plot_type(sample_df), 'bar')

    # 5. visualize method tests
    def setUp_visualize_mcp(self):
        # Helper to get an MCP instance where files are "loaded" correctly for visualize tests
        with patch('builtins.open', new_callable=mock_open) as mock_file:
            mock_file.side_effect = [
                mock_open(read_data=json.dumps(self.sample_desc_data)).return_value,
                mock_open(read_data=json.dumps(self.sample_examples_data)).return_value
            ]
            with patch('json.load', side_effect=[self.sample_desc_data, self.sample_examples_data]):
                mcp = PlotlyMCP(plot_desc_path='desc.json', plot_examples_path='examples.json')
        return mcp

    def test_visualize_bar_chart(self):
        mcp = self.setUp_visualize_mcp()
        data = {"columns": ["Category", "Value"], "data": [["A", 10], ["B", 15]]}
        fig = mcp.visualize(data, plot_type='bar', title='Test Bar', x_label='Categories', y_label='Values')
        
        self.assertIsInstance(fig, go.Figure)
        self.assertEqual(len(fig.data), 1)
        self.assertIsInstance(fig.data[0], go.Bar)
        self.assertEqual(fig.layout.title.text, 'Test Bar')
        self.assertEqual(fig.layout.xaxis.title.text, 'Categories')
        self.assertEqual(fig.layout.yaxis.title.text, 'Values')

    def test_visualize_scatter_chart(self):
        mcp = self.setUp_visualize_mcp()
        data = {"columns": ["X", "Y"], "data": [[1, 2], [3, 4], [5, 1]]}
        fig = mcp.visualize(data, plot_type='scatter', title='Test Scatter', x_label='X-vals', y_label='Y-vals')

        self.assertIsInstance(fig, go.Figure)
        self.assertEqual(len(fig.data), 1)
        self.assertIsInstance(fig.data[0], go.Scatter)
        self.assertEqual(fig.data[0].mode, 'markers')
        self.assertEqual(fig.layout.title.text, 'Test Scatter')
        self.assertEqual(fig.layout.xaxis.title.text, 'X-vals')
        self.assertEqual(fig.layout.yaxis.title.text, 'Y-vals')

    def test_visualize_line_chart(self):
        mcp = self.setUp_visualize_mcp()
        data = {"columns": ["Time", "Value"], "data": [[1, 10], [2, 12], [3, 8]]}
        fig = mcp.visualize(data, plot_type='line', title='Test Line', x_label='Timepoints', y_label='Measurements')

        self.assertIsInstance(fig, go.Figure)
        self.assertEqual(len(fig.data), 1)
        self.assertIsInstance(fig.data[0], go.Scatter) # Line chart is also a Scatter trace
        self.assertEqual(fig.data[0].mode, 'lines+markers')
        self.assertEqual(fig.layout.title.text, 'Test Line')
        self.assertEqual(fig.layout.xaxis.title.text, 'Timepoints')
        self.assertEqual(fig.layout.yaxis.title.text, 'Measurements')

    def test_visualize_plot_type_none(self):
        mcp = self.setUp_visualize_mcp()
        data = {"columns": ["X", "Y"], "data": [["A", 1], ["B", 2]]}
        # Mock recommend_plot_type to ensure it's called and to control its output
        with patch.object(mcp, 'recommend_plot_type', return_value='bar') as mock_recommend:
            fig = mcp.visualize(data, plot_type=None)
            mock_recommend.assert_called_once()
            self.assertIsInstance(fig, go.Figure)
            self.assertEqual(len(fig.data), 1)
            self.assertIsInstance(fig.data[0], go.Bar) # Should default to bar via recommend

    @patch('builtins.print')
    def test_visualize_invalid_data_format_not_dict(self, mock_print):
        mcp = self.setUp_visualize_mcp()
        fig = mcp.visualize(data="not a dict", plot_type='bar')
        self.assertIsNone(fig)
        mock_print.assert_any_call("Error: Invalid data format. Expected a dict with 'columns' and 'data' keys.")

    @patch('builtins.print')
    def test_visualize_invalid_data_format_missing_keys(self, mock_print):
        mcp = self.setUp_visualize_mcp()
        fig = mcp.visualize(data={"nodata": True}, plot_type='bar')
        self.assertIsNone(fig)
        mock_print.assert_any_call("Error: Invalid data format. Expected a dict with 'columns' and 'data' keys.")

    @patch('builtins.print')
    def test_visualize_empty_dataframe(self, mock_print):
        mcp = self.setUp_visualize_mcp()
        data = {"columns": ["X", "Y"], "data": []} # Data leads to empty DataFrame
        fig = mcp.visualize(data, plot_type='bar')
        self.assertIsNone(fig)
        mock_print.assert_any_call("Error: DataFrame is empty.")
        
    @patch('builtins.print')
    def test_visualize_insufficient_columns_bar(self, mock_print):
        mcp = self.setUp_visualize_mcp()
        data = {"columns": ["Value"], "data": [[10], [20]]}
        fig = mcp.visualize(data, plot_type='bar')
        self.assertIsNone(fig)
        mock_print.assert_any_call("Error: Bar chart requires at least two columns.")

    @patch('builtins.print')
    def test_visualize_insufficient_columns_scatter(self, mock_print):
        mcp = self.setUp_visualize_mcp()
        data = {"columns": ["Value"], "data": [[10], [20]]}
        fig = mcp.visualize(data, plot_type='scatter')
        self.assertIsNone(fig)
        mock_print.assert_any_call("Error: Scatter plot requires at least two columns.")

    @patch('builtins.print')
    def test_visualize_insufficient_columns_line(self, mock_print):
        mcp = self.setUp_visualize_mcp()
        data = {"columns": ["Value"], "data": [[10], [20]]}
        fig = mcp.visualize(data, plot_type='line')
        self.assertIsNone(fig)
        mock_print.assert_any_call("Error: Line chart requires at least two columns.")

    @patch('builtins.print')
    def test_visualize_unsupported_plot_type(self, mock_print):
        mcp = self.setUp_visualize_mcp()
        data = {"columns": ["X", "Y"], "data": [["A", 1]]}
        fig = mcp.visualize(data, plot_type='unsupported_chart')
        self.assertIsNone(fig)
        mock_print.assert_any_call("Plot type 'unsupported_chart' is not yet supported.")

if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
