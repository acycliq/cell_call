import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl
import os
import errno
from scipy.stats import gmean
import logging

logger = logging.getLogger()
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s:%(levelname)s:%(message)s"
    )

def best_class(df):
    '''
    Returns a list with the names of all the optimal/best classes
    '''
    class_name = df['ClassName']
    prob = df['Prob']
    out = [class_name[n][np.argmax(prob[n])] for n in range(class_name.shape[0])]
    return out


def flat_list(l):

    # make sure it is list of lists
    my_list = [x if isinstance(x, (list,)) else [x] for x in l]

    # return the flattened list
    out = [item for sublist in my_list for item in sublist]
    return np.array(out)


def plot_confusion_matrix(cm,
                          norm,
                          cmap=plt.cm.Blues):

    title = 'Confusion matrix' + ' (Norm: ' + norm + ')'
    mpl.rcParams['font.family'] = 'sans-serif'
    mpl.rcParams['font.sans-serif'] = 'DejaVu Sans'
    fntSize = 7
    xClasses = cm.columns
    yClasses = cm.index
    plt.imshow(cm, interpolation='nearest', cmap=cmap)
    plt.title(title)
    plt.colorbar()
    xTick_marks = np.arange(len(xClasses))
    yTick_marks = np.arange(len(yClasses))
    plt.xticks(xTick_marks, xClasses, rotation=45, ha='right', fontsize=fntSize-2)
    plt.yticks(yTick_marks, yClasses, fontsize=fntSize)

    # fmt = '.2f'
    # thresh = cm.max() / 2.
    # for i, j in itertools.product(range(cm.shape[0]), range(cm.shape[1])):
    #     plt.text(j, i, format(cm.iloc[i, j], fmt),
    #              horizontalalignment="center",
    #              color="white" if cm.iloc[i, j] > thresh else "black")

    plt.ylabel('Predicted')
    plt.xlabel('True')
    plt.tight_layout()
    plt.savefig('cm_' + norm + '.png')


def aggregator(df, column_names, norm):
    N = df.shape[0]
    temp = pd.DataFrame(np.zeros([N, len(column_names)]), columns=column_names)
    for i, key in enumerate(df.index):
        labels = df.loc[key, 'ClassName']
        prob = df.loc[key, 'Prob']
        temp.loc[i, labels] = prob

    raw_data = temp.copy()
    raw_data.insert(0, 'model_class', df['model_class'].values)

    if norm == 'median':
        out = temp.median(axis=0)
    elif norm == 'mean':
        out = temp.mean(axis=0)
    else:
        print('NORM should be either "mean" or "media"')
        out = None

    print(out.sum())
    return out, raw_data


def stripper(x, n):
    for i in range(n):
        if x.rfind('.') > 0:
            x = x[:x.rfind('.')]
    return x


def confusion_matrix(model_data, sim_data, norm='mean', fold=0):
    'get the model class, ie most likely as this is derived from the model'
    _model_class = best_class(model_data)

    df = sim_data[["Cell_Num", "ClassName", "Prob"]]
    df = df.assign(model_class=_model_class)

    all_class_names = sorted(set(flat_list(df.ClassName)))

    'get all the unique model_class names'
    umc = sorted(list(set(_model_class)))

    'if you fold the names, then remove the last dot separated substring'
    all_class_names = [stripper(x, fold) for x in all_class_names]
    umc = [stripper(x, fold) for x in umc]

    n = len(umc)
    m = len(all_class_names)
    out = pd.DataFrame(np.zeros((m, n)), columns=umc, index=all_class_names)

    'loop over the class names (those assigned my the model)'
    appended_data = []
    for c in umc:
        mask = df['model_class'] == c
        temp = df[mask]
        agg, raw_data = aggregator(temp, all_class_names, norm)

        # store DataFrame in list
        appended_data.append(raw_data)
        key = agg.index
        prob = agg.values
        out.loc[key, c] = prob
        print('Finished with %s' % c)

    # concatenate along the index(axis=0), overwrite raw_data variable
    raw_data = pd.concat(appended_data, axis=0)
    return out, raw_data


def analytics(df):
    d = []  #keep here the elements of the diagonal
    model_classes = df.columns.values
    for c in model_classes:
        if c in df.index:
            # maybe i should append a zero if c not in the index.
            # Now I just ignore this.'
            d.append(df.loc[c, c])

    avg = np.mean(d)
    median = np.median(d)
    return avg, median


