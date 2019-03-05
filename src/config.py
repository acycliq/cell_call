import ruamel.yaml
from pathlib import Path
import utils
import numpy
from geneset import GeneSet
import os
import logging

logger = logging.getLogger()
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s:%(levelname)s:%(message)s"
    )



def read(filename, dataset_name):
    config_file = Path(filename)
    yaml = ruamel.yaml.YAML(typ='safe')
    my_path = os.path.abspath(os.path.dirname(__file__))

    @yaml.register_class
    class Array:
        yaml_tag = '!2darray'

        @classmethod
        def from_yaml(cls, constructor, node):
            array = constructor.construct_sequence(node, deep=True)
            return numpy.array(array)

    cf = yaml.load(config_file)

    matStr = cf[dataset_name]['LABEL_IMAGE']
    print("reading CellMap from %s" % matStr)
    # print(os.path.abspath(os.sep))
    # os.path.join(my_path, '..', matStr)
    mat = utils.loadmat(os.path.join(my_path, '..', matStr))
    cf['label_image'] = mat["CellMap"]
    cf['gSet'] = GeneSet(cf)

    return cf