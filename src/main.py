import systemData
import cell
import klass
import spot

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

    # calc the loglik and populate some of the object's properties
    spots.loglik(cells, algo.iss)

    # make now a genes object
    genes = spots.getGenes()

    # calc the number of copies of each gene in each cell
    cells.geneCount(spots, genes)

    # make a klass object
    klasses = klass.Klass(algo.gSet)

    # now you can set expressions and logexpressions (as the mean expession over klass)
    genes.setKlassExpressions(klasses, algo.iss, algo.gSet)

    # algo.callCells(spots, cells, genes, klasses)

    # cell calling: Assign cells to klasses
    cells.klassAssignment(spots, genes, klasses, algo.iss)

    # spot calling: Assign spots to cells
    spots.cellAssignment(cells, genes, klasses)

    # Update parameter
    genes.updateGamma(cells, spots, klasses, algo.iss)



    print("done")