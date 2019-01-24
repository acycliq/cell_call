import numpy as np
import pandas as pd
import xarray as xr
import random


df = pd.read_json("https://raw.githubusercontent.com/acycliq/issplus/master/dashboard/data/img/default/json/iss.json")
GeneExp = np.load('GeneExp.npy')
ctc = np.load('cell_to_class_map.npy')
ctc = ['PC.Other1' if x == 'PC.CA2' else x for x in ctc]
ctc = ['PC.Other2' if x == 'PC.CA3' else x for x in ctc]


def best_class_domain(df):
    '''
    Returns a list with the names of all the optimal/best classes
    '''
    class_name = df['ClassName']
    prob = df['Prob']
    out = [class_name[n][np.argmax(prob[n])] for n in range(class_name.shape[0])]
    return out


def cell_selector(df, selected, best_classes):
    while set(selected) != set(best_classes):
        # select a cell
        cid = random.choice(range(df.shape[0]))

        # Get the most likely class the cell might belong to
        class_names = df['ClassName'][cid]
        prob = df['Prob'][cid]
        class_name = class_names[np.argmax(prob)]

        if class_name not in selected:
            selected.append(class_name)
            print('Appending %s', class_name)
            print('length is ', len(selected))
            cell_selector(df, selected, best_classes)
        else:
            print(class_name, '% has already been selected...Redoing loop')
            cell_selector(df, selected, best_classes)

    return selected


selected = []
bc = best_class_domain(df)
df['best_class'] = bc
nonZero = df['best_class'] != 'Zero'
df = df[nonZero]

my_cells = sorted(set(ctc))
out = dict.fromkeys(['cid', 'Cell', 'X', 'Y', 'class_name'])
out = {'cid': [], 'Cell_Num': [], 'X': [], 'Y': [], 'class_name': [], 'GenExp': np.nan * np.zeros([GeneExp.shape[0], len(my_cells)])}
for i in range(len(my_cells)):
    cell = my_cells[i]
    print(cell)
    temp = df[df['best_class'] == cell]
    cid = random.choice(temp.index)
    out['cid'].append([cid])
    out['Cell_Num'].append([temp.loc[cid]['Cell_Num']])
    out['X'].append([temp.loc[cid]['X']])
    out['Y'].append([temp.loc[cid]['Y']])
    out['class_name'].append([temp.loc[cid]['best_class']])
    mask = [i for i in range(len(ctc)) if ctc[i] == cell]
    col = random.choice(mask)
    out['GenExp'][:, i] = GeneExp[:, col]

# select a cell
cid = random.choice(range(df.shape[0]))

class_name = df['best_class'][cid]
mask = [i for i in range(len(ctc)) if ctc[i] == class_name ]
col = random.choice(mask)
out = GeneExp[:, col]
print('done')







