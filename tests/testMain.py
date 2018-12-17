from unittest import TestCase
import numpy as np
import src.systemData
import src.cell
import src.klass
import src.spot
import src.utils
import src.config as cfg
import logging


class TestSet(TestCase):
    def test_cells(self):
        # make a cell object
        ini = cfg.settings['default']
        algo = src.systemData.algo(ini)

        # make a cell object
        cells = src.cell.Cell(algo.iss)

        # make a spots object
        spots = src.spot.Spot(algo.iss)

        # make a klass object
        klasses = src.klass.Klass(algo.gSet)

        # calc the loglik and populate some of the object's properties
        spots.loglik(cells, algo.iss)

        # make now a genes object
        genes = spots.getGenes()

        # universe
        gSub = algo.gSet.GeneSubset(genes.names)
        gSub = gSub.ScaleCell(0)

        # now you can set expressions and logexpressions (as the mean expression over klass)
        genes.setKlassExpressions(klasses, algo.iss, gSub)

        p0 = None
        for i in range(2):
            # calc the number of copies of each gene in each cell
            cells.geneCount(spots, genes)

            # cell calling: Assign cells to klasses
            cells.klassAssignment(spots, genes, klasses, algo.iss)

            # spot calling: Assign spots to cells
            spots.cellAssignment(cells, genes, klasses)

            # Update parameter
            genes.updateGamma(cells, spots, klasses, algo.iss)

            converged, delta = src.utils.isConverged(spots, p0, algo.iss.CellCallTolerance)
            print('Iteration %d, mean prob change %f' % (i, delta))

            # replace p0 with the latest probabilities
            p0 = spots.neighbors['prob']

        # Check the mean probability change
        self.assertAlmostEqual(delta, 0.7941027935, places=10)

        # Check the probabilities: Sum across rows
        p1 = [51592.077426481825, 1930.6235359075301, 296.9864193894876, 18516.31261822084]
        delta_p = np.max(np.abs(spots.neighbors['prob'].sum(axis=0) - p1))
        self.assertAlmostEqual(delta_p, 0.0, places=10)

        # Check the probabilities: Column-wise sum must be equal to 1.0
        delta_p = np.max(np.abs(spots.neighbors['prob'].sum(axis=1) - 1.0))
        self.assertAlmostEqual(delta_p, 0.0, places=10)

        # The sum of all probabilities should be the same as the number of spots
        self.assertEqual(spots.neighbors['prob'].sum(), spots.nS)

