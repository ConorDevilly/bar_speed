import cv2
import os
import requests
import logging as log
import numpy as np


"""
The purpose of this script is to download a list of images and resize them
Parts of this script are based off the following tutorial:
    [1] Python Programming Tutorials,
        https://pythonprogramming.net/haar-cascade-object-detection-python-opencv-tutorial/,
        Date Accessed: Oct 2017
"""


# TODO: These should really be passed from command-line
POS_IMG_LIST = 'barbell_img.txt'
POS_IMG_DIR = 'pos_png'
IMG_SUFFIX = '.png'
WIDTH_SCALE_SIZE = 32
HEIGHT_SCALE_SIZE = 18


def configure_logging():
    """Configure logging settings"""
    log.basicConfig(filename = 'download_img.log', level = log.DEBUG)


def resize_imgs(dirname, width, height):
    """
    Resizes images to a given size
    Params:
        dirname: Path of directory of images
        width: Desired image width
        height: Desired image height
    """
    for f in os.listdir(dirname):
        img = cv2.imread(dirname + '/' + f)
        resized_img = cv2.resize(img, (width, height))
        cv2.imwrite(dirname + '/' + f, resized_img)


def generate_descriptors(dirname):
    """
    Generates a descriptor file (essentially a list of files) for training a classifier
    Params:
        dirname: Path to directory containing images
    """
    # Create a list of entries in form <dir_name>/<img_name>
    entries = [ dirname + '/' + f for f in os.listdir(dirname) ]
    # Write list to file
    with open(dirname + '_desc.txt', 'w') as f:
        for entry in entries:
            f.write(entry + '\n')


def remove_invalid(invalid_img_path, dir_to_check):
    """
    Some images can non longer be downloaded.
    These images have a default error image.
    This function removes these images
    Paramas:
        invalid_img_path: Path to the invalid image example
        dir_to_check: The directory containing images to compare
    """
    """Taken from [1] but rewritten to be more efficient & reliable"""
    invalid_img = cv2.imread(invalid_img_path)
    for f in os.listdir(dir_to_check):
        try:
            img = cv2.imread(dir_to_check + '/' + f)
            # Remove image if they match the given invalid image
            if invalid_img.shape == img.shape and not(np.bitwise_xor(invalid_img, img).any()):
                log.info('Deleting: ' + f)
                os.remove(dir_to_check + '/' + f)
        # Also delete unreadable images
        except AttributeError:
            log.warn(f + ' is corrupted / not readable')
            log.info('Deleting: ' + f)
            os.remove(dir_to_check + '/' + f)


def store_img(dirname, img_list):
    """
    Retrieves a list of images from URLs
    and stores them in a directory.
    Params:
        dirname: Path of directory to store images
        img_list: Path to text file of image URLs
    """
    """General idea for this function is based off [1] but completely rewritten"""
    # Check if directory exists, if not make it
    if not os.path.exists(dirname):
        log.info('Creating directory: ' + dirname)
        os.makedirs(dirname)

    img_counter = 0
    with open(img_list) as f:
        for line in f:
            log.info('Retrieving ' + line)
            try:
                # Get the image
                resp = requests.get(line.strip(), timeout = 5)
                if resp.status_code == 200:
                    img_name = dirname + '_' + str(img_counter) + IMG_SUFFIX
                    # Write the image
                    with open(dirname + '/' + img_name, 'wb') as img:
                        log.info('Saving ' + img_name)
                        for chunk in resp:
                            img.write(chunk)
                    img_counter += 1
                else:
                    log.warning('Bad response code for: ' + line)
            except requests.exceptions.Timeout:
                log.warning('Timeout for URL: ' + line)
            except requests.exceptions.ConnectionError:
                log.warning('Could not connect to: ' + line)


def main():
    configure_logging()
    store_img(POS_IMG_DIR, POS_IMG_LIST)
    remove_invalid(POS_IMG_LIST, i)
    resize_imgs(POS_IMG_DIR, WIDTH_SCALE_SIZE, HEIGHT_SCALE_SIZE)
    generate_descriptors(POS_IMG_DIR)


if __name__ == '__main__':
    main()
