import argparse
import os
import cv2
from tracker import BarbellTracker


def get_args():
    '''Parses and returns arguments'''
    parser = argparse.ArgumentParser(description='Detect & Track a barbell in a film')

    parser.add_argument('-cp', '--cascade_path', help='Path to cascade file', default='cascade.xml')
    parser.add_argument('-vp', '--video_path', help='Path to video', required=True)
    parser.add_argument('--tracker', help='Tracker Algorithm',
                        choices=[
                            'boosting',  # OK
                            'mil',  # Bad performance, box jitters
                            'kcf',  # Good performance, detection point strange
                            'tld',  # Awful performance
                            'medianflow',  # Excellent performance & Accuracy
                            'goturn'  # Doesn't work at all
                        ], default='medianflow')
    parser.add_argument('-d', '--debug', action='store_true')
    args = parser.parse_args()
    return args


def main():
    args = get_args()

    # Check that the cascade file and video file exist
    for path in [args.cascade_path, args.video_path]:
        if not os.path.exists(path):
            raise IOError('File {} not found'.format(path))

    # Read cascade file
    cascade = cv2.CascadeClassifier(args.cascade_path)
    if cascade.empty():
        raise IOError('Error reading classifier file. Cascade is empty')

    tracker = BarbellTracker(args.tracker.upper(), debug_mode=args.debug)
    tracker.load_video(args.video_path)
    tracker.get_video_fps()
    init_frame, init_pos, cm_mult = tracker.detect_barbell_pos(cascade)
    tracker.track(init_frame, init_pos)


if __name__ == '__main__':
    main()
