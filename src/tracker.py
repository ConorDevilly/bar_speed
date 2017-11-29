from __future__ import division
import cv2
import numpy as np
import logging
import random


class BarbellTracker:
    """
    Tracks a barbell movement throughout a video
    """

    def __init__(self, tracking_algo, debug_mode=False):
        """
        Params:
            String: tracking_algo: The algorithm to use for tracking. Can be any supported by OpenCV
            Boolean: debug_mode: Whether do display debug information or not
        """
        self.tracker = cv2.Tracker_create(tracking_algo)
        self.debug_mode = debug_mode
        logging.basicConfig(filename='track_barbell.log', level=logging.DEBUG)

    def track(self, frame, init_pos, frame_ctr=1):
        """
        Tracks a position through the duration of the loaded video
        Params:
            cv2.Image: frame: Frame to initialise tracker on
            List: init_pos: Position to track in form: [x, y, width, height]
        """
        self.tracker.init(frame, tuple(init_pos))
        init_center_pos = int((init_pos[3] / 2) + init_pos[1])

        if self.debug_mode:
            # Created window to display video
            cv2.namedWindow('Barbell_Tracker', cv2.WINDOW_NORMAL)

        while(self.video.isOpened()):
            """
            Based off: https://pythonprogramming.net/haar-cascade-object-detection-python-opencv-tutorial/
            Using tracker instead of constant detection
            """
            # Read a frame
            retval, frame = self.video.read()
            if not retval:
                break
            frame_ctr += 1

            # Update the tracker
            retval, current_pos = self.tracker.update(frame)
            if not retval:
                raise Exception('Could not update tracker')

            # Find center of current position
            current_center_pos = int((current_pos[3] / 2) + current_pos[1])

            # Log distance moved
            distance_moved = init_center_pos - current_center_pos
            logging.info('Frame {}. Distance moved: {}'.format(frame_ctr, distance_moved))

            if self.debug_mode:
                # Draw inital position
                cv2.rectangle(frame, (int(init_pos[0]), int(init_pos[1])),
                              (int(init_pos[0] + init_pos[2]), int(init_pos[1] + init_pos[3])),
                              (0, 255, 0), 1)
                # Draw rectangle over tracker position
                cv2.rectangle(frame, (int(current_pos[0]), int(current_pos[1])),
                              (int(current_pos[0] + current_pos[2]), int(current_pos[1] + current_pos[3])),
                              (0, 0, 255), 2)
                # Display distance moved
                cv2.putText(frame, 'Distance moved: {}'.format(distance_moved),
                            (100, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 255), 2)
                # Show frame
                cv2.imshow('Barbell_Tracker', frame)
                # Exit if q pressed
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

        # Stop video when finished
        self.video.release()

    def detect_barbell_pos(self, classifier):
        """
        Detects a barbell's position in a frame
        Params:
            cv2.CascadeClassifier: classifier: Classifier to detect barbell
        Returns:
            tuple: p: Position of barbell in form: (x, y, width, height)
            cv2.Image: frame: Frame that barbell was detected in
            float: cm_multiplier: Value to multiply pixels by to find cm equivalent
        """
        self._check_vid_open()
        retval, frame = self.video.read()
        if not retval:
            raise IOError('Could not read frame from video')

        barbell_pos = classifier.detectMultiScale(frame, 1.1, 25)
        if not barbell_pos.any():
            raise Exception('Classifier detection failed')

        for p in barbell_pos:
            circles = self.test_hough_circle(frame[p[1]:p[1]+p[3], p[0]:p[0]+p[2]])
            if circles is not None:
                # If one circle detected, track current position
                if len(circles[0]) == 1:
                    # Extract diameter of circle to find cm_multiplier
                    pixel_diameter = circles[0, :][0][2] * 2
                    cm_multiplier = self._get_cm_per_pixel(pixel_diameter)
                    logging.info('CM Multiplier: {}'.format(cm_multiplier))
                    return frame, p, cm_multiplier

        # If no circles found, return random object
        return frame, barbell_pos[random.randint(0, len(barbell_pos)-1)], None

    def _get_cm_per_pixel(self, diameter):
        """Converts pixels in a barbell's diameter to centimeters"""
        CM_PER_INCH = 2.54
        pixels_per_inch = 2 / diameter
        cm_per_pixel = CM_PER_INCH * pixels_per_inch
        return cm_per_pixel

    def get_video_fps(self):
        """Gets Frames Per Second of loaded video"""
        fps = self.video.get(cv2.CAP_PROP_FPS)
        logging.info('Video FPS: {}'.format(fps))
        return fps

    def test_hough_circle(self, img):
        '''
        Performs a Hough Circle transformation on an image
        Params:
            cv2.Image: img: Image to perform transformation on
        Returns:
            List: circles: A list of circles in the image
        '''
        """
        Based off:
            http://opencv-python-tutroals.readthedocs.io/en/latest/py_tutorials/py_imgproc/py_houghcircles/py_houghcircles.html
        """
        grey_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        circles = cv2.HoughCircles(grey_img, cv2.HOUGH_GRADIENT, 1, 20,
                                   param1=50, param2=30, minRadius=0, maxRadius=0)
        if circles is not None:
            circles = np.uint16(np.around(circles))
        return circles

    def load_video(self, vid_path):
        """Loads a video. Returns 1 on success"""
        self.video = cv2.VideoCapture(vid_path)
        self._check_vid_open()
        logging.info('Loaded video at: {}'.format(vid_path))
        return 1

    def _check_vid_open(self):
        """Raises an error if a video is not opened. Else return 1"""
        if not self.video.isOpened():
            raise IOError('Video is not open')
        return 1
