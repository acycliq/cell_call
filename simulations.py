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
    GeneExp = np.load(dir_path + '/data_preprocessed/GeneExp.npy')
    genes = [line.rstrip("\n''") for line in open(dir_path + '/data_preprocessed/mygenes.csv')]
    ctc = [line.rstrip("\n''") for line in open(dir_path + '/data_preprocessed/cell_to_class_map.csv')]

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

def draw_sample(df, ge):
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
           'col': [],
           'GenExp': np.empty([M, N], dtype=np.int32)
           }
    for i in range(N):
        # select a class
        bc = best_classes[i]
        print(bc)

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
        start = time.time()
        mask = [i for i in range(len(class_list)) if class_list[i] == bc]
        print(time.time() - start)
        col = random.choice(mask)
        out['col'].append(col)
        out['GenExp'][:, i] = ge.data[:, col]

    return out

def thinner(data):
    p = 0.1
    mat = data['GenExp']
    # rnd = np.nan * np.ones(mat.shape)
    # nCols,nRows = mat.shape
    # for i in range(nCols):
    #     for j in range(nRows):
    #         n = mat[i, j]
    #         rnd[i, j] = np.random.binomial(n, p, 1)

    # you should be able to run this instead and avoid the loop
    # it need GenExp to be defined as: np.zeros([GeneExp.shape[0], N], dtype=int)
    # check why it not running
    rnd = np.random.binomial(mat, p)
    data['GenExp'] = rnd
    return data

def position_genes(data):
    r = 8.8673
    u = np.random.normal(0, r, data['GenExp'].shape)
    v = np.random.normal(0, r, data['GenExp'].shape)
    xCoord = (data["X"]+u)*(data['GenExp']>0)
    yCoord = (data["Y"]+v)*(data['GenExp']>0)
    print('in position')
    return xCoord, yCoord


if __name__ == "__main__":
    n = 10 #sample size
    xCoord = []
    yCoord = []

    # Fetch the data
    df, ge = fetch_data()

    # for each cell find its most likely cell class
    bc = best_class(df)

    # stick it at the end of the dataframe
    df['best_class'] = bc

    # remove cells belonging to the Zero class
    nonZero = df['best_class'] != 'Zero'
    df = df[nonZero]

    for i in range(3):
        sample = draw_sample(df, ge)

        data = thinner(sample)

        _xCoord, _yCoord = position_genes(data)
        xCoord.append(_xCoord)
        yCoord.append(_yCoord)



    print('done!')





