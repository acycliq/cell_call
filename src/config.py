import ruamel.yaml
from pathlib import Path
import src.utils
import numpy
from src.geneset import GeneSet
import logging

logger = logging.getLogger()
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s:%(levelname)s:%(message)s"
    )



def read(filename, dataset_name):
    config_file = Path(filename)
    yaml = ruamel.yaml.YAML(typ='safe')

    @yaml.register_class
    class Array:
        yaml_tag = '!2darray'

        @classmethod
        def from_yaml(cls, constructor, node):
            array = constructor.construct_sequence(node, deep=True)
            return numpy.array(array)

    cf = yaml.load(config_file)

    matStr = cf[dataset_name]['LABEL_IMAGE']
    logger.info("reading CellMap from %s", matStr)
    mat = src.utils.loadmat(matStr)
    cf['label_image'] = mat["CellMap"]
    cf['gSet'] = GeneSet(cf)

    return cf