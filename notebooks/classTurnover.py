import pandas as pd
import numpy as np
import os

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


def best_class(df):
    '''
    Returns a list with the names of all the optimal/best classes
    '''
    class_name = df['ClassName']
    prob = df['Prob']
    out = [class_name[n][np.argmax(prob[n])] for n in range(class_name.shape[0])]
    return out


dir_path = os.path.dirname(os.path.realpath(__file__))
print(dir_path)

df = pd.read_json(dir_path + '/../dashboard/data/img/default_98genes/json/iss.json')
dfSim = pd.read_json(dir_path + '/../dashboard/data/img/sim_123456_98genes/json/iss.json')
dfSim_beta10 = pd.read_json(dir_path + '/../dashboard/data/img/sim_123456_98genes_beta10_FakeGenes/json/iss.json')
dfSim_beta30 = pd.read_json(dir_path + '/../dashboard/data/img/sim_123456_98genes_beta30_FakeGenes/json/iss.json')

genesProb = best_class(df)
df['top_class'] = genesProb

genesProb = best_class(dfSim)
dfSim['top_class (Sim)'] = genesProb

genesProb10 = best_class(dfSim_beta10)
dfSim_beta10['top_class (Sim, beta10)'] = genesProb10

genesProb30 = best_class(dfSim_beta30)
dfSim_beta30['top_class (Sim, beta30)'] = genesProb30

out = df[['Cell_Num', 'X', 'Y', 'top_class']].join(dfSim[['top_class (Sim)']])
out = out.join(dfSim_beta10[['top_class (Sim, beta10)']])
out = out.join(dfSim_beta30[['top_class (Sim, beta30)']])

out.to_csv('classTurnover.csv', index=False)
print('Done')