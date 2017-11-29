import unittest
import numpy as np
from mock import patch, MagicMock
from tracker import BarbellTracker


class TestBarbellTracker(unittest.TestCase):

    def setUp(self):
        """Setup before each test is run"""
        # Default test objects
        self.tracker = BarbellTracker('MEDIANFLOW')

        # Declare patchers
        self.video_patcher = patch('cv2.VideoCapture')
        self.hc_patcher = patch('tracker.BarbellTracker.test_hough_circle')

        # Start patchers
        self.video_mock = self.video_patcher.start()
        self.hc_mock = self.hc_patcher.start()

        # Default values for objects
        self.video_mock.return_value.read.return_value = 1, MagicMock()
        self.hc_mock.return_value = [[1]]
        self.dummy_vid_path = 'a_video.mp4'
        self.tracker.load_video(self.dummy_vid_path)

    def tearDown(self):
        """Cleanup after each test is run"""
        # Stop patchers
        self.video_patcher.stop()
        self.hc_patcher.stop()

    # TODO: Need to test log output to unit test main track function

    @patch('cv2.Tracker_create')
    def test_track_exception(self, tracker_create_mock):
        """Test an exception is thrown when tracker fails to update"""
        tracker_mock = MagicMock()
        tracker_mock.return_value.update.return_value = 0, MagicMock()
        tracker_create_mock.return_value = tracker_mock

        tracker = BarbellTracker('MEDIANFLOW')
        with self.assertRaises(Exception):
            tracker.track(MagicMock(), MagicMock())

    def test_detect_barbell_pos(self):
        """Test barbell detection working as expected"""
        classifier_mock = MagicMock()
        res_arr = np.array([[1, 2, 3, 4]], np.int32)
        classifier_mock.detectMultiScale.return_value = res_arr
        self.hc_mock.return_value = np.array([[[22, 22, 16]]], np.int32)

        ret_frame, ret_pos, ret_dia = self.tracker.detect_barbell_pos(classifier_mock)
        self.assertEquals(ret_pos.tolist(), [1, 2, 3, 4])
        self.assertEquals(ret_dia, 0.15875)

    def test_detect_barbell_pos_ioerror(self):
        """Test IOError thrown if video read fails during detection"""
        self.video_mock.return_value.read.return_value = 0, MagicMock()
        with self.assertRaises(IOError):
            self.tracker.detect_barbell_pos(MagicMock())

    def test_detect_barbell_pos_exception(self):
        """Test Exception thrown if classifier fails to detect anything"""
        classifier_mock = MagicMock()
        classifier_mock.detectMultiScale.return_value = np.array([])
        with self.assertRaises(Exception):
            self.tracker.detect_barbell_pos(classifier_mock)

    def test_get_cm_per_pixel(self):
        """Test that _get_cm_per_pixel is working as expected"""
        cm_multiplier = self.tracker._get_cm_per_pixel(2)
        self.assertEqual(cm_multiplier, 2.54)

    def test_get_video_fps(self):
        mock_vals = {5: 60}
        self.video_mock.return_value.get.side_effect = mock_vals.__getitem__
        fps = self.tracker.get_video_fps()
        self.assertEqual(fps, 60)

    @patch('random.randint')
    def test_detect_barbell_pos_no_circles(self, rand_mock):
        rand_mock.return_value = 1
        self.hc_mock.return_value = None
        classifier_mock = MagicMock()
        res_arr = np.array([[1, 2, 3, 4], [4, 3, 2, 1]], np.int32)
        classifier_mock.detectMultiScale.return_value = res_arr
        ret_frame, ret_pos, ret_dia = self.tracker.detect_barbell_pos(classifier_mock)
        self.assertEquals(ret_pos.tolist(), [4, 3, 2, 1])
        self.assertEquals(ret_dia, None)

    @patch('cv2.cvtColor')
    @patch('cv2.HoughCircles')
    def test_hough_circle(self, hough_circle_mock, cvt_color_mock):
        """Test that Hough Circles work as expected"""
        self.hc_patcher.stop()
        hough_circle_mock.return_value = [(3.42, 9.95, 12.4)]
        img_mock = MagicMock()
        circles = self.tracker.test_hough_circle(img_mock)
        self.assertEquals(len(circles), 1)
        self.assertEquals(circles[0][0], 3)
        self.assertEquals(circles[0][1], 10)
        self.assertEquals(circles[0][2], 12)
        self.hc_patcher.start()

    def test_load_video(self):
        """Test that videos load as expected"""
        tracker = BarbellTracker('MEDIANFLOW')
        load_ret = tracker.load_video(self.dummy_vid_path)
        self.assertEqual(load_ret, 1)

    def test_check_vid_open_err(self):
        """Test IOError thrown when video does not load"""
        tracker = BarbellTracker('MEDIANFLOW')
        self.video_mock.return_value.isOpened.return_value = False
        with self.assertRaises(IOError):
            tracker.load_video(self.dummy_vid_path)
