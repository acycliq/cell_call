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


def plot_confusion_matrix(cm, classes,
                          normalize=False,
                          title='Confusion matrix',
                          cmap=plt.cm.Blues):
    """
    This function prints and plots the confusion matrix.
    Normalization can be applied by setting `normalize=True`.
    """
    if normalize:
        cm = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]
        print("Normalized confusion matrix")
    else:
        print('Confusion matrix, without normalization')

    print(cm)

    plt.imshow(cm, interpolation='nearest', cmap=cmap)
    plt.title(title)
    plt.colorbar()
    tick_marks = np.arange(len(classes))
    plt.xticks(tick_marks, classes, rotation=45)
    plt.yticks(tick_marks, classes)

    fmt = '.2f' if normalize else 'd'
    thresh = cm.max() / 2.
    for i, j in itertools.product(range(cm.shape[0]), range(cm.shape[1])):
        plt.text(j, i, format(cm[i, j], fmt),
                 horizontalalignment="center",
                 color="white" if cm[i, j] > thresh else "black")

    plt.ylabel('True label')
    plt.xlabel('Predicted label')
    plt.tight_layout()


def helper(df):
    N = df.shape[0]
    labels = sorted(set(flat_list(df.ClassName.tolist())))
    out = pd.DataFrame(np.zeros([N, len(labels)]), columns=labels)

    return out


def confusion_matrix(model_data, sim_data):
    'get the model class, ie most likely as this is derived from the model'
    _model_class = best_class(model_data)

    df = sim_data[["Cell_Num", "ClassName", "Prob"]]
    df = df.assign(model_class=_model_class)
    # df.loc[:, 'model_class'] = _model_class

    all_class_names = sorted(set(flat_list(df.ClassName)))

    'get all the unique model_class names'
    umc = sorted(list(set(_model_class)))

    N = len(umc)
    M = len(all_class_names)
    out = pd.DataFrame(np.zeros((M, N)), columns=umc, index=all_class_names)

    'loop over the class names (those assigned my the model)'
    for c in umc:
        mask = df['model_class'] == c
        temp = df[mask]
        testMe = helper(temp)
        class_name = flat_list(temp['ClassName'].values)
        prob = flat_list(temp['Prob'].values)

        x = pd.DataFrame({'class_name': class_name, 'Prob': prob})

        res = x.groupby(['class_name']).sum()
        val = [x[0] for x in res.values]
        out.loc[res.index, c] = val

        print('Finished with %s' % c)

    return out


if __name__ == "__main__":
    model_data = pd.read_json(MODEL_DATA)
    sim_data = pd.read_json(SIM_DATA)

    cm = confusion_matrix(model_data, sim_data)

    print('Done')