###############
Getting Started
###############


The tutorial on these pages is meant for those who are interested in
developing widgets in Orange. Orange Widgets are components in
Orange's visual programming environment. They are wrappers around some
data analysis code that provide graphical user interface
(GUI). Widgets communicate, and pass tokens through communication
channels to interact with other widgets. While simplest widgets
consist of even less than 100 lines of code, those more complex that
often implement some fancy graphical display of data and allow for
some really nice interaction may be over 1000 lines long.

When we have started to write this tutorial, we have been working
on widgets for quite a while. There are now (now being in the very
time this page has been crafted) about 50 widgets available, and we
have pretty much defined how widgets and their interfaces should look
like. We have also made some libraries that help set up GUI with only
a few lines of code, and some mechanisms that one may found useful and
user friendly, like progress bars and alike.

On this page, we will start with some simple essentials, and then
show how to build a simple widget that will be ready to run within
Orange Canvas, our visual programming environment.

*************
Prerequisites
*************

Each Orange widget belongs to a category and within a
category has an associated priority. Opening Orange Canvas, a visual
programming environment that comes with Orange, widgets are listed in
toolbox on the top of the window:

.. image:: widgettoolbox.png

By default, Orange is installed in site-packages directory of
Python libraries. Widgets are all put in the subdirectories of
OrangeWidget directory; these subdirectories define widget
categories. For instance, under windows and default settings, a
directory that stores all the widgets displayed in the Evaluate pane is
*C:\\Python23\\Lib\\site-packages\\Orange\\OrangeWidgets\\Evaluate*. Figure
above shows that at the time of writing of this text there were five
widgets for evaluation of classifiers, and this is how my Evaluate
directory looked like:

.. image:: explorer.png

Notice that there are a number of files in Evaluate directory, so
how does Orange Canvas distinguish those that define widgets? Well,
widgets are Python script files that start with a header. Here is a
header for OWTestLearners.py::

    <name>Test Learners</name>
    <description>Estimates the predictive performance of learners on a data set.</description>
    <icon>icons/TestLearners.png</icon>
    <priority>200</priority>

OWTestLearners is a Python script, so the header information we
show about lies within the comment block, with triple quote opening
and closing the comment. Header defines the name of the widget, its
description, the name of the picture file the widget will use for an
icon, and a number expressing the priority of the widget. The name of
the widget as given in the header will be the one that will be used
throughout in Orange Canvas. As for naming, the actual file name of
the widget is not important. The description of the widget is shown
once mouse rests on an toolbar icon representing the widget. And for
the priority: this determines the order in which widgets appear in the
toolbox. The one shown above for Evaluate groups has widget named Test
Learners with priority 200, Classifications with 300, ROC Analysis
with 1010, Lift Curve with 1020 and Calibration Plot with 1030. Notice
that every time the priority number crosses a multiplier of a 1000,
there is a gap in the toolbox between the widgets; in this way, a
subgroups of the widgets within the same group can be imposed.

Widgets communicate. They use typed channels, and exchange
tokens. Each widget would define its input and output channels in
something like::

    self.inputs = [("Test Data Set", ExampleTable, self.cdata),
                   ("Learner", orange.Learner, self.learner, 0)]
    self.outputs = [("Evaluation Results", orngTest.ExperimentResults)]

Above two lines are for Test Learners widget, so hovering with your
mouse over its icon in the widget toolbox would yield:

.. image:: mouseoverwidgetintoolbox.png

We will go over the syntax of channel definitions later, but for
now the following is important:

   - Widgets are defined in a Python files.
   - For Orange and Orange canvas to find them, they reside in subdirectories
     in OrangeWidgets directory of Orange installation. The name of the
     subdirectory matters, as this is the name of the widget category. Widgets
     in the same directory will be grouped in the same pane of widget toolbox
     in Orange Canvas.
   - A file describing a widget starts with a header. This, given in sort of
     XMLish style, tells about the name, short description, location of an
     icon and priority of the widget.
   - The sole role of priority is to specify the placement (order) of widgets
     in the Orange Canvas toolbox.
   - Somewhere in the code (where we will learn later) there are two lines
     which tell which channels the widgets uses for communication. These,
     together with the header information, completely specify the widget as it
     is seen from the outside.

