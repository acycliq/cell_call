import systemData
import cell
import klass
import spot
import utils

import logging


logger = logging.getLogger()
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s:%(levelname)s:%(message)s"
    )


if __name__ == "__main__":
    algo = systemData.algo()

    # make a cell object
    cells = cell.Cell(algo.iss)

    # make a spots object
    spots = spot.Spot(algo.iss)

    # make a klass object
    klasses = klass.Klass(algo.gSet)

    # calc the loglik and populate some of the object's properties
    spots.loglik(cells, algo.iss)

    # make now a genes object
    genes = spots.getGenes()

    p0 = None
    for i in range(algo.iss.CellCallMaxIter):
        # calc the number of copies of each gene in each cell
        cells.geneCount(spots, genes)

        # now you can set expressions and logexpressions (as the mean expression over klass)
        genes.setKlassExpressions(klasses, algo.iss, algo.gSet)

        # cell calling: Assign cells to klasses
        cells.klassAssignment(spots, genes, klasses, algo.iss)

        # spot calling: Assign spots to cells
        spots.cellAssignment(cells, genes, klasses)

        # Update parameter
        genes.updateGamma(cells, spots, klasses, algo.iss)

        converged, delta = isConverged(spots, p0, algo.iss.CellCallTolerance)
        logger.info('Iteration %d, mean prob change %f' % (i, delta))

        # replace p0 with the latest probabilities
        p0 = spots.neighbors['prob']

        if converged:
            print("Success!!")
            break

    print("done")




