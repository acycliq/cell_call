import utils
import numpy as np
import pandas as pd
from skimage.measure import regionprops
from sklearn.neighbors import NearestNeighbors
from time import time
import logging

logger = logging.getLogger()
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s:%(levelname)s:%(message)s"
    )


def preprocess(iss, gSet):
    spots = filter_spots(iss)
    cellinfo = cell_info(iss)
    ini = initialise(spots, cellinfo, iss, gSet)


# @utils.cached('filter_spots_cache.pickle')
def filter_spots(iss):
    excludeGenes = ['Vsnl1', 'Atp1b1', 'Slc24a2', 'Tmsb10', 'Calm2', 'Gap43', 'Fxyd6']
    allGeneNames = iss.GeneNames[iss.SpotCodeNo - 1]  # -1 is needed because Matlab is 1-based
    cond1 = ~np.isin(allGeneNames, excludeGenes)
    start_time = time()
    cond2 = utils.inpolygon(iss.SpotGlobalYX, iss.CellCallRegionYX)
    print('Elapsed time: ' + str(time() - start_time))

    cond3 = qualityThreshold(iss)

    includeSpot = cond1 & cond2 & cond3
    spotYX = iss.SpotGlobalYX[includeSpot, :].round()
    spotGeneName = allGeneNames[includeSpot]

    out = dict()
    out["spotYX"] = spotYX
    out["spotGeneName"] = spotGeneName
    return out


def qualityThreshold(iss):
    qualOk = iss.SpotCombi & (iss.SpotScore > iss.CombiQualThresh) & (
                iss.SpotIntensity > iss.CombiIntensityThresh);

    anchorsOk = np.ones(qualOk.shape)
    isGreater = iss.cAnchorIntensities > iss.DetectionThresh
    tot = isGreater.sum(axis=1)
    idx = tot > iss.CombiAnchorsReq

    anchorsOk[np.array(iss.SpotCombi, dtype=bool)] = idx
    qualOk = np.array(qualOk, dtype=bool) & np.array(anchorsOk, dtype=bool)
    nCombiCodes = np.array([x != 'EXTRA' for x in iss.CharCodes]).sum()

    for i in range(iss.ExtraCodes.shape[0]):
        my_spots = iss.SpotCodeNo == nCombiCodes + (i + 1)
        my_spots = np.array(my_spots, dtype=bool)
        thres = iss.ExtraCodes[i, 3]
        isAboveThres = iss.SpotIntensity[my_spots] > thres
        qualOk[my_spots] = isAboveThres

    return qualOk


# @utils.cached('cell_info_cache.pickle')
def cell_info(iss):
    '''
    Read image and calc some statistics
    :return:
    '''
    y0 = iss.CellCallRegionYX[:, 0].min()
    x0 = iss.CellCallRegionYX[:, 1].min()

    matStr = "..\data\CellMap.mat"
    logger.info("reading CellMap from %s", matStr)
    mat = utils.loadmat(matStr)
    #cell_map = mat["CellMap"]

    rp = regionprops(mat["CellMap"])
    cellYX = np.array([x.centroid for x in rp]) + np.array([y0, x0])

    cellArea0 = np.array([x.area for x in rp])
    meanCellRadius = np.mean(np.sqrt(cellArea0 / np.pi)) * 0.5;

    relCellRadius = np.sqrt(cellArea0 / np.pi) / meanCellRadius
    relCellRadius = np.append(relCellRadius, 1)

    logger.info("Rebasing CellYX to match the one-based indexed Matlab object. ")
    cellYX = cellYX + 1

    out = dict()
    out["cellYX"] = cellYX
    out["meanCellRadius"] = meanCellRadius
    out["relCellRadius"] = relCellRadius
    return out


