import numpy as np
import pandas as pd
import xarray as xr
import time
import random
import os
import errno
import logging

logger = logging.getLogger()
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s:%(levelname)s:%(message)s"
    )



def fetch_data(dataset_name):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    print(dir_path)

    if dataset_name == 'DEFAULT':
        df = pd.read_json("https://raw.githubusercontent.com/acycliq/issplus/master/dashboard/data/img/default/json/iss.json")
        GeneExp = np.load(dir_path + '/../data_preprocessed/default/GeneExp.npy')
        eGeneGamma = [line.rstrip("\n''") for line in open(dir_path + '/../data_preprocessed/default/eGeneGamma.csv')]
        eGeneGamma = [float(i) for i in eGeneGamma]
        genes = [line.rstrip("\n''") for line in open(dir_path + '/../data_preprocessed/default/genes.csv')]
    elif dataset_name == 'DEFAULT_42GENES':
        df = pd.read_json(dir_path + '/../dashboard/data/img/default_42genes/json/iss.json')
        GeneExp = np.load(dir_path + '/../data_preprocessed/default_42genes/GeneExp.npy')
        eGeneGamma = [line.rstrip("\n''") for line in open(dir_path + '/../data_preprocessed/default_42genes/eGeneGamma.csv')]
        eGeneGamma = [float(i) for i in eGeneGamma]
        genes = [line.rstrip("\n''") for line in open(dir_path + '/../data_preprocessed/default_42genes/genes.csv')]
    elif dataset_name == 'DEFAULT_99GENES':
        df = pd.read_json(dir_path + '/../dashboard/data/img/default_99genes/json/iss.json')
        GeneExp = np.load(dir_path + '/../data_preprocessed/default_99genes/GeneExp.npy')
        eGeneGamma = [line.rstrip("\n''") for line in open(dir_path + '/../data_preprocessed/default_99genes/eGeneGamma.csv')]
        eGeneGamma = np.array([float(i) for i in eGeneGamma])
        genes = [line.rstrip("\n''") for line in open(dir_path + '/../data_preprocessed/default_99genes/genes.csv')]
    elif dataset_name == 'DEFAULT_98GENES':
        df = pd.read_json(dir_path + '/../dashboard/data/img/default_98genes/json/iss.json')
        GeneExp = np.load(dir_path + '/../data_preprocessed/default_98genes/GeneExp.npy')
        eGeneGamma = [line.rstrip("\n''") for line in open(dir_path + '/../data_preprocessed/default_98genes/eGeneGamma.csv')]
        eGeneGamma = np.array([float(i) for i in eGeneGamma])
        genes = [line.rstrip("\n''") for line in open(dir_path + '/../data_preprocessed/default_98genes/genes.csv')]
    else:
        dataset_name == ''


    ctc = [line.rstrip("\n''") for line in open(dir_path + '/../data_preprocessed/cell_to_class_map.csv')]

    # Rename PC.CA2 to PC.Other1 and PC.CA3 to PC.Other2
    ctc = ['PC.Other1' if x == 'PC.CA2' else x for x in ctc]
    ctc = ['PC.Other2' if x == 'PC.CA3' else x for x in ctc]

    ge = xr.DataArray(GeneExp, coords=[genes, ctc], dims=['Genes', 'Class'])

    return df, ge, eGeneGamma

def best_class(df):
    '''
    Returns a list with the names of all the optimal/best classes
    '''
    class_name = df['ClassName']
    prob = df['Prob']
    out = [class_name[n][np.argmax(prob[n])] for n in range(class_name.shape[0])]
    return out

