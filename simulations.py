import numpy as np
import pandas as pd
import random


df = pd.read_json("https://raw.githubusercontent.com/acycliq/issplus/master/dashboard/data/img/default/json/iss.json")
GeneExp = np.load('.\data_preprocessed\GeneExp.npy')
ctc = np.load('.\data_preprocessed\cell_to_class_map.npy')
ctc = ['PC.Other1' if x == 'PC.CA2' else x for x in ctc]
ctc = ['PC.Other2' if x == 'PC.CA3' else x for x in ctc]


def best_class(df):
    '''
    Returns a list with the names of all the optimal/best classes
    '''
    class_name = df['ClassName']
    prob = df['Prob']
    out = [class_name[n][np.argmax(prob[n])] for n in range(class_name.shape[0])]
    return out


# for each cell find its most likely cell class
bc = best_class(df)

# stick it at the end of the dataframe
df['best_class'] = bc

# remove cells belonging to the Zero class
nonZero = df['best_class'] != 'Zero'
df = df[nonZero]

# cell class (unique and ranked alphabetically)
cell_classes = sorted(set(df['best_class']))
N = len(cell_classes)
out = {'cid': [],
       'Cell_Num': [],
       'X': [],
       'Y': [],
       'class_name': [],
       'col': [],
       'GenExp': np.nan * np.zeros([GeneExp.shape[0], N])
       }
for i in range(N):
    # select a class
    cell_class = cell_classes[i]
    print(cell_class)

    # carve out data only relevant to the selected class
    class_df = df[df['best_class'] == cell_class]

    # randomly select a cell of that specific class
    cid = random.choice(class_df.index)
    temp = class_df.loc[cid]

    # keep the data for that particular cell to a dictionary
    out['cid'].append(cid)
    out['Cell_Num'].append(temp['Cell_Num'])
    out['X'].append(temp['X'])
    out['Y'].append(temp['Y'])
    out['class_name'].append(temp['best_class'])
    mask = [i for i in range(len(ctc)) if ctc[i] == cell_class]
    col = random.choice(mask)
    out['col'].append(col)
    out['GenExp'][:, i] = GeneExp[:, col]


print('done!')





