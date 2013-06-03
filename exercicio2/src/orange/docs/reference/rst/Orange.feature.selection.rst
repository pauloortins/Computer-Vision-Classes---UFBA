.. :py:currentmodule:: Orange.feature.selection

#########################
Selection (``selection``)
#########################

.. index:: feature selection

.. index::
   single: feature; feature selection

Feature selection module contains several utility functions for selecting features based on they scores normally
obtained in classification or regression problems. A typical example is the function :obj:`select`
that returns a subsets of highest-scored features features:

.. literalinclude:: code/selection-best3.py
    :lines: 7-

The script outputs::

    Best 3 features:
    physician-fee-freeze
    el-salvador-aid
    synfuels-corporation-cutback

The module also includes a learner that incorporates feature subset
selection.

--------------------------------------
Functions for feature subset selection
--------------------------------------

.. automethod:: Orange.feature.selection.top_rated

.. automethod:: Orange.feature.selection.above_threshold

.. automethod:: Orange.feature.selection.select

.. automethod:: Orange.feature.selection.select_above_threshold

.. automethod:: Orange.feature.selection.select_relief(data, measure=Orange.feature.scoring.Relief(k=20, m=10), margin=0)

--------------------------------------
Learning with feature subset selection
--------------------------------------

.. autoclass:: Orange.feature.selection.FilteredLearner(base_learner, filter=FilterAboveThreshold(), name=filtered)
   :members:

.. autoclass:: Orange.feature.selection.FilteredClassifier
   :members:


--------------------------------------
Class wrappers for selection functions
--------------------------------------

.. autoclass:: Orange.feature.selection.FilterAboveThreshold(data=None, measure=Orange.feature.scoring.Relief(k=20, m=50), threshold=0.0)
   :members:

Below are few examples of utility of this class::

    >>> filter = Orange.feature.selection.FilterAboveThreshold(threshold=.15)
    >>> new_data = filter(data)
    >>> new_data = Orange.feature.selection.FilterAboveThreshold(data)
    >>> new_data = Orange.feature.selection.FilterAboveThreshold(data, threshold=.1)
    >>> new_data = Orange.feature.selection.FilterAboveThreshold(data, threshold=.1, \
        measure=Orange.feature.scoring.Gini())

.. autoclass:: Orange.feature.selection.FilterBestN(data=None, measure=Orange.feature.scoring.Relief(k=20, m=50), n=5)
   :members:

.. autoclass:: Orange.feature.selection.FilterRelief(data=None, measure=Orange.feature.scoring.Relief(k=20, m=50), margin=0)
   :members:



.. rubric:: Examples

The following script defines a new Naive Bayes classifier, that
selects five best features from the data set before learning.
The new classifier is wrapped-up in a special class (see
:doc:`/tutorial/rst/python-learners` lesson in
:doc:`/tutorial/rst/index`). Th script compares this filtered learner with
one that uses a complete set of features.

:download:`selection-bayes.py<code/selection-bayes.py>`

.. literalinclude:: code/selection-bayes.py
    :lines: 7-

Interestingly, and somehow expected, feature subset selection
helps. This is the output that we get::

    Learner      CA
    Naive Bayes  0.903
    with FSS     0.940

We can do all of  he above by wrapping the learner using
:class:`~Orange.feature.selection.FilteredLearner`, thus
creating an object that is assembled from data filter and a base learner. When
given a data table, this learner uses attribute filter to construct a new
data set and base learner to construct a corresponding
classifier. Attribute filters should be of the type like
:class:`~Orange.feature.selection.FilterAboveThreshold` or
:class:`~Orange.feature.selection.FilterBestN` that can be initialized with
the arguments and later presented with a data, returning new reduced data
set.

The following code fragment replaces the bulk of code
from previous example, and compares naive Bayesian classifier to the
same classifier when only a single most important attribute is
used.

:download:`selection-filtered-learner.py<code/selection-filtered-learner.py>`

.. literalinclude:: code/selection-filtered-learner.py
    :lines: 13-16

Now, let's decide to retain three features and observe how many times
an attribute was used. Remember, 10-fold cross validation constructs
ten instances for each classifier, and each time we run
:class:`~.FilteredLearner` a different set of features may be
selected. ``Orange.evaluation.testing.cross_validation`` stores classifiers in
``results`` variable, and :class:`~.FilteredLearner`
returns a classifier that can tell which features it used, so the code
to do all this is quite short.

.. literalinclude:: code/selection-filtered-learner.py
    :lines: 25-

Running :download:`selection-filtered-learner.py <code/selection-filtered-learner.py>`
with three features selected each time a learner is run gives the
following result::

    Learner      CA
    bayes        0.903
    filtered     0.956

    Number of times features were used in cross-validation:
     3 x el-salvador-aid
     6 x synfuels-corporation-cutback
     7 x adoption-of-the-budget-resolution
    10 x physician-fee-freeze
     4 x crime


==========
References
==========

* K. Kira and L. Rendell. A practical approach to feature selection. In
  D. Sleeman and P. Edwards, editors, Proc. 9th Int'l Conf. on Machine
  Learning, pages 249{256, Aberdeen, 1992. Morgan Kaufmann Publishers.

* I. Kononenko. Estimating attributes: Analysis and extensions of RELIEF.
  In F. Bergadano and L. De Raedt, editors, Proc. European Conf. on Machine
  Learning (ECML-94), pages  171-182. Springer-Verlag, 1994.

* R. Kohavi, G. John: Wrappers for Feature Subset Selection, Artificial
  Intelligence, 97 (1-2), pages 273-324, 1997
