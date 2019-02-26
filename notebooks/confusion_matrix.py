import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import gmean


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

    if norm == 'median':
        out = temp.median(axis=0)
    elif norm == 'mean':
        out = temp.mean(axis=0)
    else:
        print('NORM should be either "mean" or "media"')
        out = None

    print(out.sum())
    return out


def confusion_matrix(model_data, sim_data, norm='mean'):
    'get the model class, ie most likely as this is derived from the model'
    _model_class = best_class(model_data)

    df = sim_data[["Cell_Num", "ClassName", "Prob"]]
    df = df.assign(model_class=_model_class)

    all_class_names = sorted(set(flat_list(df.ClassName)))

    'get all the unique model_class names'
    umc = sorted(list(set(_model_class)))

    n = len(umc)
    m = len(all_class_names)
    out = pd.DataFrame(np.zeros((m, n)), columns=umc, index=all_class_names)

    'loop over the class names (those assigned my the model)'
    for c in umc:
        mask = df['model_class'] == c
        temp = df[mask]
        agg = aggregator(temp, all_class_names, norm)
        key = agg.index
        prob = agg.values
        out.loc[key, c] = prob
        print('Finished with %s' % c)

    return out

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


if __name__ == "__main__":

    # VIEWER_PATH = 'https://raw.githubusercontent.com/acycliq/issplus/master/dashboard/data/img/'
    SIM_PATH = 'https://raw.githubusercontent.com/acycliq/spacetx/rectHeatmap/dashboard/data/img/'
    MODEL_DATA = SIM_PATH + '/default_42genes/json/iss.json'
    SIM_DATA = SIM_PATH + '/sim_123456_42genes/json/iss.json'  # Simulation 1
    # SIM_DATA = SIM_PATH + '/sim_123456_42genes_excludedClasses/json/iss.json'  # Simulation 1


    norm = 'median'
    # norm = 'mean'

    use_pool = False

    model_data = pd.read_json(MODEL_DATA)
    sim_data = pd.read_json(SIM_DATA)

    if use_pool:
        model_data = pool(model_data)
        sim_data = pool(sim_data)

    cm = confusion_matrix(model_data, sim_data, norm)
    print(cm.sum(axis=0))
    plot_confusion_matrix(cm, norm)

    unmatched = [x for x in cm.index.values if x not in cm.columns.values]
    if len(unmatched) > 0:
        print('The following cell exist in predicted but not in actual')
        print(unmatched)

    cm.to_json('confusionMatrix.json', orient='split')

    print('Done')