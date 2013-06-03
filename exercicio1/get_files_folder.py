import os
import glob
import time
from SimpleCV import *

print __doc__

def get_files_from_type(extension):
    my_images_path = "../dataset/monkey/"

    if not my_images_path:
        path = os.getcwd() #get the current directory
    else:
        path = my_images_path

        directory = os.path.join(path, extension)
        files = glob.glob(directory)

    return files

if __name__=="__main__":
    f = open('datasetFeatures.txt', 'w')

    extractor = MorphologyFeatureExtractor()

    files = get_files_from_type('*.jpg')
    files.extend(get_files_from_type('*.gif'))

    for file in files:
        new_img = Image(file)
        feature_array = extractor.extract(new_img)
        f.write('{0}\n'.format(feature_array))
        print file
    