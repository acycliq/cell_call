import numpy as np
import pandas as pd
import xarray as xr
import random
import time
import os


def fetch_data():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    print(dir_path)
    df = pd.read_json("https://raw.githubusercontent.com/acycliq/issplus/master/dashboard/data/img/default/json/iss.json")
    GeneExp = np.load(dir_path + '/../data_preprocessed/GeneExp.npy')
    genes = [line.rstrip("\n''") for line in open(dir_path + '/../data_preprocessed/genes.csv')]
    ctc = [line.rstrip("\n''") for line in open(dir_path + '/../data_preprocessed/cell_to_class_map.csv')]

    # Rename PC.CA2 to PC.Other1 and PC.CA3 to PC.Other2
    ctc = ['PC.Other1' if x == 'PC.CA2' else x for x in ctc]
    ctc = ['PC.Other2' if x == 'PC.CA3' else x for x in ctc]

    ge = xr.DataArray(GeneExp, coords=[genes, ctc], dims=['Genes', 'Class'])
    return df, ge

def best_class(df):
    '''
    Returns a list with the names of all the optimal/best classes
    '''
    class_name = df['ClassName']
    prob = df['Prob']
    out = [class_name[n][np.argmax(prob[n])] for n in range(class_name.shape[0])]
    return out

def draw_gene_expression(df, ge):
    # cell class (unique and ranked alphabetically)
    best_classes = sorted(set(df['best_class']))
    class_list = ge.Class.values.tolist()
    N = len(best_classes)
    M = ge.shape[0]
    out = {'cid': [],
           'Cell_Num': [],
           'X': [],
           'Y': [],
           'class_name': [],
           'gene_name': ge.Genes.values.tolist(),
           'col': [],
           'GenExp': np.empty([M, N], dtype=np.int32)
           }
    for i in range(N):
        # select a class
        bc = best_classes[i]
        # print(bc)

        # carve out data only relevant to the selected class
        class_df = df[df['best_class'] == bc]

        # randomly select a cell of that specific class
        cid = random.choice(class_df.index)
        temp = class_df.loc[cid]

        # keep the data for that particular cell to a dictionary
        out['cid'].append(cid)
        out['Cell_Num'].append(temp['Cell_Num'])  # This is 1-based, not 0-based
        out['X'].append(temp['X'])
        out['Y'].append(temp['Y'])
        out['class_name'].append(temp['best_class'])
        # start = time.time()
        mask = [i for i in range(len(class_list)) if class_list[i] == bc]
        # print(time.time() - start)
        col = random.choice(mask)
        out['col'].append(col)
        out['GenExp'][:, i] = ge[:, col]

    return out

def thinner(data):
    p = 0.1
    mat = data['GenExp']
    rnd = np.random.binomial(mat, p)
    data['GenExp'] = rnd
    return data

def position_genes(data):
    r = 8.8673
    u = np.random.normal(0, r, data['GenExp'].shape)
    v = np.random.normal(0, r, data['GenExp'].shape)
    _xCoord = (data["X"]+u)*(data['GenExp'] > 0)
    _yCoord = (data["Y"]+v)*(data['GenExp'] > 0)

    xCoord = pd.DataFrame(_xCoord,
                          columns=data['class_name'],
                          index=data['gene_name']
                          )
    yCoord = pd.DataFrame(_yCoord,
                          columns=data['class_name'],
                          index=data['gene_name']
                          )

    return xCoord, yCoord


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


if __name__ == "__main__":
    n = 1000 #sample size
    xCoord = []
    yCoord = []

    # Fetch the data
    raw_data, gene_expression = fetch_data()

    # for each cell find its most likely cell class
    bc = best_class(raw_data)

    # stick it at the end of the dataframe
    raw_data['best_class'] = bc

    # remove cells belonging to the Zero class
    nonZero = raw_data['best_class'] != 'Zero'
    raw_data = raw_data[nonZero]

    spots = np.empty((0, 3))
    start = time.time()
    while spots.shape[0] < n:
        sample = draw_gene_expression(raw_data, gene_expression)

        sample = thinner(sample)

        _xCoord, _yCoord = position_genes(sample)
        _spots = post_process(_xCoord, _yCoord)
        spots = np.append(spots, _spots, axis=0)
        xCoord.append(_xCoord)
        yCoord.append(_yCoord)


    print('Done!')
    print('Collected %d spots in %4.2f secs' % (spots.shape[0], time.time()-start))






