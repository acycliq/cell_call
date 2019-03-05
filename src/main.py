import cell
import klass
import spot
import utils
import config
import os
import logging

dir_path = os.path.dirname(os.path.realpath(__file__))
CONFIG_FILE = dir_path + '/config.yml'
# yaml = ruamel.yaml.YAML(typ='safe')

logger = logging.getLogger()
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s:%(levelname)s:%(message)s"
    )


if __name__ == "__main__":
    print(CONFIG_FILE)
    ini = config.read(CONFIG_FILE, 'DEFAULT')
    # ini = config.read(CONFIG_FILE, 'fourThreeRight')

    # make a cell object
    cells = cell.Cell(ini)

    # make a spots object
    spots = spot.Spot(ini)

    # make a klass object
    klasses = klass.Klass(ini['gSet'])

    # calc the loglik and populate some of the object's properties
    spots.loglik(cells, ini)

    # make now a genes object
    genes = spots.getGenes()

    # universe
    gSub = ini['gSet'].GeneSubset(genes.names)
    gSub = gSub.ScaleCell(0)

    # now you can set expressions and logexpressions (as the mean expression over klass)
    genes.setKlassExpressions(klasses, ini, gSub)

    p0 = None
    for i in range(ini['CellCallMaxIter']):
        # calc the number of copies of each gene in each cell
        cells.geneCount(spots, genes)

        # cell calling: Assign cells to klasses
        cells.klassAssignment(spots, genes, klasses, ini)

        # spot calling: Assign spots to cells
        spots.cellAssignment(cells, genes, klasses)

        # Update parameter
        genes.updateGamma(cells, spots, klasses, ini)

        converged, delta = utils.isConverged(spots, p0, ini['CellCallTolerance'])
        logger.info('Iteration %d, mean prob change %f' % (i, delta))

        # replace p0 with the latest probabilities
        p0 = spots.neighbors['prob']

        if converged:
            print("Success!!")
            break

    spots.bestNeighbour()
    print("done")




