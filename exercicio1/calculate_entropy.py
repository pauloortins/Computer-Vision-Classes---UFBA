from SimpleCV import *
from scipy import *
from numpy import *
import pylab as P
from matplotlib import *
from time import time, sleep
import random
import matplotlib.pyplot as plt

import math


def calc_entropy(array):
    
    total = 0
    ent = 0

    for x in range(len(array)):
        total = total + (pow(array[x],2.0))

    for x in range(len(array)):
        quo = (pow(array[x],2.0)) / total
        if (quo != 0):        
            ent = ent + (quo * math.log(quo))

    return -ent

def read_feature_file():

    f = open('datasetFeatures.txt', 'r')
    image_feature = []

    for lines in f:
        image_feature.append(lines)

    return image_feature

def get_feature_array(image_feature, n):

    array = []

    for feature in image_feature:
        array.append(eval(feature)[n])

    return array

if __name__=="__main__":

    arrayFeatures = read_feature_file()
    
    entropy_feature1 = calc_entropy(get_feature_array(arrayFeatures, 0))
    entropy_feature2 = calc_entropy(get_feature_array(arrayFeatures, 1))
    entropy_feature3 = calc_entropy(get_feature_array(arrayFeatures, 2))
    entropy_feature4 = calc_entropy(get_feature_array(arrayFeatures, 3))
    entropy_feature5 = calc_entropy(get_feature_array(arrayFeatures, 4))
    entropy_feature6 = calc_entropy(get_feature_array(arrayFeatures, 5))
    entropy_feature7 = calc_entropy(get_feature_array(arrayFeatures, 6))
    entropy_feature8 = calc_entropy(get_feature_array(arrayFeatures, 7))
    entropy_feature9 = calc_entropy(get_feature_array(arrayFeatures, 8))

    entropy_array = [entropy_feature1, entropy_feature2, entropy_feature3, entropy_feature4,
    entropy_feature5, entropy_feature6, entropy_feature7, entropy_feature8, entropy_feature9]

    plt.bar(range(0,9), entropy_array)
    plt.show()

    sleep(10)