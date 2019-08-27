DEFAULT = {
    'CellCallMaxIter': 100,
    'CellCallTolerance': 0.02,
    'Inefficiency': 0.2,
    'InsideCellBonus': 2,
    'MisreadDensity': 0.00001,
    'SpotReg': 0.1,
    'nNeighbors': 3,
    'rGene': 20,
    'rSpot': 2,
    'label_image': '../demo_data/CellMap.mat',
    'roi': {"x0": 6150, "x1": 13751, "y0": 12987, "y1": 18457},
    'geneset': '../demo_data/GeneSet.mat',
    'saFile': '../demo_data/spots.csv',  # Spot attributes, contains x,y coordinates for the spots and their gene names
    'tiles_path': './dashboard/data/img',
    'dataset_id': 'default'  # should not have spaces. You can use .replace(" ", "") to strip all whitespaces
}
