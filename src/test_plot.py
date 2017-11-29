import unittest
from mock import patch, MagicMock, mock_open
from plot import BarGraph


class TestBarGraph(unittest.TestCase):
    def setUp(self):
        """Setup before each test is run"""
        self.bar_graph = BarGraph()
        self.log_data = [
            'INFO:root:Loaded video at: a_test.mp4',
            'INFO:root:Video FPS: 3.0',
            'INFO:root:CM Multiplier: 0.15875',
            'INFO:root:Frame 1. Distance moved: -1',
            'INFO:root:Frame 2. Distance moved: -3',
            'INFO:root:Frame 3. Distance moved: -5',
            'INFO:root:Frame 4. Distance moved: -1',
            'INFO:root:Frame 5. Distance moved: 0'
        ]
        self.bad_log_data = ['random', 'test', 'text']
        #with patch('__builtin__.open', mock_open(read_data = self.log_data)) as mock_file:
        with patch('__builtin__.open', mock_open()) as mock_file:
            mock_file.return_value.readlines.return_value = self.log_data
            self.bar_graph.load_data('a_path')

    def test_load_distance_data(self):
        """Test distance data loads as expected"""
        expected = ['-1', '-3', '-5', '-1', '0']
        actual = self.bar_graph._load_distance_data(self.log_data)
        self.assertEquals(expected, actual)

    def test_load_distance_data_no_data(self):
        """Test distance data when no data present"""
        expected = []
        actual = self.bar_graph._load_distance_data(self.bad_log_data)
        self.assertEquals(expected, actual)

    def test_load_cm_multiplier(self):
        """Test cm multiplier loads as expected"""
        expected = 0.15875
        actual = self.bar_graph._load_cm_multiplier(self.log_data)
        self.assertEquals(expected, actual)

    def test_load_cm_multiplier_no_data(self):
        """Test cm multiplier when no value present"""
        expected = None
        actual = self.bar_graph._load_cm_multiplier(self.bad_log_data)
        self.assertEquals(expected, actual)

    def test_load_fps(self):
        """Test FPS laods as expected"""
        expected = 3.0
        actual = self.bar_graph._load_fps(self.log_data)
        self.assertEquals(expected, actual)

    def test_load_fps_no_data(self):
        """Test FPS when no value present"""
        expected = None
        actual = self.bar_graph._load_fps(self.bad_log_data)
        self.assertEquals(expected, actual)

    def test_transform_to_velocity_data(self):
        """Test distance data transforms to velocity data as expected"""
        expected = [-0.15875, -0.3175, -0.3175, 0.635, 0.15875]
        distance_data = self.bar_graph._load_distance_data(self.log_data)
        cm_multiplier = self.bar_graph._load_cm_multiplier(self.log_data)
        actual = self.bar_graph._transform_to_velocity_data(distance_data, cm_multiplier)
        self.assertEqual(expected, actual)

    def test_transform_to_speed_data(self):
        """Test distance data transforms to speed data as expected"""
        expected = [0.15875, 0.3175, 0.3175, 0.635, 0.15875]
        distance_data = self.bar_graph._load_distance_data(self.log_data)
        cm_multiplier = self.bar_graph._load_cm_multiplier(self.log_data)
        actual = self.bar_graph._transform_to_speed_data(distance_data, cm_multiplier)
        self.assertEqual(expected, actual)

    def test_get_total_seconds(self):
        """Test total seconds calculated"""
        expected = 1
        actual = self.bar_graph._get_total_seconds()
        self.assertEquals(expected, actual)

    def test_get_total_seconds_exception(self):
        """Test exception thrown when no fps present"""
        bar_graph = BarGraph()
        with patch('__builtin__.open', mock_open()) as mock_file:
            mock_file.return_value.readlines.return_value = []
            bar_graph.load_data('a_path')
        with self.assertRaises(Exception):
            bar_graph._get_total_seconds()

    def test_reduce_points(self):
        """Test points in a list reduces as expected"""
        expected = ['-1', '-5', '0']
        actual = self.bar_graph._reduce_points(['-1', '-3', '-5', '-1', '0'], 2)
        self.assertEqual(expected, actual)

    def test_reduce_data_half_second(self):
        """Test points reduce to seconds / 2 points"""
        expected = ['-1', '-5', '0']
        actual = self.bar_graph._reduce_data_half_second(['-1', '-3', '-5', '-1', '0'])
        self.assertEqual(expected, actual)

    # Cannot unit test plotting functions (no way to test pyplot values)
