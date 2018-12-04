import numpy as np
import logging


logger = logging.getLogger()
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s:%(levelname)s:%(message)s"
    )

class Gene(object):
    def __init__(self):
        self.names = None
        self.spotNo = None
        self.totalSpots = None
        self.nG = None
        self.totalBackground = None
        # self._totalZero = None
        self.expectedGamma = None
        self.expression = None
        self.logExpression = None

    # @property
    # def totalZero(self, spots):
    #     self._totalZero = np.bincount(spots.geneNo, spots.zeroProb)
    #     return self._totalZero

    def updateGamma(self, cells, spots, klasses, iss):
        # pSpotZero = spots.zeroKlassProb(klasses, cells)
        TotPredictedZ = spots.TotPredictedZ(spots.geneNo, cells.classProb[:, -1])

        # klassProb = cells.classProb.reshape((cells.nC, 1, klasses.nK))
        # temp = spots.expectedGamma * klassProb * cells.areaFactor[..., None, None]
        # temp = np.sum(temp, axis=0)
        # temp = np.squeeze(temp)
        # ClassTotPredicted = temp * (self.expression + iss.SpotReg)
        # ClassTotPredicted = np.squeeze(ClassTotPredicted)
        # TotPredicted = np.sum(ClassTotPredicted[:, :-1], axis=1)

        TotPredicted = cells.geneCountsPerKlass(self, spots, klasses, iss)

        nom = iss.rGene + self.totalSpots - spots.TotPredictedB - TotPredictedZ
        denom = iss.rGene + TotPredicted
        self.expectedGamma = nom / denom

    def setKlassExpressions(self, klasses, iss, gSet):
        MeanClassExp = np.zeros([self.nG, klasses.nK])
        temp = gSet.GeneSubset(self.names).ScaleCell(0)
        for k in range(klasses.nK - 1):
            val = iss.Inefficiency * np.mean(temp.CellSubset(klasses.name[k]).GeneExp, 1)
            MeanClassExp[:, k] = val[None, :]
        # MeanClassExp = MeanClassExp, (1, self.nG, klasses.nK)
        expression = MeanClassExp
        logExpression = np.log(MeanClassExp + iss.SpotReg)
        self.expression = np.reshape(expression, (1, self.nG, klasses.nK))
        self.logExpression = np.reshape(logExpression, (1, self.nG, klasses.nK))

    def totalZero(self, spots, zeroProb):
        out = np.bincount(spots.geneNo, zeroProb)
        # self._totalZero = out
        # np.bincount(spots.geneNo, pSpotZero)
        return out
