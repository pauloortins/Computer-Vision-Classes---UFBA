"""
<name>Linear Projection</name>
<description>Create a linear projection.</description>
<contact>Gregor Leban (gregor.leban@fri.uni-lj.si)</contact>
<icon>icons/LinearProjection.svg</icon>
<priority>2000</priority>
"""
# LinProj.py
#
# Show a linear projection of the data
#
from OWVisWidget import *
from OWLinProjGraph import *
from OWkNNOptimization import OWVizRank
from OWFreeVizOptimization import *
import OWToolbars, OWGUI, orngTest
import orngVisFuncts, OWColorPalette
import orngVizRank

###########################################################################################
##### WIDGET : Linear Projection
###########################################################################################
class OWLinProj(OWVisWidget):
    settingsList = ["graph.pointWidth", "graph.jitterSize", "graph.showFilledSymbols", "graph.scaleFactor",
                    "graph.showLegend", "graph.useDifferentSymbols", "autoSendSelection", "graph.useDifferentColors", "graph.showValueLines",
                    "graph.tooltipKind", "graph.tooltipValue", "toolbarSelection", "graph.alphaValue",
                    "graph.showProbabilities", "graph.squareGranularity", "graph.spaceBetweenCells", "graph.useAntialiasing"
                    "valueScalingType", "showAllAttributes", "colorSettings", "selectedSchemaIndex", "addProjectedPositions"]
    jitterSizeNums = [0.0, 0.01, 0.1, 0.5, 1, 2, 3, 4, 5, 7, 10, 15, 20]

    contextHandlers = {"": DomainContextHandler("", [ContextField("shownAttributes", DomainContextHandler.RequiredList, selected="selectedShown", reservoir="hiddenAttributes")])}

    def __init__(self,parent=None, signalManager = None, name = "Linear Projection", graphClass = None):
        OWVisWidget.__init__(self, parent, signalManager, name, TRUE)

        self.inputs = [("Data", ExampleTable, self.setData, Default),
                       ("Data Subset", ExampleTable, self.setSubsetData),
                       ("Features", AttributeList, self.setShownAttributes),
                       ("Evaluation Results", orngTest.ExperimentResults, self.setTestResults),
                       ("VizRank Learner", orange.Learner, self.setVizRankLearner),
                       ("Distances", orange.SymMatrix, self.setDistances)]
        self.outputs = [("Selected Data", ExampleTable), ("Other Data", ExampleTable), ("Features", AttributeList), ("FreeViz Learner", orange.Learner)]

        # local variables
        self.showAllAttributes = 0
        self.valueScalingType = 0
        self.autoSendSelection = 1
        self.data = None
        self.subsetData = None
        self.distances = None
        self.toolbarSelection = 0
        self.classificationResults = None
        self.outlierValues = None
        self.attributeSelectionList = None
        self.colorSettings = None
        self.selectedSchemaIndex = 0
        self.addProjectedPositions = 0
        self.resetAnchors = 0

        #add a graph widget
        if graphClass:
            self.graph = graphClass(self, self.mainArea, name)
        else:
            self.graph = OWLinProjGraph(self, self.mainArea, name)
        self.mainArea.layout().addWidget(self.graph)

        # graph variables
        self.graph.manualPositioning = 0
        self.graph.hideRadius = 0
        self.graph.showAnchors = 1
        self.graph.jitterContinuous = 0
        self.graph.showProbabilities = 0
        self.graph.useDifferentSymbols = 0
        self.graph.useDifferentColors = 1
        self.graph.tooltipKind = 0
        self.graph.tooltipValue = 0
        self.graph.scaleFactor = 1.0
        self.graph.squareGranularity = 3
        self.graph.spaceBetweenCells = 1
        self.graph.showAxisScale = 0
        self.graph.showValueLines = 0
        self.graph.valueLineLength = 5

        #load settings
        self.loadSettings()

