import unittest
import sys
import os
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.dirname(__file__))
from utils import process_csv, import_pyModule

import_pyModule()
from pywib.utils.visualization import visualize_trace
from pywib.utils.visualization.trace_strategies import TraceVisualizationType

DEBUG = True

class TestData:
    if(DEBUG):
        dataFile = 'test/test_data/test_auc.csv'
    else:
        dataFile = 'pywib/test/test_data/test_auc.csv'

class TestVisualization(unittest.TestCase):
    def setUp(self):
        """Set up test data"""
        self.df = process_csv(TestData.dataFile)
        
        # We can test with just a few rows to make it fast
        self.stroke_indices = self.df.head(10).index.tolist()
        self.stroke_id = "test_stroke"

    @patch('pywib.utils.visualization.visualization.plt')
    def test_visualize_trace_simple(self, mock_plt):
        # Mock subplots to return a figure and an axis
        mock_fig = MagicMock()
        mock_ax = MagicMock()
        mock_plt.subplots.return_value = (mock_fig, mock_ax)

        visualize_trace(self.df, self.stroke_indices, self.stroke_id, 
                        type="simple", plot=False)
        
        # Verify that plot was called for the real trace
        mock_ax.plot.assert_called()
        # SIMPLE should call axis('off')
        mock_ax.axis.assert_called_with('off')
        mock_plt.close.assert_called_with(mock_fig)

    @patch('pywib.utils.visualization.visualization.plt')
    def test_visualize_trace_info(self, mock_plt):
        mock_fig = MagicMock()
        mock_ax = MagicMock()
        mock_plt.subplots.return_value = (mock_fig, mock_ax)

        visualize_trace(self.df, self.stroke_indices, self.stroke_id, 
                        type="info", plot=False)
        
        mock_ax.plot.assert_called()
        mock_ax.set_title.assert_called()
        mock_ax.set_xlabel.assert_called()
        mock_plt.close.assert_called_with(mock_fig)

    @patch('pywib.utils.visualization.visualization.plt')
    def test_visualize_trace_optimal_line(self, mock_plt):
        mock_fig = MagicMock()
        mock_ax = MagicMock()
        mock_plt.subplots.return_value = (mock_fig, mock_ax)

        visualize_trace(self.df, self.stroke_indices, self.stroke_id, 
                        type="optimal_line", plot=False)
        
        # Optimal line has multiple plot calls (trace, optimal line, start dot, end dot)
        self.assertGreater(mock_ax.plot.call_count, 1)
        mock_ax.axis.assert_called_with('off')
        mock_plt.close.assert_called_with(mock_fig)

    @patch('pywib.utils.visualization.visualization.plt')
    def test_visualize_trace_full(self, mock_plt):
        mock_fig = MagicMock()
        mock_ax = MagicMock()
        mock_plt.subplots.return_value = (mock_fig, mock_ax)

        visualize_trace(self.df, self.stroke_indices, self.stroke_id, 
                        type="full", plot=False)
        
        self.assertGreater(mock_ax.plot.call_count, 1)
        mock_ax.set_title.assert_called()
        mock_ax.set_xlabel.assert_called()
        mock_plt.close.assert_called_with(mock_fig)

    def test_visualize_trace_invalid_type(self):
        with self.assertRaises(ValueError):
            visualize_trace(self.df, self.stroke_indices, self.stroke_id, 
                            type="invalid_type", plot=False)

if __name__ == '__main__':
    unittest.main()
