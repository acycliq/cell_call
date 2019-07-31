import numpy as np
import numexpr as ne
import numba as nb
import scipy
import xarray as xr
from skimage.measure import regionprops
import scipy.io as spio
import os
import logging

dir_path = os.path.dirname(os.path.realpath(__file__))
CONFIG_FILE = dir_path + '/config.yml'
# yaml = ruamel.yaml.YAML(typ='safe')

logger = logging.getLogger()
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s:%(levelname)s:%(message)s"
    )



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


def label_spot(a, idx):
    '''
    Given an array a (image_array) and
    :param a: An array of size numPixelsY-by-numPixelsX specifying that element (i,j) belongs to
                cell a[i,j]. Note that array a is 1-based, ie if pixel (i,j) is outside a cell then
                a[i,j] = 0.
    :param idx: An array of size 2-by-N of the pixels coordinates of spot idx[k], k=1...N
    :return:
    a = np.array([  [4,0,1],
                    [2,0,0],
                    [0,1,0]])

    idx = np.array([[0,0],
                    [2, 1],
                    [1,2],
                    [1,3]])

    IndexArrayNan(a, idx.T) = [4., 1., 0., nan]
    which means that:
            spot with coords [0,0] belongs to cell 4
            spot with coords [2,0] belongs to cell 1
            spot with coords [1,2] belongs to 0 (ie no assigned cell)
            spot with coords [1,3] is outside the bounds and assigned to nan

    '''
    assert isinstance(idx[0], np.ndarray), "Array 'idx' must be an array of arrays."
    idx = idx.astype(np.int64)
    out = np.array([])
    dim = np.ones(idx.shape[0], dtype=int)
    dim[:len(a.shape)] = a.shape

    # output array
    out = np.nan * np.ones(idx.shape[1], dtype=int)

    # find the ones within bounds:
    is_within = np.all(idx.T <= dim-1, axis=1)

    # also keep only non-negative ones
    is_positive = np.all(idx.T >= 0, axis=1)

    # filter array`
    arr = idx[:, is_within & is_positive]
    flat_idx = np.ravel_multi_index(arr, dims=dim, order='C')
    out[is_within & is_positive] = a.ravel()[flat_idx]

    return out


def gammaExpectation(rho, beta):
    '''
    :param r:
    :param b:
    :return: Expectetation of a rv X following a Gamma(r,b) distribution with pdf
    f(x;\alpha ,\beta )= \frac{\beta^r}{\Gamma(r)} x^{r-1}e^{-\beta x}
    '''

    # sanity check
    assert (np.all(rho.coords['cell_id'].data == beta.coords['cell_id'])), 'rho and beta are not aligned'
    assert (np.all(rho.coords['gene_name'].data == beta.coords['gene_name'])), 'rho and beta are not aligned'
    r = rho.data[:, :, None]
    b = beta.data
    gamma = np.empty(b.shape)
    ne.evaluate('r/b', out=gamma)
    out = xr.DataArray(gamma,
                       coords={'cell_id': beta.cell_id.values,
                               'gene_name': beta.gene_name.values,
                               'class_name': beta.class_name.values},
                       dims=['cell_id', 'gene_name', 'class_name']
                       )
    return out


def logGammaExpectation(rho, beta):
    '''
    :param r:
    :param b:
    :return: Expectetation of a rv log(X) where X follows a Gamma(r,b) distribution
    '''
    # start = time.time()
    # out = scipy.special.psi(r) - np.log(b)
    # end = time.time()
    # print('time in logGammaExpectation:', end - start)
    # start = time.time()

    # sanity check
    assert (np.all(rho.coords['cell_id'].data == beta.coords['cell_id'])), 'rho and beta are not aligned'
    assert (np.all(rho.coords['gene_name'].data == beta.coords['gene_name'])), 'rho and beta are not aligned'
    r = rho.data[:, :, None]
    b = beta.data
    logb = np.empty(b.shape)
    ne.evaluate("log(b)", out=logb)
    log_gamma = scipy.special.psi(r) - logb

    out = xr.DataArray(log_gamma,
                       coords={'cell_id': beta.cell_id.values,
                               'gene_name': beta.gene_name.values,
                               'class_name': beta.class_name.values},
                       dims=['cell_id', 'gene_name', 'class_name']
                       )
    # end = time.time()
    # print('time in logGammaExpectation ne:', end - start)
    return out


