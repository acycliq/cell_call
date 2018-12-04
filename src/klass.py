import numpy as np
import pandas as pd
import logging


logger = logging.getLogger()
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s:%(levelname)s:%(message)s"
    )

class Klass(object):
    def __init__(self, gSet):
        self.nK = None
        self.name = None
        self.prior = None
        self.logPrior = None
        self._populate(gSet)

    def _populate(self, gSet):
        self.name = np.append(pd.unique(gSet.Class), 'Zero')
        self.nK = self.name.shape[0]
        self.prior = np.append([.5 * np.ones(self.nK - 1) / self.nK], 0.5)
        self.logPrior = np.log(self.prior)


def negBinLoglik(x, r, p):
    '''
    Negative Binomial loglikehood
    :param x:
    :param r:
    :param p:
    :return:
    '''
    out = x * np.log(p) + r * np.log(1-p)
    return out