import numpy as np
import scipy.io as spio
import os
import pickle
from shapely.geometry import Point, MultiPoint, Polygon
import logging


logger = logging.getLogger()
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s:%(levelname)s:%(message)s"
    )

def parse_mat_array(name):
# TODO
# Make the code more generic. Not only for 3-D arrays
#

    proj_path = os.path.abspath(os.path.dirname(__file__))
    rel_path = "../data/" + name + ".mat"
    path_str = os.path.join(proj_path, rel_path)
    print(path_str)
    mat = spio.loadmat(path_str)
    x = mat[name]
    out = np.nan * np.ones(x.shape, dtype=object)

    for i in range(out.shape[0]):
        for j in range(out.shape[1]):
            for k in range(out.shape[2]):
                out[i, j, k] = x[i, j, k]

    return out


def loadmat(filename):
    '''
    this function should be called instead of direct spio.loadmat
    as it cures the problem of not properly recovering python dictionaries
    from mat files. It calls the function check keys to cure all entries
    which are still mat-objects

    from: `StackOverflow <http://stackoverflow.com/questions/7008608/scipy-io-loadmat-nested-structures-i-e-dictionaries>`_
    '''
    data = spio.loadmat(filename, struct_as_record=False, squeeze_me=True)
    return _check_keys(data)


def _check_keys(dict):
    '''
    checks if entries in dictionary are mat-objects. If yes
    todict is called to change them to nested dictionaries
    '''
    for key in dict:
        if isinstance(dict[key], spio.matlab.mio5_params.mat_struct):
            dict[key] = _todict(dict[key])
    return dict


def _todict(matobj):
    '''
    A recursive function which constructs from matobjects nested dictionaries
    '''
    dict = {}
    for strg in matobj._fieldnames:
        elem = matobj.__dict__[strg]
        if isinstance(elem, spio.matlab.mio5_params.mat_struct):
            dict[strg] = _todict(elem)
        else:
            dict[strg] = elem
    return dict


def inpolygon(xq, yq, xv, yv):
    '''
    :param xq:
    :param yq:
    :param xv:
    :param yv:
    :return:
    '''

    # create the polygon
    coords = list(zip(xv, yv))
    poly = Polygon(coords)

    # create a list of Points
    pts = MultiPoint(list(zip(xq, yq)))

    # check if point is inside or on the edge
    isInside = [pt.within(poly) for pt in pts]
    isOn = [pt.touches(poly) for pt in pts]

    out = np.array(isInside) | np.array(isOn)
    return out



def ismember(a, b):
    '''
    From https://stackoverflow.com/questions/15864082/python-equivalent-of-matlabs-ismember-function
    :param a:
    :param b:
    :return:
    '''
    bind = {}
    for i, elt in enumerate(b):
        if elt not in bind:
            bind[elt] = i
    return [bind.get(itm, None) for itm in a]


class IterMixin(object):
    def __iter__(self):
        for attr, value in self.__dict__.items():
            yield attr, value



def cached(cachefile):
    """
    A function that creates a decorator which will use "cachefile" for caching the results of the decorated function "fn".
    From: https://datascience.blog.wzb.eu/2016/08/12/a-tip-for-the-impatient-simple-caching-with-python-pickle-and-decorators/
    """
    def decorator(fn):  # define a decorator for a function "fn"
        def wrapped(*args, **kwargs):   # define a wrapper that will finally call "fn" with all arguments
            # if cache exists -> load it and return its content
            if os.path.exists(cachefile):
                    with open(cachefile, 'rb') as cachehandle:
                        logger.info("reading cached result from '%s' ..." % cachefile)
                        pkl = pickle.load(cachehandle)
                        logger.info("...finished")
                        return pkl

            # execute the function with all arguments passed
            res = fn(*args, **kwargs)

            # write to cache file
            with open(cachefile, 'wb') as cachehandle:
                logger.info("saving result to cache '%s'" % cachefile)
                pickle.dump(res, cachehandle)

            return res

        return wrapped

    return decorator   # return this "customized" decorator that uses "cachefile"


def IndexArrayNan(a, idx):
    assert isinstance(idx[0], np.ndarray), "Array 'idx' must be an array of arrays."
    idx = idx.astype(np.int64)
    out = np.array([])
    dim = np.ones(idx.shape[0], dtype=int)
    dim[:len(a.shape)] = a.shape

    # output array
    out = np.nan * np.ones(idx.shape[1])

    # find the ones within bounds:
    is_within = np.all(idx.T <= dim-1, axis=1)

    # also keep only non-negative ones
    is_positive = np.all(idx.T >= 0, axis=1)

    # filter array`
    arr = idx[:, is_within & is_positive]
    flat_idx = np.ravel_multi_index(arr, dims=dim, order='C')
    out[is_within & is_positive] = a.ravel()[flat_idx]

    return out

def LogLtoP(L):
    L1 = L - np.max(L, axis=1)[:, None]
    eL = np.exp(L1)
    p = eL / np.sum(eL, axis=1)[:, None]
    return p


def bi(X, *args):
    inds = []
    ZeroIndexArray = 0
    for i in range(len(args)):
        ZeroIndexArray = ZeroIndexArray * args[i]

    for i in range(len(args)):
        inds.append(ZeroIndexArray + args[i])

    inds = np.ravel_multi_index(inds, X.shape, order='F')
    out = X[np.unravel_index(inds, X.shape, order='F')]

    return out
