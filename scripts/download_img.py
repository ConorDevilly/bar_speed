import cv2
import os
import requests
import logging as log
import numpy as np


POS_IMG_LIST = 'barbell_img.txt'
#POS_IMG_DIR = 'pos'
POS_IMG_DIR = 'pos_png'
NEG_IMG_LIST = 'people_leader_img.txt'
NEG_IMG_DIR = 'neg'
IMG_SUFFIX = '.jpeg'
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
    entries = [ dirname + '/' + f for f in os.listdir(dirname) ]
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
    invalid_img = cv2.imread(invalid_img_path)
    for f in os.listdir(dir_to_check):
        try:
            img = cv2.imread(dir_to_check + '/' + f)
            if invalid_img.shape == img.shape and not(np.bitwise_xor(invalid_img, img).any()):
                log.info('Deleting: ' + f)
                os.remove(dir_to_check + '/' + f)
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
    resize_imgs(POS_IMG_DIR, WIDTH_SCALE_SIZE, HEIGHT_SCALE_SIZE)
    #configure_logging()
    #store_img(POS_IMG_DIR, POS_IMG_LIST)
    #store_img(NEG_IMG_DIR, NEG_IMG_LIST)
    #for i in [ POS_IMG_DIR, NEG_IMG_DIR ]:
    #    remove_invalid('invalid.jpeg', i)
    #    resize_imgs(i, 100, 100)
    #    generate_descriptors(i)


if __name__ == '__main__':
    main()
