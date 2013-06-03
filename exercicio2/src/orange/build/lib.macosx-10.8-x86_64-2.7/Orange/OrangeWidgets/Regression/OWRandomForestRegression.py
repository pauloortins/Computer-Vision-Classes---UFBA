"""
<name>Random Forest Regression</name>
<description>Random forest regression.</description>
<icon>icons/RandomForestRegression.svg</icon>
<contact>Marko Toplak (marko.toplak(@at@)gmail.com)</contact>
<priority>320</priority>
<keywords>bagging, ensemble</keywords>

"""

from OWRandomForest import *

class OWRandomForestRegression(OWRandomForest):
    def __init__(self, parent=None, signalManager=None, title="Random forest regression"):
        OWRandomForest.__init__(self, parent, signalManager, title)
        
        self.inputs = [("Data", ExampleTable, self.setData),
                       ("Preprocess", PreprocessedLearner, self.setPreprocessor)]
        
        self.outputs = [("Learner", orange.Learner),
                        ("Random Forest Classifier", orange.Classifier)]

    def setData(self, data):
        self.data = self.isDataWithClass(data, orange.VarTypes.Continuous, checkMissing=True) and data or None
        
        if self.data:
            learner = self.constructLearner()
            self.progressBarInit()
            learner.callback = lambda v: self.progressBarSet(100.0 * v)
            try:
                self.classifier = learner(self.data)
                self.classifier.name = self.name
            except Exception, (errValue):
                self.error(str(errValue))
                self.classifier = None
            self.progressBarFinished()
        else:
            self.classifier = None

        self.send("Random Forest Classifier", self.classifier)
        