from unittest import TestCase
import src.systemData
import src.cell
import src.klass
import src.spot
import src.utils
import src.config as cfg

class TestSet(TestCase):

    # def test_will_work(self):
    #     pass

    # def will_not_work(self):
    #     pass

# class test_Main(TestCase):
    ini = cfg.settings['default']
    algo = src.systemData.algo(ini)

    def test_cells(self, algo):
        # make a cell object
        cells = src.cell.Cell(algo.iss)
        self.assertEqual(sum([2.]), 2.)

    def test_spots(self, algo):
        # make a spots object
        spots = src.spot.Spot(algo.iss)
        self.assertEqual(sum([2.]), 2.)

    def test_klasses(self, algo):
        # make a klass object
        klasses = src.klass.Klass(algo.gSet)
        self.assertEqual(sum([2.]), 2.)

    def test_loglik(self, algo):
        spots = src.spot.Spot(algo.iss)
        cells = src.cell.Cell(algo.iss)
        # calc the loglik and populate some of the object's properties
        spots.loglik(cells, algo.iss)
        self.assertEqual(sum([2.]), 2.)

    def test_genes(self, algo):
        spots = src.spot.Spot(algo.iss)
        # make now a genes object
        genes = spots.getGenes()
        self.assertEqual(sum([2.]), 2.)

    def test_gSub(self, algo):
        spots = src.spot.Spot(algo.iss)
        genes = spots.getGenes()
        self.assertEqual(sum([2.]), 2.)

        # universe
        gSub = algo.gSet.GeneSubset(genes.names)
        gSub = gSub.ScaleCell(0)
        self.assertEqual(sum([2.]), 2.)


    def test_2(self):
        print('Im in test2')
        self.assertEqual(sum([2.]), 2.)