Oh, by the way. Orange caches widget descriptions to achieve a faster
startup, but this cache is automatically refreshed at startup if any change
is detected in widgets' files.

***********
Let's Start
***********

Now that we went through some of the more boring stuff, let us now
have some fun and write a widget. We will start with a very simple
one, that will receive a data set on the input and will output a data
set with 10% of the data instances. Not to mess with other widgets, we
will create a Test directory within OrangeWidgets directory, and write
the widget in a file called `OWDataSamplerA.py`: OW for Orange Widget,
DataSampler since this is what widget will be doing, and A since we
prototype a number of this widgets in our tutorial.

The script defining the OWDataSamplerA widget starts with a follwing header::

    <name>Data Sampler</name>
    <description>Randomly selects a subset of instances from the data set</description>
    <icon>icons/DataSamplerA.png</icon>
    <priority>10</priority>

This should all be clear now, perhaps just a remark on an icon. We
can put any name here, and if Orange Canvas won't find the
corresponding file, it will use a file called Unknown.png (an icon
with a question mark).

Orange Widgets are all derived from the class OWWidget. The name of
the class should be match the file name, so the lines following the
header in our Data Sampler widget should look something like::

    from OWWidget import *
    import OWGUI

    class OWDataSamplerA(OWWidget):

        def __init__(self, parent=None, signalManager=None):
            OWWidget.__init__(self, parent, signalManager, 'SampleDataA')

            self.inputs = [("Data", ExampleTable, self.data)]
            self.outputs = [("Sampled Data", ExampleTable)]

            # GUI
            box = OWGUI.widgetBox(self.controlArea, "Info")
            self.infoa = OWGUI.widgetLabel(box, 'No data on input yet, waiting to get something.')
            self.infob = OWGUI.widgetLabel(box, '')
            self.resize(100,50)

In initialization, the widget calls the :obj:`__init__` function
of a base class, passing the name 'SampleData' which will,
essentially, be used for nothing else than a stem of a file for saving
the parameters of the widgets (we will regress on these somehow
latter in tutorial). Widget then defines inputs and outputs. For
input, widget defines a "Data" channel, accepting tokens of the type
orange.ExampleTable and specifying that :obj:`data` function will
be used to handle them. For now, we will use a single output channel
called "Sampled Data", which will be of the same type
(orange.ExampleTable).

Notice that the types of the channels are
specified by a class name; you can use any classes here, but if your
widgets need to talk with other widgets in Orange, you will need to
check which classes are used there. Luckily, and as one of the main
design principles, there are just a few channel types that current
Orange widgets are using.

The next four lines specify the GUI of our widget. This will be
simple, and will include only two lines of text of which, if nothing
will happen, the first line will report on "no data yet", and second
line will be empty. By (another) design principles, in an interface
Orange widgets are most often split to control and main area. Control
area appears on the left and should include any controls for settings
or options that your widget will use. Main area would most often
include a graph, table or some drawing that will be based on the
inputs to the widget and current options/setting in the control
area. OWWidget make these two areas available through its attributes
:obj:`self.controlArea` and :obj:`self.mainArea`. Notice
that while it would be nice for all widgets to have this common visual
look, you can use these areas in any way you want to, even disregarding one
and composing your widget completely unlike the others in Orange.

As our widget won't display anything apart from some info, we will
place the two labels in the control area and surround it with the box
"Info".

