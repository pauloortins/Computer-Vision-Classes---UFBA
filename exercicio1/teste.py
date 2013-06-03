from SimpleCV import *

extractor = MorphologyFeatureExtractor()
lenna = Image("lenna")
lenna.show()
features_array = extractor.extract(lenna)

print features_array
    