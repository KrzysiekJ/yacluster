#!/usr/bin/env python
from math import log, sqrt
from functools import reduce
from itertools import product
import random
import sys

from hypothesis import given
from hypothesis.strategies import floats, integers, lists, one_of, random_module, tuples, text
import pytest

from yacluster import cluster


# Hypothesis strategies definitions.

def coordinates():
    """Return a Hypothesis strategy which yields valid point coordinates."""
    return one_of(
        floats(
            min_value=-100.0,
            max_value=100.0,
        ),
        integers(
            min_value=-100,
            max_value=100,
        ),
    )


def thresholds():
    """Return a Hypothesis strategy which yields valid clustering thresholds."""
    floats_or_integers = one_of(floats(min_value=1e-6), integers())
    return floats_or_integers.map(abs).filter(lambda x: x)


def points():
    """Return a Hypothesis strategy which yields point tuples."""
    return tuples(
        tuples(coordinates(), coordinates()),
        text(min_size=1),
    )


def point_lists(**kwargs):
    """Return a Hypothesis which yields lists of point tuples containing unique objects."""
    return lists(
        points(),
        unique_by=lambda point: point[1],
        **kwargs
    )


# Helper functions.

def distance(coords_1, coords_2):
    x_1, y_1 = coords_1
    x_2, y_2 = coords_2
    return sqrt(pow(x_1 - x_2, 2) + pow(y_1 - y_2, 2))


def point_distance(point_1, point_2):
    coords_1, object_1 = point_1
    coords_2, object_2 = point_2
    return distance(coords_1, coords_2)


def get_coords(object_, points):
    """Return coordinates for an object which is somewhere in a list of points."""
    return next(coords for coords, maybe_this_object in points if maybe_this_object == object_)


def average_coords(coords):
    coords_list = list(coords)
    coords_sum = reduce(
        lambda coords_sum, coords: (coords_sum[0] + coords[0], coords_sum[1] + coords[1]),
        coords_list,
    )
    count = len(coords_list)
    return (coords_sum[0] / count, coords_sum[1] / count)


# Actual tests.

@given(point_lists(), thresholds())
def test_points_in_cluster_are_somewhat_close(points, threshold):
    """Ensure that distance between any two points in n-element cluster is less than the (n–1)-th harmonic number times threshold.

    We approximate the n-th harmonic number by its boundary: ln(n) + 1.
    """
    clustered = cluster(points, threshold)
    assert all(
        all(distance(coords_1, coords_2) < (log(len(objects) - 1) + 1) * threshold
            for coords_1, coords_2 in product(*2 * [[get_coords(object_, points) for object_ in objects]]))
        for center, objects in clustered if len(objects) > 1)


@given(point_lists(), thresholds())
def test_cluster_centers_are_points_average(points, threshold):
    """Ensure that cluster center is the average of coordinates of its points."""
    clustered = cluster(points, threshold)
    assert all(
        distance(center, average_coords(get_coords(object_, points) for object_ in objects)) < 5e-8
        for center, objects in clustered
    )


@given(point_lists(), thresholds())
def test_points_are_in_exactly_one_cluster_each(points, threshold):
    clustered = cluster(points, threshold)
    clusters = [objects for center, objects in clustered]
    assert all(
        len(list(filter(lambda objects: object_ in objects, clusters))) == 1
        for (coords, object_) in points)


@given(point_lists(min_size=2, max_size=6).filter(lambda point_list: point_distance(*point_list[:2]) < 40), random_module())
def test_two_points_cannot_be_in_singleton_clusters_both_if_they_are_close(points, rand_module):
    points_shuffled = points.copy()
    random.shuffle(points_shuffled)
    clustered = list(cluster(points_shuffled, 40))
    assert any(
        len(next(objects for center, objects in clustered if object_ in objects)) > 1
        for coords, object_ in points[:2]
    )


@given(point_lists(), thresholds(), random_module())
def test_clustering_is_deterministic(points, threshold, rand_module):
    assert list(cluster(points, threshold)) == list(cluster(points, threshold))


@given(point_lists(min_size=2, max_size=2).filter(lambda point_list: point_distance(*point_list) > 1e-4))
def test_point_is_added_to_the_nearest_already_created_cluster(points):
    """Ensure that a point is added to the nearest already created cluster (assuming that point order is not abused).

    The Google’s description states that the point is added to the nearest nearby cluster. However we could just add to it a an arbitrary nearby cluster (bypassing some computations) and claim that it could be the nearest cluster if only the point order was different.

    So why do we make this test? It’s because choosing some arbitrary method of picking a nearby cluster could bias our results and render them statistically non-symmetrical.
    """
    [(coords_1, object_1), (coords_2, object_2)] = [point_1, point_2] = points
    object_3 = 'An average of 1 point “{}” and 2 points {}'.format(object_1, object_2)
    point_3 = (
        average_coords([coords_1, coords_2, coords_2]),
        object_3,
    )
    threshold = distance(coords_1, coords_2) * 0.95
    assert all(
        sorted([[object_1], [object_2, object_3]]) == sorted(objects for center, objects in cluster(points, threshold))
        for points in [[point_1, point_2, point_3], [point_2, point_1, point_3]]
    )


# Command-line execution.
if __name__ == '__main__':
    sys.exit(pytest.main(sys.argv))
