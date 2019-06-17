import os
from sklearn.neighbors import NearestNeighbors
import logging

dir_path = os.path.dirname(os.path.realpath(__file__))
CONFIG_FILE = dir_path + '/config.yml'


logger = logging.getLogger()
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s:%(levelname)s:%(message)s"
    )


def closestCell(spotYX, cellYX, config):
    n = config['nNeighbors']
    # for each spot find the closest cell (in fact the top nN-closest cells...)
    nbrs = NearestNeighbors(n_neighbors=n, algorithm='ball_tree').fit(cellYX)
    dist, neighbors = nbrs.kneighbors(spotYX)

    return dist, neighbors