def draw_gene_expression(df, ge, eGeneGamma, alpha, beta):
    # cell class (unique and ranked alphabetically)
    # best_classes = sorted(set(df['best_class']))
    # totalCountsArray = getTotalGeneCounts(df)
    class_list = ge.Class.values.tolist()
    N = df.shape[0]
    M = ge.shape[0]
    out = {'cid': [],
           'best_class': [],
           'Cell_Num': [],
           'X': [],
           'Y': [],
           'class_name': [],
           'gene_name': ge.Genes.values.tolist(),
           'colNum': [],
           'GenExp': np.empty([M, N], dtype=np.int32),
           }
    for i in range(N):  # loop over the cells
        # select a class
        bc = df['best_class'].iloc[i]
        # totalCounts = totalCountsArray[i]
        totalCounts = df['totalGeneCounts'].iloc[i]
        _cell_num = df['Cell_Num'].iloc[i]
        _x = df['X'].iloc[i]
        _y = df['Y'].iloc[i]
        # print(bc)

        # carve out data only relevant to the selected class
        class_df = df[df['best_class'] == bc]

        # randomly select a cell of that specific class
        cid = np.random.choice(class_df.index)
        # temp = class_df.loc[cid]

        # keep the data for that particular cell to a dictionary
        out['cid'].append(cid)
        out['Cell_Num'].append(_cell_num)  # Cell_Num is 1-based, not 0-based
        out['X'].append(_x)
        out['Y'].append(_y)
        out['class_name'].append(bc)
        # start = time.time()
        mask = [i for i in range(len(class_list)) if class_list[i] == bc]
        # print(time.time() - start)

        # select a column randomly
        colNum = np.random.choice(mask)
        out['colNum'].append(colNum)
        col = ge[:, colNum].values
        # draw N counts with prob p

        # multiply now by the eGeneGamma
        col = col * eGeneGamma

        # derive the relative weights of each gene
        p = [x/sum(col) for x in col]

        # draw now a random sample genes. How many? as many as you have in the original
        # cell scaled by the parameters alpha and beta
        temp = np.random.multinomial(totalCounts * alpha * (1-beta), p)

        # append and make a gene expression matrix for you simulated spots
        out['GenExp'][:, i] = temp

    print('In draw_gene_expression')
    print('Cell at i = 1444 is %d ' % df.iloc[1444]['Cell_Num'])
    print('Cell at i = 1444 initially had %.2f ' % df.loc[2278]['totalGeneCounts'])
    print('Cell at i = 1444 now has %.2f ' % sum(df['CellGeneCount'].loc[2278]))
    print('Sum of out at column i = 1444 is %d ' % sum(out['GenExp'][:, 1444]))
    return out


def thinner(data, eGeneGamma):
    p = np.array([min(1.0, x) for x in eGeneGamma])
    mat = data['GenExp']
    rnd = np.random.binomial(mat, p[:, None])
    data['GenExp'] = rnd
    return data


def inflate(elem, counts):
    '''
    repeats each element in elem as many times as shown in the corresponding location in counts.
    Example:
        elem = ['name_1', 'name_2']
        counts = [3, 2]
        out = ['name_1', 'name_1', 'name_1', 'name_2', 'name_2']
    :param elem: A list
    :param counts: A list
    :return: A numpy array
    '''

    assert len(elem) == len(counts)
    l = []
    for i in range(len(elem)):
        x = [elem[i]] * np.int(counts[i])
        l.append(x)

    out = [item for sublist in l for item in sublist]
    return np.array(out)


def position_genes(data):
    r = 8.8673

    # make an array the same dim as GenExp filled with the gene names (ie repeat the gene_names num-of-columns times)
    gn = np.array(data['gene_name'])
    gn_arr = np.tile(gn[:, None], data['GenExp'].shape[1])

    # u = np.random.normal(0, r, data['GenExp'].shape)
    # v = np.random.normal(0, r, data['GenExp'].shape)

    # make an array the same dim as GenExp to keep the x and y
    # coordinates of the corresponding cells when the gene expression
    # is greater than zero
    _x = (data["X"])*(data['GenExp'] > 0)
    _y = (data["Y"])*(data['GenExp'] > 0)

    # unstack (ie turn the 2d array in to one hugh column
    x = _x.flatten()
    y = _y.flatten()
    gene_exp = data['GenExp'].flatten()
    gene_names = gn_arr.flatten()

    # find the positions where the column-arrays are zero
    xZero = x == 0
    yZero = y == 0
    gene_expZero = gene_exp == 0

    # Check if the are zero at the same array position (they should!)
    assert np.all(xZero == yZero)
    assert np.all(xZero == gene_expZero)
    assert np.all(yZero == gene_expZero)

    # Throw away the zero values
    x = x[~xZero]
    y = y[~yZero]
    gene_exp = gene_exp[~gene_expZero]
    gene_names = gene_names[~gene_expZero]

    # expand xCoord by repeating each element as many time as shown in the corresponding position in
    # the gene_exp array. Do the same for yCoord and gene_names
    x = inflate(x.tolist(), gene_exp.tolist())
    y = inflate(y.tolist(), gene_exp.tolist())

    # generate normal distributed numbers centered at (x,y) with stdev = r
    u = np.random.normal(x, r, x.shape[0])
    v = np.random.normal(y, r, y.shape[0])
    gene_names = inflate(gene_names.tolist(), gene_exp.tolist())

    out = np.hstack((gene_names[:, None], u[:, None], v[:, None]))

    # sanity check (length of out should be the same as sum of all elements in GenExp
    assert out.shape[0] == data['GenExp'].sum()
    return out


