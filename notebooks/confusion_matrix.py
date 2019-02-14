import numpy as np
import pandas as pd
import itertools
import matplotlib.pyplot as plt


VIEWER_PATH = 'https://raw.githubusercontent.com/acycliq/issplus/master/dashboard/data/img/'
SIM_PATH = 'https://raw.githubusercontent.com/acycliq/spacetx/master/dashboard/data/img/'
MODEL_DATA = VIEWER_PATH + '/default/json/iss.json'
SIM_DATA = SIM_PATH + '/sim_123456/json/iss.json'  # Simulation 1


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


if __name__ == "__main__":
    model_data = pd.read_json(MODEL_DATA)
    sim_data = pd.read_json(SIM_DATA)
    norm = 'median'
    # norm = 'mean'

    cm = confusion_matrix(model_data, sim_data, norm)
    print(cm.sum(axis=0))
    plot_confusion_matrix(cm, norm)

    print('Done')