In order to complete our widget, we now need to define how will it
handle the input data. This is done in a function called
:obj:`data` (remember, we did introduce this name in the
specification of the input channel)::

    def data(self, dataset):
        if dataset:
            self.infoa.setText('%d instances in input data set' % len(dataset))
            indices = orange.MakeRandomIndices2(p0=0.1)
            ind = indices(dataset)
            sample = dataset.select(ind, 0)
            self.infob.setText('%d sampled instances' % len(sample))
            self.send("Sampled Data", sample)
        else:
            self.infoa.setText('No data on input yet, waiting to get something.')
            self.infob.setText('')
            self.send("Sampled Data", None)

The function is defined within a class definition, so its first
argument has to be :obj:`self`. The second argument called
:obj:`dataset` is the token sent through the input channel which
our function needs to handle.

To handle the non-empty token, the widget updates the interface
reporting on number of data items on the input, then does the data
sampling using Orange's routines for these, and updates the
interface reporting on the number of sampled instances. Finally, the
sampled data is sent as a token to the output channel with a name
"Sampled Data".

Notice that the token can be empty (``dataset is None``),
resulting from either the sending widget to which we have connected
intentionally emptying the channel, or when the link between the two
widgets is removed. In any case, it is important that we always write
token handlers that appropriately handle the empty tokens. In our
implementation, we took care of empty input data set by appropriately
setting the GUI of a widget and sending an empty token to the
output channel.

..
   Although our widget is now ready to test, for a final touch, let's
   design an icon for our widget. As specified in the widget header, we
   will call it :download:`DataSamplerA.png <DataSamplerA.png>` and will
   put it in icons subdirectory of OrangeWidgets directory (together with
   all other icons of other widgets).

For a test, we now open Orange Canvas. There should be a new pane in a
widget toolbox called Test (this is the name of the directory we have
used to put in our widget). If we click on this pane, it displays an
icon of our widget. Try to hoover on it to see if the header and
channel info was processed correctly:

.. image:: samplewidgetontoolbox.png

Now for the real test. We put the File widget on the schema (from
Data pane), read iris.tab data set. We also put our Data Sampler widget on the pane and
open it (double click on the icon, or right-click and choose
Open):

.. image:: datasamplerAempty.png

Drag this window off the window with the widget schema of Orange
Canvas, and connect File and Data Sampler widget (click on an ouput
connector - green box - of the File widget, and drag the line to the
input connector of the Data Sampler). If everything is ok, as soon as
you release the mouse the connection is established and, the token
that was waiting on the output of the file widget was sent to the Data
Sampler widget, which in turn updated its window:

.. image:: datasamplerAupdated.png

To see if the Data Sampler indeed sent some data to the output,
connect it to the Data Table widget:

.. image:: schemawithdatatable.png

Try opening different data files (the change should propagate
through your widgets and with Data Table window open, you should
immediately see the result of sampling). Try also removing the
connection between File and Data Sampler (right click on the
connection, choose Remove). What happens to the data displayed in the
Data Table?

*****************************************
Testing Your Widget Outside Orange Canvas
*****************************************

When prototyping a single widget, for a fast test I often get
bored of running Orange Canvas, setting the schema and clicking on
icons to get widget windows. There are two options to bypass this. The
first one is to add a testing script at the end of your widget. To do
this, we finished Data Sampler with::

    if __name__=="__main__":
        appl = QApplication(sys.argv)
        ow = OWDataSamplerA()
        ow.show()
        dataset = orange.ExampleTable('iris.tab')
        ow.data(dataset)
        appl.exec_()

These are essentially some calls to Qt routines that run GUI for our
widgets. At the core, however, notice that instead of sending the
token to the input channel, we directly called the routine for token
handling (:obj:`data`).

To test your widget in more complex environment, that for instance
requires to set a complex schema in which your widget collaborates,
use Orange Canvas to set the schema and then either 1) save the schema
to be opened every time you run Orange Canvas, or 2) save this schema
(File menu) as an application within a single file you will need to
run each time you will test your widget.