def flatten(df):
    '''
    flattens a dataframe
    '''
    temp = df.unstack()
    values = temp.values
    labels = temp.index.droplevel().values
    out = np.hstack( (labels[:, None], values[:, None]) )
    return out


def xy_pairs(x, y):
    '''
    zips x, y lists to produce the coordinates
    '''

    # check is x and y are aligned
    assert np.all(x[:, 0] == y[:, 0])

    # remove if both are zero
    isZero = (np.array(x[:, 1]) == 0) & (np.array(y[:, 1]) == 0)
    x = x[~isZero, :]
    y = y[~isZero, :]

    # return the gene names and associated coordinates
    _labels = x[:, 0]
    _x = x[:, 1]
    _y = y[:, 1]
    out = np.hstack((_labels[:, None], _x[:, None], _y[:, None]))
    return out


def post_process(df1, df2):
    x = flatten(df1)
    y = flatten(df2)
    out = xy_pairs(x, y)
    return out


def checkFile(filename_out):
    # remove the file if it exists
    try:
        os.remove(filename_out)
        logger.info(' File %s exists. DELETED! ' % filename_out)
    except OSError:
        pass


def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc: # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise


def inject(raw_data, sample, perc):
    '''
    :param sample:
    :param univ:
    :param perc:
    :param selectFrom:
    :return: an array the same size as sample['GenExp'] which defines how many extra spots per cell we can sample.
            For example x_ij means that for class j we will draw x_ij more spots of gene i.
            Note also that sample['GenExp'] is a resampled gene expression matrix, of dimension numGenes-by-numCells
    '''
    allGenes = sample['gene_name']

    # take the total gene count for each cell type
    gc = raw_data['totalGeneCounts']

    # percentage of total gene counts we want to inject
    # perc = 0.10
    newSpotsCounts = [int(x * perc) for x in gc]

    out = np.zeros(sample['GenExp'].shape)
    assert out.shape[1] == len(sample['class_name'])
    for i, cn in enumerate(sample['class_name']):
        numSpots = newSpotsCounts[i]
        newGenes = sorted(np.random.choice(allGenes, numSpots, replace=True))
        binNames, binCounts = np.unique(newGenes, return_counts=True)
        idx = [allGenes.index(x) for x in binNames]
        out[idx, i] = binCounts

    return out


def dropout(data, perc):
    '''
    Return a dataframe where the genes have be removed in a propotional to the total gene counts manner
    :param sample:
    :param univ:
    :param perc:
    :return:
    '''

    # loop over all cells in the raw_data
    col = []
    for i in range(data.shape[0]):
        p = data['genesProb'].iloc[i]
        N = data['totalGeneCounts'].iloc[i]
        cgc = data['CellGeneCount'].iloc[i]

        # draw N * perc counts with prob p
        temp = np.random.multinomial(N*perc, p)

        # remove the randomly selected counts from the original gene counts
        newCounts = np.array(cgc) - temp

        # make sure you have no negatives
        newCounts = [max(x, 0) for x in newCounts]

        col.append(newCounts)

        # now put the newCounts into the raw_data
        # //raw_data['CellGeneCount'].iloc[i] = newCounts

    data['CellGeneCount'] = col
    return data