##        # cluster dialog
##        self.clusterDlg = ClusterOptimization(self, self.signalManager, self.graph, name)
##        self.graph.clusterOptimization = self.clusterDlg

        # optimization dialog
        if name.lower() == "radviz":
            self.vizrank = OWVizRank(self, self.signalManager, self.graph, orngVizRank.RADVIZ, name)
            self.connect(self.graphButton, SIGNAL("clicked()"), self.saveToFile)
        elif name.lower() == "polyviz":
            self.vizrank = OWVizRank(self, self.signalManager, self.graph, orngVizRank.POLYVIZ, name)
            self.connect(self.graphButton, SIGNAL("clicked()"), self.graph.saveToFile)
        else:
            self.vizrank = OWVizRank(self, self.signalManager, self.graph, orngVizRank.LINEAR_PROJECTION, name)
            self.connect(self.graphButton, SIGNAL("clicked()"), self.saveToFile)

        self.optimizationDlg = self.vizrank  # for backward compatibility

        self.graph.normalizeExamples = (name.lower() == "radviz")       # ignore settings!! if we have radviz then normalize, otherwise not.

        #GUI
        # add a settings dialog and initialize its values

        self.tabs = OWGUI.tabWidget(self.controlArea)
        self.GeneralTab = OWGUI.createTabPage(self.tabs, "Main")
        self.SettingsTab = OWGUI.createTabPage(self.tabs, "Settings", canScroll = 1)

        #add controls to self.controlArea widget
        self.createShowHiddenLists(self.GeneralTab, callback = self.updateGraphAndAnchors)

        self.optimizationButtons = OWGUI.widgetBox(self.GeneralTab, "Optimization Dialogs", orientation = "horizontal")
        self.vizrankButton = OWGUI.button(self.optimizationButtons, self, "VizRank", callback = self.vizrank.reshow, tooltip = "Opens VizRank dialog, where you can search for interesting projections with different subsets of attributes.", debuggingEnabled = 0)
        self.wdChildDialogs = [self.vizrank]    # used when running widget debugging

        # freeviz dialog
        if name.lower() in ["linear projection", "radviz"]:
            self.freeVizDlg = FreeVizOptimization(self, self.signalManager, self.graph, name)
            self.wdChildDialogs.append(self.freeVizDlg)
            self.freeVizDlgButton = OWGUI.button(self.optimizationButtons, self, "FreeViz", callback = self.freeVizDlg.reshow, tooltip = "Opens FreeViz dialog, where the position of attribute anchors is optimized so that class separation is improved", debuggingEnabled = 0)
            if name.lower() == "linear projection":
                self.freeVizLearner = FreeVizLearner(self.freeVizDlg)
                self.send("FreeViz Learner", self.freeVizLearner)

