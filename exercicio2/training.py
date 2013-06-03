import os
import glob
from SimpleCV import *
from time import time, sleep

def get_files_from_type(extension):
    my_images_path = "../dataset/monkey/"

    if not my_images_path:
        path = os.getcwd() #get the current directory
    else:
        path = my_images_path

        directory = os.path.join(path, extension)
        files = glob.glob(directory)

    return files

if (__name__ == "__main__"):

    # Training data set paths for classification(suppervised learnning)
    image_dirs = ['dataset/positives/',
                  'dataset/negatives/']

    # Different class labels for multi class classification
    class_names = ['yes','no']

    feature_extractors = [HueHistogramFeatureExtractor()]
    classifier = TreeClassifier(feature_extractors, 'Boosted')

    classifier.train(image_dirs,class_names,savedata='train.txt')

    test_dirs = ['test/positives/',
                  'test/negatives/']

    classifier.test(test_dirs, class_names)