def pool(df):
    print('Pooling all Non Neurons together.')
    non_neuron = ['Astro.1',
                 'Astro.2',
                 'Astro.3',
                 'Astro.4',
                 'Astro.5',
                 'Choroid',
                 'Endo',
                 'Eryth.1',
                 'Eryth.2',
                 'Microglia.1',
                 'Microglia.2',
                 'Oligo.1',
                 'Oligo.2',
                 'Oligo.3',
                 'Oligo.4',
                 'Oligo.5',
                 'Vsmc'
                 ]

    class_names = df['ClassName']
    prob = df['Prob']
    out_names = []
    out_prob = []
    for key, name in enumerate(class_names):
        name = ['Non.Neuron' if x in non_neuron else x for x in name]
        temp = pd.DataFrame({'class_name': name, 'prob': prob[key]} )
        temp = temp.groupby('class_name').sum()

        out_names.append(temp.index.tolist())
        out_prob.append(temp['prob'].tolist())

    df['ClassName'] = out_names
    df['Prob'] = out_prob
    return df


def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc: # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else: raise


def makeOutput(SIM_DATA, norm, use_pool):

    root = 'jsonFiles' # All generated files are going to sit within this folder

    if 'beta10' in SIM_DATA:
        level0 = 'beta10'
    elif 'beta30' in SIM_DATA:
        level0 = 'beta30'
    elif '99genes' in SIM_DATA:
        level0 = '99genes'
    elif '98genes' in SIM_DATA:
        level0 = '98genes'
    elif '62genes' in SIM_DATA:
        level0 = '62genes'
    elif '42genes' in SIM_DATA:
        level0 = '42genes'
    else:
        print('ERROR')


    # first check if you exclude some classes
    if '_excludedClasses' in SIM_DATA:
        level1 = 'rangeDomainOn'
    else:
        level1 = 'rangeDomainOff'

    # now check if you are taking mean or median
    if norm not in ['mean', 'median']:
        print('ERROR')
    level2 = norm

    if use_pool:
        level3 = 'nonNeuronsOn'
    else:
        level3 = 'nonNeuronsOff'

    dir_path = os.path.dirname(os.path.realpath(__file__))
    outPath = os.path.join(dir_path, root, level0, level1, level2, level3)

    # make now the directory
    mkdir_p(outPath)

    return outPath


def mutual_information(data):
    prob = data.iloc[:, 1:]
    model_class = data.iloc[:, 0]
    # first find the locations in each row where the max occurs
    mask = np.zeros(prob.shape)

    # loop over the model class=
    predictedNames = prob.columns
    sampleSize = prob.shape[0]
    for i, val in enumerate(model_class):
        # find the index in the predicted
        col_id = predictedNames.tolist().index(val)
        mask[i, col_id] = 1

    marginals = mask.sum(axis=0) / mask.shape[0]
    # contribution = prob.values * mask / marginals
    contribution = np.divide(prob.values * mask, marginals, out=np.zeros_like(prob.values), where=marginals != 0)
    logContribution = np.log2(contribution, where=(contribution != 0))
    mutualInformation = np.sum(logContribution) / sampleSize

    return mutualInformation



def paramGrid(alpha, beta):
    grid = np.meshgrid(alpha, beta)
    grid = np.array(grid).T.reshape(-1, 2)
    return grid


def mk_dir(target):
    if not os.path.exists(target):
        os.makedirs(target)



def app(N):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    PATH = os.path.join(dir_path, '..', 'dashboard/data/img')
    MODEL_DATA = PATH + '/default_98genes/json/iss.json'

    subfolder = 'N' + str(N)
    fName = 'N' + str(N)  + '_iss.json'
    N_DATA = os.path.join(PATH, 'random_genes', 'pool_99', subfolder, fName)


    model_data = pd.read_json(MODEL_DATA)
    sim_data = pd.read_json(N_DATA)

    cm, raw_data = confusion_matrix(model_data, sim_data)
    avg, median = analytics(cm)
    # mi = mutual_information(raw_data)

    root = r'D:\Dimitris\Dropbox\random_genes'
    subfolder = 'N' + str(N)
    fName = 'N' + str(N) + '_cm_raw_data.csv'
    target = os.path.join(root, subfolder, fName)
    mk_dir(os.path.join(root, subfolder))
    raw_data.to_csv(target, index=False)
    logger.info('Saved to %s ' % target)


if __name__ == "__main__":
    N = 5
    while N < 99:
        # start the app
        app(N)
        N = N + 5

    logger.info('Done')

