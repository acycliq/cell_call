import pandas as pd
import numpy as np
import os.path

my_path = os.path.abspath(os.path.dirname(__file__))


def getNames(n):
    fName = os.path.join(my_path, "../data/yob2017.txt")
    df = pd.read_csv(fName,  names=["Name", "Sex", "Counts"])
    out = np.random.permutation(df.Name)[:n]

    return out


class Geneset:
    def __init__(self,):
        fname = os.path.join(my_path, "../data/gene_exp.msg")
        self._gene_exp = pd.read_msgpack(fname)
        self._cell_name = self.gene_exp.columns.values
        self._gene_name = self.gene_exp.index.values
        self._nGenes = self.gene_name.shape[0]
        self._nCells = self.cell_name.shape[0]

    def getNames(self, n):
        fName = os.path.join(my_path, "../data/yob2017.txt")
        df = pd.read_csv(fName, names=["Name", "Sex", "Counts"])
        out = np.random.permutation(df.Name)[:n]
        return out

    def names_to_Ids(self, Names):
        out = [self.gene_name.index(x) for x in Names]
        # TODO:
        # 1) catch Exception
        # 2) do nothing if Names are integers

        return out

    @property
    def gene_exp(self):
        return self._gene_exp

    @property
    def nGenes(self):
        return self._nGenes

    @property
    def nCells(self):
        return self._nCells

    @property
    def cell_name(self):
        return self._cell_name

    @property
    def gene_name(self):
        return self._gene_name