def cellType_geneUniverse(gene_expression):
    '''
    :param gene_expression: The (Full) gene expression matrix (xarray)
    :return: a dictionary where the keys are the cell types and values the genes that can that particular cell type can contain
    '''
    out = {}
    cellTypes = np.unique(gene_expression.Class.values)
    for i, cellType in enumerate(cellTypes):
        # print(cellType)
        temp = gene_expression[:, gene_expression.Class == cellType]
        inCellType = temp.sum(axis=1) > 0
        val = temp.Genes[inCellType].values
        out[cellType] = val
    return out


def getGenesProb(df):
    p = []
    total = []
    # loop over the cells
    for i in range(df.shape[0]):
        geneName = df['Genenames'].iloc[i]
        geneCounts = df['CellGeneCount'].iloc[i]
        N = sum(geneCounts)
        temp = [x/N for x in geneCounts]
        p.append(temp)
        total.append(N)

    return p, total


def getTotalGeneCounts(df):
    p = []
    out = []
    # loop over the cells
    for i in range(df.shape[0]):
        geneCounts = df['CellGeneCount'].iloc[i]
        N = sum(geneCounts)
        out.append(N)

    return out


def adjust(raw_data, sample):
    '''
    adjust the expression matrix. Draw gene expressions using the proportions of the original cell
    but using the total gene counts (ie sum of gene expressions) from the randomly selected cell
    :param raw_data:
    :param sample:
    :return:
    '''
    #Get the grand total for each column (ie for each cell get the total gene count)
    grandTotal = sample['GenExp'].sum(axis=0)

    out = np.zeros(sample['GenExp'].shape, dtype=np.int_)
    # loop over the cells
    for i in range(raw_data.shape[0]):
        p = raw_data['genesProb'].iloc[i]
        N = grandTotal[i]

        #draw N counts with prob p
        temp = np.random.multinomial(N, p)

        idx = [sample['gene_name'].index(x) for x in raw_data['Genenames'].iloc[i]]
        out[idx, i] = temp

    #sanity check
    assert np.all(out.sum(axis=0) == grandTotal)
    return out


def paramGrid(alpha, beta):
    grid = np.meshgrid(alpha, beta)
    grid = np.array(grid).T.reshape(-1, 2)
    return grid


def app(alpha, beta):
    # _seed = np.int(time.time())
    _seed = 123456
    np.random.seed(_seed)

    # Fetch the data
    dataset_name = 'DEFAULT_98GENES'

    raw_data, gene_expression, eGeneGamma = fetch_data(dataset_name)

    # for each cell find its most likely cell class
    bc = best_class(raw_data)

    # stick it at the end of the dataframe
    raw_data['best_class'] = bc

    # remove cells belonging to the Zero class
    nonZero = raw_data['best_class'] != 'Zero'
    raw_data = raw_data[nonZero]

    # for each cell find the total gene counts and stick that into the dataframe for later use.
    grandTotal = getTotalGeneCounts(raw_data)
    raw_data['totalGeneCounts'] = grandTotal

    # genesProb, _ = getGenesProb(raw_data)
    # raw_data['genesProb'] = genesProb

    sample = draw_gene_expression(raw_data, gene_expression, eGeneGamma, alpha, beta)

    injected = inject(raw_data, sample, alpha*beta)  # put extra gene selected randomly
    sample['GenExp'] = sample['GenExp'] + injected
    sample['GenExp'] = sample['GenExp'].astype(int)  # cast as int
    spots = position_genes(sample)

    fName = 'spots_' + dataset_name + '_' + str(_seed) + '_alpha' + str(alpha) + '_beta' + str(beta) + 'fakeGenes' + '.csv'
    dir_path = os.path.dirname(os.path.realpath(__file__))
    outPath = os.path.join(dir_path, 'Simulated spots', 'grid')
    outFile = os.path.join(outPath, fName)

    # make now the directory
    mkdir_p(outPath)

    pd.DataFrame(spots).to_csv(outFile, header=['name', 'x', 'y'], index=None)
    logger.info('Saved to %s ' % outFile)

    print(spots[-3:, :])
    print('Done!')


if __name__ == "__main__":
    alpha = [0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 1.75, 2.0, 2.25, 2.5, 2.75, 3.0]
    beta = [0.1, 0.3, 0.5, 0.7]
    grid = paramGrid(alpha, beta)
    grid = [[1, 1]]
    for p in grid:
        alpha = p[0]
        beta = p[1]

        # start the app
        app(alpha, beta)