##        self.clusterDetectionDlgButton = OWGUI.button(self.optimizationButtons, self, "Cluster", callback = self.clusterDlg.reshow, debuggingEnabled = 0)
##        self.vizrankButton.setMaximumWidth(63)
##        self.clusterDetectionDlgButton.setMaximumWidth(63)
##        self.freeVizDlgButton.setMaximumWidth(63)
##        self.connect(self.clusterDlg.startOptimizationButton , SIGNAL("clicked()"), self.optimizeClusters)
##        self.connect(self.clusterDlg.resultList, SIGNAL("selectionChanged()"),self.showSelectedCluster)

        self.zoomSelectToolbar = OWToolbars.ZoomSelectToolbar(self, self.GeneralTab, self.graph, self.autoSendSelection)
        self.graph.autoSendSelectionCallback = self.selectionChanged
        self.connect(self.zoomSelectToolbar.buttonSendSelections, SIGNAL("clicked()"), self.sendSelections)

        # ####################################
        # SETTINGS TAB
        # #####
        self.extraTopBox = OWGUI.widgetBox(self.SettingsTab, orientation = "vertical")
        self.extraTopBox.hide()

        box = OWGUI.widgetBox(self.SettingsTab, "Point Properties")
        OWGUI.hSlider(box, self, 'graph.pointWidth', label = "Size: ", minValue=1, maxValue=20, step=1, callback = self.updateGraph)
        OWGUI.hSlider(box, self, 'graph.alphaValue', label = "Transparency: ", minValue=0, maxValue=255, step=10, callback = self.updateGraph)

        box = OWGUI.widgetBox(self.SettingsTab, "Jittering Options")
        OWGUI.comboBoxWithCaption(box, self, "graph.jitterSize", 'Jittering size (% of range):', callback = self.resetGraphData, items = self.jitterSizeNums, sendSelectedValue = 1, valueType = float)
        OWGUI.checkBox(box, self, 'graph.jitterContinuous', 'Jitter continuous attributes', callback = self.resetGraphData, tooltip = "Does jittering apply also on continuous attributes?")

        box = OWGUI.widgetBox(self.SettingsTab, "Scaling Options")
        OWGUI.qwtHSlider(box, self, "graph.scaleFactor", label = 'Inflate points by: ', minValue=1.0, maxValue= 10.0, step=0.1, callback = self.updateGraph, tooltip="If points lie too much together you can expand their position to improve perception", maxWidth = 90)

        box = OWGUI.widgetBox(self.SettingsTab, "General Graph Settings")
        #OWGUI.checkBox(box, self, 'graph.normalizeExamples', 'Normalize examples', callback = self.updateGraph)
        OWGUI.checkBox(box, self, 'graph.showLegend', 'Show legend', callback = self.updateGraph)
        bbox = OWGUI.widgetBox(box, orientation = "horizontal")
        OWGUI.checkBox(bbox, self, 'graph.showValueLines', 'Show value lines  ', callback = self.updateGraph)
        OWGUI.qwtHSlider(bbox, self, 'graph.valueLineLength', minValue=1, maxValue=10, step=1, callback = self.updateGraph, showValueLabel = 0)
        OWGUI.checkBox(box, self, 'graph.useDifferentSymbols', 'Use different symbols', callback = self.updateGraph, tooltip = "Show different class values using different symbols")
        OWGUI.checkBox(box, self, 'graph.useDifferentColors', 'Use different colors', callback = self.updateGraph, tooltip = "Show different class values using different colors")
        OWGUI.checkBox(box, self, 'graph.showFilledSymbols', 'Show filled symbols', callback = self.updateGraph)
        OWGUI.checkBox(box, self, 'graph.useAntialiasing', 'Use antialiasing', callback = self.updateGraph)
        wbox = OWGUI.widgetBox(box, orientation = "horizontal")
        OWGUI.checkBox(wbox, self, 'graph.showProbabilities', 'Show probabilities'+'  ', callback = self.updateGraph, tooltip = "Show a background image with class probabilities")
        smallWidget = OWGUI.SmallWidgetLabel(wbox, pixmap = 1, box = "Advanced settings", tooltip = "Show advanced settings")
        OWGUI.rubber(wbox)

        box = OWGUI.widgetBox(self.SettingsTab, "Colors", orientation = "horizontal")
        OWGUI.button(box, self, "Colors", self.setColors, tooltip = "Set the canvas background color and color palette for coloring variables", debuggingEnabled = 0)

        box = OWGUI.widgetBox(self.SettingsTab, "Tooltips Settings")
        OWGUI.comboBox(box, self, "graph.tooltipKind", items = ["Show line tooltips", "Show visible attributes", "Show all attributes"], callback = self.updateGraph)
        OWGUI.comboBox(box, self, "graph.tooltipValue", items = ["Tooltips show data values", "Tooltips show spring values"], callback = self.updateGraph, tooltip = "Do you wish that tooltips would show you original values of visualized attributes or the 'spring' values (values between 0 and 1). \nSpring values are scaled values that are used for determining the position of shown points. Observing these values will therefore enable you to \nunderstand why the points are placed where they are.")

        box = OWGUI.widgetBox(self.SettingsTab, "Auto Send Selected Data When...")
        OWGUI.checkBox(box, self, 'autoSendSelection', 'Adding/Removing selection areas', callback = self.selectionChanged, tooltip = "Send selected data whenever a selection area is added or removed")
        OWGUI.checkBox(box, self, 'graph.sendSelectionOnUpdate', 'Moving/Resizing selection areas', tooltip = "Send selected data when a user moves or resizes an existing selection area")
        OWGUI.comboBox(box, self, "addProjectedPositions", items = ["Do not modify the domain", "Append projection as attributes", "Append projection as meta attributes"], callback = self.sendSelections)
        self.selectionChanged()

        box = OWGUI.widgetBox(smallWidget.widget, orientation = "horizontal")
        OWGUI.widgetLabel(box, "Granularity:  ")
        OWGUI.hSlider(box, self, 'graph.squareGranularity', minValue=1, maxValue=10, step=1, callback = self.updateGraph)

        box = OWGUI.widgetBox(smallWidget.widget, orientation = "horizontal")
        OWGUI.checkBox(box, self, 'graph.spaceBetweenCells', 'Show space between cells', callback = self.updateGraph)

        self.SettingsTab.layout().addStretch(100)

        self.icons = self.createAttributeIconDict()
        self.debugSettings = ["hiddenAttributes", "shownAttributes"]

        dlg = self.createColorDialog()
        self.graph.contPalette = dlg.getContinuousPalette("contPalette")
        self.graph.discPalette = dlg.getDiscretePalette("discPalette")
        self.graph.setCanvasBackground(dlg.getColor("Canvas"))

        apply([self.zoomSelectToolbar.actionZooming, self.zoomSelectToolbar.actionRectangleSelection, self.zoomSelectToolbar.actionPolygonSelection][self.toolbarSelection], [])

        self.cbShowAllAttributes()      # update list boxes based on the check box value

        self.resize(900, 700)

    def saveToFile(self):
        self.graph.saveToFile([("Save PicTex", self.graph.savePicTeX)])

    # #########################
    # KNN OPTIMIZATION BUTTON EVENTS
    # #########################
    def saveCurrentProjection(self):
        qname = QFileDialog.getSaveFileName(self, "Save File",  os.path.realpath(".") + "/Linear_projection.tab", "Orange Example Table (*.tab)")
        if qname.isEmpty(): return
        name = unicode(qname)
        if len(name) < 4 or name[-4] != ".":
            name = name + ".tab"
        self.graph.saveProjectionAsTabData(name, self.getShownAttributeList())


    # send signals with selected and unselected examples as two datasets
    def sendSelections(self):
        if not self.data: return
        (selected, unselected) = self.graph.getSelectionsAsExampleTables(self.getShownAttributeList(), addProjectedPositions = self.addProjectedPositions)

        self.send("Selected Data", selected)
        self.send("Other Data", unselected)

    def sendShownAttributes(self):
        self.send("Features", [a[0] for a in self.shownAttributes])

    # show selected interesting projection
    def showSelectedAttributes(self):
        val = self.vizrank.getSelectedProjection()
        if val:
            (accuracy, other_results, tableLen, attrList, tryIndex, generalDict) = val
            self.updateGraph(attrList, setAnchors= 1, XAnchors = generalDict.get("XAnchors"), YAnchors = generalDict.get("YAnchors"))
            self.graph.removeAllSelections()


    def updateGraphAndAnchors(self):
        self.updateGraph(setAnchors = 1)

    def updateGraph(self, attrList = None, setAnchors = 0, insideColors = None, **args):
        if not attrList:
            attrList = self.getShownAttributeList()
        else:
            self.setShownAttributeList(attrList)

        self.graph.showKNN = 0
        if self.graph.dataHasDiscreteClass:
            self.graph.showKNN = (self.vizrank.showKNNCorrectButton.isChecked() and 1) or (self.vizrank.showKNNCorrectButton.isChecked() and 2)

        self.graph.insideColors = insideColors or self.classificationResults or self.outlierValues
        self.graph.updateData(attrList, setAnchors, **args)


    # ###############################################################################################################
    # INPUT SIGNALS

    # receive new data and update all fields
    def setData(self, data):
        if data is not None and (len(data) == 0 or len(data.domain) == 0):
            data = None
        if self.data and data and self.data.checksum() == data.checksum():
            return    # check if the new data set is the same as the old one

        self.closeContext()
        sameDomain = self.data and data and data.domain.checksum() == self.data.domain.checksum() # preserve attribute choice if the domain is the same
        self.resetAnchors = not sameDomain
        self.data = data
        self.classificationResults = None
        self.outlierValues = None
        self.vizrank.clearResults()
        if hasattr(self, "freeVizDlg"):
            self.freeVizDlg.clearData()