# @utils.cached('ini_cache.pickle')
def initialise(spots, cellinfo, iss, gSet):

    # 1) Get Genenames etc
    [GeneNames, SpotGeneNo, TotGeneSpots] = np.unique(spots['spotGeneName'], return_inverse=True, return_counts=True)

    # 2) Get the class name and add an extra class, labeled 'Zero'
    ClassNames = np.append(pd.unique(gSet.Class), 'Zero')

    # 3) calc the prior
    LogClassPrior = getLogClassPrior(ClassNames)

    # 4) get the log-mean expression across all classes
    lMeanClassExp, MeanClassExp = getClassExpression(GeneNames, ClassNames, iss, gSet)

    # 5) calc loglikelihood
    D, Neighbors, SpotInCell = loglik(cellinfo, spots, iss)

    # 6) calc the cell area factor
    CellAreaFactor = getCellAreaFactor(cellinfo, iss)

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


def getLogClassPrior(ClassNames):
    print('in logClassPrior')
    # uniform prior on Zero and non-zero classes
    nK = ClassNames.shape[0]
    classPrior = np.append([.5 * np.ones(nK - 1) / nK], 0.5)
    logClassPrior = np.log(classPrior)
    return logClassPrior


def getClassExpression(GeneNames, ClassNames, iss, gSet):
    print('in classExpression')
    nG = GeneNames.shape[0]
    nK = ClassNames.shape[0]
    MeanClassExp = np.zeros([nK, nG])
    temp = gSet.GeneSubset(GeneNames).ScaleCell(0)
    for k in range(nK - 1):
        val = iss.Inefficiency * np.mean(temp.CellSubset(ClassNames[k]).GeneExp, 1)
        MeanClassExp[k, :] = val

    logMeanClassExp = np.log(MeanClassExp + iss.SpotReg)

    return logMeanClassExp, MeanClassExp


def getCellAreaFactor(cellinfo, iss):
    relCellRadius = cellinfo["relCellRadius"]
    nom = np.exp(-relCellRadius ** 2 / 2) * (1 - np.exp(iss.InsideCellBonus)) + np.exp(iss.InsideCellBonus)
    denom = np.exp(-0.5) * (1 - np.exp(iss.InsideCellBonus)) + np.exp(iss.InsideCellBonus)
    cellAreaFactor = nom / denom

    return cellAreaFactor


def loglik(cellinfo, spots, iss):
    cellYX = cellinfo['cellYX']
    spotYX = spots['spotYX']
    meanCellRadius = cellinfo["meanCellRadius"]
    nC = cellYX.shape[0] + 1
    nN = iss.nNeighbors + 1

    # for each spot find the closest cell (in fact the top nN-closest cells...)
    nbrs = NearestNeighbors(n_neighbors=nN, algorithm='ball_tree').fit(cellYX)
    Dist, Neighbors = nbrs.kneighbors(spotYX)

    # Assign the nN-closest neighbour to an out-of-bounds value. (I would use -1 here instead of nC, anyways...)
    Neighbors[:, -1] = nC

    # Assume a bivariate normal and calc the likelihood
    D = -Dist ** 2 / (2 * meanCellRadius ** 2) - np.log(2 * np.pi * meanCellRadius ** 2)

    # last column (nN-closest) keeps the misreads,
    D[:, -1] = np.log(iss.MisreadDensity)


    y0 = iss.CellCallRegionYX[:, 0].min()
    x0 = iss.CellCallRegionYX[:, 1].min()
    logger.info("Rebasing SpotYX to match the one-based indexed Matlab object.")
    spotyx = spotYX - 1 # I DO NOT THINK THIS IS NEEDED!! REMOVE IT!
    idx = spotyx - [y0, x0]
    SpotInCell = utils.IndexArrayNan(iss.cell_map, idx.T) # I DONT QUITE GET THAT. WHY NOT JUST CHECKING IF Dist<meanCellRadius INSTEAD?
    logger.info("Rebasing Neighbors to match the one-based indexed Matlab object.")
    sanity_check = Neighbors[SpotInCell > 0, 0] + 1 == SpotInCell[SpotInCell > 0]
    assert ~any(sanity_check), "a spot is in a cell not closest neighbor!"

    D[SpotInCell > 0, 0] = D[SpotInCell > 0, 0] + iss.InsideCellBonus

    return D, Neighbors, SpotInCell