def negBinLoglik(da_x, r, da_p):
    '''
    Negative Binomial loglikehood
    :param x:
    :param r:
    :param p:
    :return:
    '''

    # sanity check
    assert (np.all(da_x.coords['cell_id'].data == da_p.coords['cell_id'])), 'gene counts and beta probabilities are not aligned'
    assert (np.all(da_x.coords['gene_name'].data == da_p.coords['gene_name'])), 'gene counts and beta probabilities are not aligned'

    contr = np.zeros(da_p.shape)
    x = da_x.data[:, :, None]
    p = da_p.data
    # start = time.time()
    # out = x * np.log(p, where=x.astype(bool)) + r * np.log(1-p)
    # end = time.time()
    # print('time in negBinLoglik:', end - start)
    # start = time.time()
    ne.evaluate("x * log(p) + r * log(1 - p)", out=contr)
    # end = time.time()
    # print('time in negBinLoglik - ne:', end - start)

    out = xr.DataArray(contr,
                       coords={'cell_id': da_p.cell_id.values,
                               'gene_name': da_p.gene_name.values,
                               'class_name': da_p.class_name.values},
                       dims=['cell_id', 'gene_name', 'class_name']
                       )

    return out


def _negBinLoglik(x, r, p):
    '''
    Negative Binomial loglikehood
    :param x:
    :param r:
    :param p:
    :return:
    '''
    out=np.zeros(p.shape)
    # start = time.time()
    # out = x * np.log(p, where=x.astype(bool)) + r * np.log(1-p)
    # end = time.time()
    # print('time in negBinLoglik:', end - start)
    # start = time.time()
    ne.evaluate("x * log(p) + r * log(1 - p)", out=out)
    # end = time.time()
    # print('time in negBinLoglik - ne:', end - start)
    return out

@nb.njit(parallel=True, fastmath=True)
def nb_negBinLoglik(x, r, p):
    '''
    Negative Binomial loglikehood
    :param x:
    :param r:
    :param p:
    :return:
    '''
    out = np.empty(p.shape,p.dtype)

    for i in nb.prange(p.shape[0]):
        for j in range(p.shape[1]):
            if x[i, j, 0] != 0.:
                x_ = x[i, j, 0]
                for k in range(p.shape[2]):
                    out[i, j, k] = x_ * np.log(p[i, j, k]) + r * np.log(1.-p[i, j, k])
            else:
                for k in range(p.shape[2]):
                    out[i, j, k] = r * np.log(1.-p[i, j, k])

    return out


def softmax(x):
    '''
    https://stackoverflow.com/questions/34968722/how-to-implement-the-softmax-function-in-python
    :param x:
    :return:
    '''
    """Compute softmax values for each sets of scores in x."""
    assert 'class_name' in x.dims, 'There is not dimension "class_name" '
    temp = xr.ufuncs.exp(x)
    return temp / temp.sum('class_name')


def softmax2(x):
    '''
    https://stackoverflow.com/questions/34968722/how-to-implement-the-softmax-function-in-python
    :param x:
    :return:
    '''
    """Compute softmax values for each sets of scores in x."""
    return np.exp(x) / np.sum(np.exp(x), axis=1)[:, None]



def isConverged(spots, p0, tol):
    p1 = spots.neighboring_cells['prob']
    if p0 is None:
        p0 = np.zeros(p1.shape)
    delta = np.max(np.abs(p1 - p0))
    converged = (delta < tol)
    return converged, delta


def bi2(X, dims, *args):
    nK = dims[1]
    inds = []
    if len(args) == 2:
        # print('im in!')
        args = (*args, np.arange(0, nK))

    temp = np.zeros(dims).astype(int)
    for i in range(len(args)):
        inds.append(temp + args[i])

    # out = X[inds]
    return X[inds]
