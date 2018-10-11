import copy
import numpy as np
import pandas as pd
import logging
import copy

logger = logging.getLogger()
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s:%(levelname)s:%(message)s"
    )

class Base(object):
    def get_attr(self):
        return [a for a in dir(self) if not a.startswith('__') and not callable(getattr(self, a))]

    def _carve_out(self, IDs, flag):
        if flag == 'Genes':
            out = self._carve_out_genes(IDs)
        elif flag == 'Cells':
            out = self._carve_out_cells(IDs)
        else:
            print('I shouldnt be here')
        return out

    def _carve_out_genes(self, IDs):
        dc = copy.deepcopy(self)
        dc.GeneExp_df = self.GeneExp_df.loc[IDs, :]
        id_matched = np.isin(IDs, self.GeneName)
        if ~id_matched.all():
            unmatched = IDs[~id_matched]
            if len(unmatched) == 1:
                msg = "The ID: %s is missing from GeneNames" % unmatched
            else:
                msg = "These IDs: %s are missing from GeneNames" % unmatched
            logger.info(msg)
        return dc

    def _carve_out_cells(self, IDs):
        dc = copy.deepcopy(self)
        mask = None
        if np.issubdtype(np.array(IDs).dtype, np.number):
            dc.GeneExp_df = self.GeneExp_df.iloc[:, IDs]
        elif np.issubdtype(np.array(IDs).dtype, np.bool_):
            dc.GeneExp_df = self.GeneExp_df.iloc[:, IDs]
        elif np.issubdtype(np.array(IDs).dtype, np.str_):
            mask = self.Class == IDs
            if np.issubdtype(np.array(mask).dtype, np.bool_):
                print(self.GeneExp.shape)
                print(mask.shape)
                dc.GeneExp_df = self.GeneExp_df.loc[:, mask]
            else:
                dc.GeneExp_df = self.GeneExp_df[IDs]
        return dc