##        self.clusterDlg.setData(data)
        if not sameDomain:
            self.setShownAttributeList(self.attributeSelectionList)
        self.openContext("", self.data)
        self.resetAttrManipulation()


    def setSubsetData(self, subsetData):
        self.subsetData = subsetData
        self.vizrank.clearArguments()

    def setDistances(self, distances):
        self.distances = distances
        
    # attribute selection signal - info about which attributes to show
    def setShownAttributes(self, attributeSelectionList):
        self.attributeSelectionList = attributeSelectionList
        self.resetAnchors = 1


    # this is called by OWBaseWidget after setData and setSubsetData are called. this way the graph is updated only once
    def handleNewSignals(self):
        self.graph.setData(self.data, self.subsetData)
        self.graph.clear()
        self.vizrank.resetDialog()
        if self.attributeSelectionList and 0 not in [self.graph.attributeNameIndex.has_key(attr) for attr in self.attributeSelectionList]:
            self.setShownAttributeList(self.attributeSelectionList)
        self.attributeSelectionList = None
        self.updateGraph(setAnchors = self.resetAnchors)
        self.sendSelections()
        self.resetAnchors = 0


    # visualize the results of the classification
    def setTestResults(self, results):
        self.classificationResults = None
        if isinstance(results, orngTest.ExperimentResults) and len(results.results) > 0 and len(results.results[0].probabilities) > 0:
            self.classificationResults = ([results.results[i].probabilities[0][results.results[i].actualClass] for i in range(len(results.results))], "Probability of correct classificatioin = %.2f%%")
        self.resetAnchors += 1


    # set the learning method to be used in VizRank
    def setVizRankLearner(self, learner):
        self.vizrank.externalLearner = learner

    # EVENTS
    def resetGraphData(self):

        tmp = self.graph.jitter_size      # do not jitter Radviz before final projection,
        if self.graph.normalize_examples: # or points in the center will be scattered all over the place
            self.graph.jitter_size = 0

        self.graph.rescaleData()
        self.graph.jitter_size = tmp

        self.updateGraph()

    def selectionChanged(self):
        self.zoomSelectToolbar.buttonSendSelections.setEnabled(not self.autoSendSelection)
        if self.autoSendSelection:
            self.sendSelections()

    def setColors(self):
        dlg = self.createColorDialog()
        if dlg.exec_():
            self.colorSettings = dlg.getColorSchemas()
            self.selectedSchemaIndex = dlg.selectedSchemaIndex
            self.graph.contPalette = dlg.getContinuousPalette("contPalette")
            self.graph.discPalette = dlg.getDiscretePalette("discPalette")
            self.graph.setCanvasBackground(dlg.getColor("Canvas"))
            self.updateGraph()

    def createColorDialog(self):
        c = OWColorPalette.ColorPaletteDlg(self, "Color palette")
        c.createDiscretePalette("discPalette", "Discrete Palette")
        c.createContinuousPalette("contPalette", "Continuous Palette")
        box = c.createBox("otherColors", "Other Colors")
        c.createColorButton(box, "Canvas", "Canvas color", QColor(Qt.white))
        c.setColorSchemas(self.colorSettings, self.selectedSchemaIndex)
        return c

    def saveSettings(self):
        OWWidget.saveSettings(self)
        self.vizrank.saveSettings()
        if hasattr(self, "freeVizDlg"):
            self.freeVizDlg.saveSettings()

    def hideEvent(self, ev):
        self.vizrank.hide()
        if hasattr(self, "freeVizDlg"):
            self.freeVizDlg.hide()
        OWVisWidget.hideEvent(self, ev)
        

    def sendReport(self):
        self.reportImage(self.graph.saveToFileDirect, QSize(500, 500))
        
#test widget appearance
if __name__=="__main__":
    a=QApplication(sys.argv)
    ow=OWLinProj()
    ow.show()
    #ow.setData(orange.ExampleTable("..\\..\\doc\\datasets\\wine.tab"))
    data = orange.ExampleTable(r"e:\Development\Orange Datasets\brown\brown-selected.tab")
    ow.setData(data)
    ow.handleNewSignals()
    a.exec_()

