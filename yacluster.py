from functools import partial, reduce
from itertools import chain, product
from math import sqrt


def distance(coords_1, coords_2):
    return sqrt(pow(coords_1[0] - coords_2[0], 2) + pow(coords_1[1] - coords_2[1], 2))


def get_grid_cell(x, y, threshold):
    return (int(x // threshold), int(y // threshold))


def get_nearby_grid_cells(grid_cell):
    grid_x, grid_y = grid_cell
    return [(i, j) for i, j in product(range(grid_x - 1, grid_x + 2), range(grid_y - 1, grid_y + 2))]


def cluster_iter(clustered, point, threshold):
    """Add a point to a grid-like cluster structure.

    This allows comparing point distances only to clusters from nearby grids, not to all clusters. Useful when there are many clusters expected."""
    coords, object_ = point
    point_grid_cell = get_grid_cell(*coords, threshold=threshold)
    nearby_grid_cells = get_nearby_grid_cells(point_grid_cell)
    possible_nearby_cluster_locations = chain(
        *[(location for location in clustered.get(grid_cell, {})) for grid_cell in nearby_grid_cells]
    )

    def nearest_location(champion_with_distance, pretender, coords=coords, threshold=threshold):
        pretender_distance = distance(coords, pretender)
        if pretender_distance < threshold:
            if champion_with_distance and champion_with_distance[1] <= pretender_distance:
                return champion_with_distance
            else:
                return (pretender, pretender_distance)
        else:
            return champion_with_distance

    nearest_cluster_with_distance = reduce(nearest_location, possible_nearby_cluster_locations, None)
    if nearest_cluster_with_distance:
        nearest_cluster_location, _nearest_cluster_distance = nearest_cluster_with_distance
    else:
        nearest_cluster_location = None

    if nearest_cluster_location:
        cluster_grid_cell = get_grid_cell(*nearest_cluster_location, threshold=threshold)
        cluster = clustered[cluster_grid_cell].pop(nearest_cluster_location)
        cluster_object_count = len(cluster)
        new_cluster_location = (
            (nearest_cluster_location[0] * cluster_object_count + coords[0]) / (cluster_object_count + 1),
            (nearest_cluster_location[1] * cluster_object_count + coords[1]) / (cluster_object_count + 1),
        )
    else:
        cluster = []
        new_cluster_location = coords
    cluster.append(point)
    new_cluster_grid_cell = get_grid_cell(*new_cluster_location, threshold=threshold)
    clustered.setdefault(new_cluster_grid_cell, {})
    clustered[new_cluster_grid_cell][new_cluster_location] = cluster

    return clustered


def cluster(points, threshold):
    """Cluster points using distance-based clustering algorithm.

    Arguments:
    points — an iterable of two-element point tuples, each containing:
      • a two-element tuple with X and Y coordinates,
      • the actual object being clustered;
    threshold — if a point is included into a cluster, it must be closer to its centroid than this value.

    Return value:
    an iterable of two-element cluster tuples, each containing:
      • a two-element tuple with X and Y coordinates of the cluster centroid;
      • a list of objects belonging to the cluster.

    Cluster’s centroid is defined as average coordinates of the cluster’s members.
    """
    cluster_iter_for_threshold = partial(cluster_iter, threshold=threshold)
    clustered = reduce(cluster_iter_for_threshold, points, {})
    return chain(
        *[((location, [object_ for coords, object_ in points]) for location, points in grid_clusters.items())
          for grid_clusters in clustered.values()]
    )
