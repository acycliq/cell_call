import numpy as np
import numpy_groupies as npg
import pandas as pd
import os
import scipy
import src.utils as utils
from src.iss import Iss
from src.geneset import GeneSet
from skimage.measure import regionprops
from sklearn.neighbors import NearestNeighbors
import logging


logger = logging.getLogger()
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s:%(levelname)s:%(message)s"
    )


class Call_cells:
    def __init__(self):
        #create iss and gSet objects and add them as propertie
        self._iss = Iss()
        self._gSet = GeneSet()

    @property
    def iss(self):
        return self._iss

    @property
    def gSet(self):
        return self._gSet

    @property
    def SpotGeneName(self):
        return self._spots["SpotGeneName"]

    @property
    def SpotYX(self):
        return self._spots["SpotYX"]

    @property
    def CellYX(self):
        return self._cellinfo["CellYX"]

    @property
    def MeanCellRadius(self):
        return self._cellinfo["MeanCellRadius"]

    @property
    def RelCellRadius(self):
        return self._cellinfo["RelCellRadius"]

    @property
    def GeneNames(self):
        return self._ini["GeneNames"]

    @property
    def SpotGeneNo(self):
        return self._ini["SpotGeneNo"]

    @property
    def TotGeneSpots(self):
        return self._ini["TotGeneSpots"]

    @property
    def ClassNames(self):
        return self._ini["ClassNames"]

    @property
    def MeanClassExp(self):
        return self._ini["MeanClassExp"]

    @property
    def lMeanClassExp(self):
        return self._ini["lMeanClassExp"]

    @property
    def Neighbors(self):
        return self._ini["Neighbors"]

    @property
    def D(self):
        return self._ini["D"]

    @property
    def LogClassPrior(self):
        return self._ini["LogClassPrior"]

    @property
    def CellAreaFactor(self):
        return self._ini["CellAreaFactor"]

    @property
    def SpotInCell(self):
        return self._ini["SpotInCell"]

    @property
    def Converged(self):
        return self._cal["Converged"]

    @property
    def pSpotNeighb(self):
        return self._cal["pSpotNeighb"]

    @property
    def CellGeneCount(self):
        return self._cal["CellGeneCount"]

    @property
    def pCellClass(self):
        return self._cal["pCellClass"]

    @property
    def eGeneGamma(self):
        return self._cal["eGeneGamma"]


    def run(self):
        self.preprocess()
        self._cal = self._calc()

    def preprocess(self):
        self._spots = self._filter_spots()
        self._cellinfo = self._cell_info()
        self._ini = self._initialise()

    @utils.cached('filter_spots_cache.pickle')
    def _filter_spots(self):
        exclude_genes = ['Vsnl1', 'Atp1b1', 'Slc24a2', 'Tmsb10', 'Calm2', 'Gap43', 'Fxyd6']
        all_gene_names = self.iss.GeneNames[self.iss.SpotCodeNo-1] # -1 is needed because Matlab is 1-based
        cond_1 = ~np.isin(all_gene_names, exclude_genes)
        cond_2 = utils.inpolygon(self.iss.SpotGlobalYX[:, 0], self.iss.SpotGlobalYX[:, 1], self.iss.CellCallRegionYX[:, 0], self.iss.CellCallRegionYX[:, 1])
        cond_3 = self._quality_threshold()

        include_spot = cond_1 & cond_2 & cond_3
        SpotYX = self.iss.SpotGlobalYX[include_spot, :].round()
        SpotGeneName = all_gene_names[include_spot]

        out = dict()
        out["SpotYX"] = SpotYX
        out["SpotGeneName"] = SpotGeneName
        return out

    def _quality_threshold(self):
        qual_ok = self.iss.SpotCombi & (self.iss.SpotScore > self.iss.CombiQualThresh) & (self.iss.SpotIntensity > self.iss.CombiIntensityThresh);

        anchors_ok = np.ones(qual_ok.shape)
        is_greater = self.iss.cAnchorIntensities > self.iss.DetectionThresh
        tot = is_greater.sum(axis=1)
        idx = tot > self.iss.CombiAnchorsReq

        anchors_ok[np.array(self.iss.SpotCombi, dtype=bool)] = idx
        qual_ok = np.array(qual_ok, dtype=bool) & np.array(anchors_ok, dtype=bool)
        nCombiCodes = np.array([x != 'EXTRA' for x in self.iss.CharCodes]).sum()

        for i in range(self.iss.ExtraCodes.shape[0]):
            my_spots = self.iss.SpotCodeNo == nCombiCodes + (i+1)
            my_spots = np.array(my_spots, dtype=bool)
            thres = self.iss.ExtraCodes[i, 3]
            is_above_thres = self.iss.SpotIntensity[my_spots] > thres
            qual_ok[my_spots] = is_above_thres

        return qual_ok

    @utils.cached('cell_info_cache.pickle')
    def _cell_info(self):
        '''
        Read image and calc some statistics
        :return:
        '''
        y0 = self.iss.CellCallRegionYX[:, 0].min()
        x0 = self.iss.CellCallRegionYX[:, 1].min()

        mat = utils.loadmat(self.iss.CellMapFile)
        rp = regionprops(mat["CellMap"])
        CellYX = np.array([x.centroid for x in rp]) + np.array([y0, x0])

        CellArea0 = np.array([x.area for x in rp])
        MeanCellRadius = np.mean(np.sqrt(CellArea0 / np.pi)) * 0.5;

        RelCellRadius = np.sqrt(CellArea0 / np.pi) / MeanCellRadius
        RelCellRadius = np.append(RelCellRadius, 1)

        logger.info("Rebasing CellYX to match the one-based indexed Matlab object. ")
        CellYX = CellYX + 1

        out = dict()
        out["CellYX"] = CellYX
        out["MeanCellRadius"] = MeanCellRadius
        out["RelCellRadius"] = RelCellRadius
        return out

    @utils.cached('ini_cache.pickle')
    def _initialise(self):
        [GeneNames, SpotGeneNo, TotGeneSpots] = np.unique(self.SpotGeneName, return_inverse=True, return_counts=True)
        ClassNames = np.append(pd.unique(self.gSet.Class), 'Zero')

        nG = GeneNames.shape[0]
        nK = ClassNames.shape[0]
        nC = self.CellYX.shape[0] + 1
        nS = self.SpotYX.shape[0]
        nN = self.iss.nNeighbors + 1

        ClassPrior = np.append([.5 * np.ones(nK - 1) / nK], 0.5);

        MeanClassExp = np.zeros([nK, nG])
        temp = self.gSet.GeneSubset(GeneNames).ScaleCell(0)
        for k in range(nK-1):
            val = self.iss.Inefficiency * np.mean(temp.CellSubset(ClassNames[k]).GeneExp, 1);
            MeanClassExp[k, :] = val

        lMeanClassExp = np.log(MeanClassExp + self.iss.SpotReg)
        nbrs = NearestNeighbors(n_neighbors=nN, algorithm='ball_tree').fit(self.CellYX)
        Dist, Neighbors = nbrs.kneighbors(self.SpotYX)
        Neighbors[:, -1] = nC

        D = -Dist**2 / (2 * self.MeanCellRadius**2) - np.log(2*np.pi*self.MeanCellRadius**2)
        D[:, -1] = np.log(self.iss.MisreadDensity)

        y0 = self.iss.CellCallRegionYX[:, 0].min()
        x0 = self.iss.CellCallRegionYX[:, 1].min()
        logger.info("Rebasing SpotYX to match the one-based indexed Matlab object.")
        spotyx = self.SpotYX - 1
        idx = spotyx - [y0, x0]
        SpotInCell = utils.IndexArrayNan(self.iss.cell_map, idx.T)
        logger.info("Rebasing Neighbors to match the one-based indexed Matlab object.")
        sanity_check = Neighbors[SpotInCell > 0, 0] + 1 == SpotInCell[SpotInCell > 0]
        assert ~any(sanity_check), "a spot is in a cell not closest neighbor!"

        D[SpotInCell > 0, 0] = D[SpotInCell > 0, 0] + self.iss.InsideCellBonus
        LogClassPrior = np.log(ClassPrior)
        nom = np.exp(-self.RelCellRadius**2/2) * ( 1 - np.exp(self.iss.InsideCellBonus)) + np.exp(self.iss.InsideCellBonus)
        denom = np.exp(-0.5) * (1 - np.exp(self.iss.InsideCellBonus)) + np.exp(self.iss.InsideCellBonus)
        CellAreaFactor = nom / denom

        out = dict()
        out["GeneNames"] = GeneNames
        out["SpotGeneNo"] = SpotGeneNo
        out["TotGeneSpots"] = TotGeneSpots
        out["ClassNames"] = ClassNames
        out["MeanClassExp"] = MeanClassExp
        out["lMeanClassExp"] = lMeanClassExp
        out["Neighbors"] = Neighbors
        out["D"] = D
        out["LogClassPrior"] = LogClassPrior
        out["CellAreaFactor"] = CellAreaFactor
        out["SpotInCell"] = SpotInCell
        return out

    def _calc(self):
        nG = self.GeneNames.shape[0]
        nK = self.ClassNames.shape[0]
        nC = self.CellYX.shape[0] + 1
        nS = self.SpotYX.shape[0]
        nN = self.iss.nNeighbors + 1

        pSpotNeighb = np.zeros([nS, nN])
        pCellClass = np.zeros([nC, nK])

        pSpotNeighb[self.Neighbors + 1 == self.SpotInCell[:, None]] = 1
        pSpotNeighb[self.SpotInCell == 0, -1] = 1

        eSpotGamma = np.ones([nC, nK, nG]);
        elSpotGamma = np.ones([nC, nK, nG]) * scipy.special.psi(1)

        eGeneGamma = np.ones(nG)

        pSpotNeighbOld = np.zeros([nS, nN])

        for i in range(self.iss.CellCallMaxIter):

            CellGeneCount = np.zeros([nC, nG]);
            for n in range(nN-1):
                c = self.Neighbors[:, n]
                group_idx = np.vstack((c[None, :], self.SpotGeneNo[None, :]))
                a = pSpotNeighb[:, n]
                accumarray = npg.aggregate(group_idx, a, func="sum", size=(nC, nG))
                CellGeneCount = CellGeneCount + accumarray

            ScaledMean = np.transpose(np.dstack([self.MeanClassExp.T] * len(self.CellAreaFactor)) * self.CellAreaFactor, (2, 1, 0))
            eSpotGamma = (self.iss.rSpot + np.reshape(CellGeneCount, (nC, 1, nG), order='F') ) / (self.iss.rSpot + ScaledMean)
            elSpotGamma = scipy.special.psi(self.iss.rSpot + np.reshape(CellGeneCount, (nC, 1, nG))) - np.log(self.iss.rSpot + ScaledMean)

            ScaledExp = np.reshape(self.MeanClassExp, (1, nK, nG)) * np.reshape(eGeneGamma, (1, 1, nG)) * self.CellAreaFactor[..., None, None] + self.iss.SpotReg
            pNegBin = ScaledExp / (self.iss.rSpot + ScaledExp)
            wCellClass = np.sum(np.reshape(CellGeneCount, (nC, 1, nG)) * np.log(pNegBin) + self.iss.rSpot * np.log(1 - pNegBin), axis = 2) + self.LogClassPrior
            pCellClass = utils.LogLtoP(wCellClass)

            aSpotCell = np.zeros([nS, nN])
            for n in range(nN-1):
                c = self.Neighbors[:, n]
                term_1 = np.sum(pCellClass[c, :] * self.lMeanClassExp[:, self.SpotGeneNo].T, axis=1)
                temp = utils.bi(elSpotGamma, c[:, None], np.arange(0, nK), self.SpotGeneNo[:, None])
                term_2 = np.sum(pCellClass[c, :] * temp, axis=1)
                aSpotCell[:, n] = term_1 + term_2
            wSpotCell = aSpotCell + self.D

            pSpotNeighb = utils.LogLtoP(wSpotCell)
            MeanProbChanged = np.max(np.abs(pSpotNeighb-pSpotNeighbOld))
            logger.info('Iteration %d, mean prob change %f' % (i, MeanProbChanged))
            Converged = (MeanProbChanged < self.iss.CellCallTolerance)
            pSpotNeighbOld = pSpotNeighb

            TotPredictedB = np.bincount(self.SpotGeneNo, pSpotNeighb[:, -1])
            pCellZero = pCellClass[:, nK-1]
            pSpotZero = np.sum(pSpotNeighb[:, 0: nN - 1] * pCellZero[self.Neighbors[:, 0: nN - 1]], axis=1)
            TotPredictedZ = np.bincount(self.SpotGeneNo, pSpotZero)

            temp = eSpotGamma * pCellClass[..., None] * self.CellAreaFactor[..., None, None]
            ClassTotPredicted = np.squeeze(np.sum(temp, axis=0))*(self.MeanClassExp + self.iss.SpotReg)
            TotPredicted = np.sum(ClassTotPredicted[np.arange(0, nK - 1), :], axis=0)
            eGeneGamma = (self.iss.rGene + self.TotGeneSpots - TotPredictedB - TotPredictedZ) / (self.iss.rGene + TotPredicted)

            if Converged:
                print("Success!!")
                break

        out = dict()
        out["Converged"] = Converged
        out["pSpotNeighb"] = pSpotNeighb
        out["CellGeneCount"] = CellGeneCount
        out["pCellClass"] = pCellClass
        out["eGeneGamma"] = eGeneGamma
        return out






if __name__ == "__main__":
    cl = Call_cells()
    cl.run()
    print("done")