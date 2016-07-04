yacluster
========

yacluster is a Python library which does `distance-based clustering`_ for 2D points. Only Python 3.4+ is officially supported, though other versions may work too. The project uses `semantic versioning`_ and is licensed under `the MIT license`_.

Usage
-----

The main utility is the ``yacluster.cluster`` function which takes two arguments:

* an iterable which yields two-element point tuples, each containing:
  - a two-element tuple with X and Y coordinates;
  - the actual object being clustered (or its identifier);
* a distance threshold; if a point is included into a cluster, it must be closer to its centroid than this value.

The function returns an iterable of two-element cluster tuples, each containing:

* a two-element tuple with X and Y coordinates of the cluster center;
* a list of objects belonging to the cluster.

Cluster’s centroid is defined as average coordinates of the cluster’s members.

Example
-------

.. code-block:: python

   from yacluster import cluster

   points = [
       ((1, 1.0), 'Foo'),
       ((1.0, 2), 'Bar'),
       ((2.0, 2.0), 'Baz'),
   ]
   threshold = 1.1
   expected_result =  [
       ((1.0, 1.5), ['Foo', 'Bar']),
       ((2.0, 2.0), ['Baz']),
   ]
   assert expected_result == list(cluster(points, threshold))

Development
-----------

Development requirements are listed in the ``requirements-development.txt`` file.

To run tests, execute ``./tests.py``.

Coding style is checked using `flake8 3.x`_.

.. _distance-based clustering: https://developers.google.com/maps/articles/toomanymarkers#distancebasedclustering
.. _flake8 3.x: http://flake8.pycqa.org/en/latest/
.. _semantic versioning: http://semver.org
.. _the MIT license: LICENSE
