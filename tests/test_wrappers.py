import unittest
from os.path import join

import zarr
from anndata import read_h5ad
from scipy.io import mmread
import pandas as pd
import numpy as np

from create_test_data import (
    create_test_anndata_file,
    create_test_loom_file,
    create_test_ometiff_file,
    create_test_omezarr_store,
    create_test_snaptools_files,
)

from vitessce import (
    OmeTiffWrapper,
    OmeZarrWrapper,
    AnnDataWrapper,
    LoomWrapper,
    SnapToolsWrapper,
)

class TestWrappers(unittest.TestCase):

    def setUp(self):
        create_test_anndata_file(join('data', 'test.h5ad'))
        create_test_loom_file(join('data', 'test.loom'))
        create_test_ometiff_file(join('data', 'test.ome.tif'))
        create_test_omezarr_store(join('data', 'test.ome.zarr'))
        create_test_snaptools_files(
            join('data', 'test.snap.mtx'),
            join('data', 'test.snap.bins.txt'),
            join('data', 'test.snap.barcodes.txt'),
            join('data', 'test.snap.clusters.csv'),
        )

    def test_ome_tiff(self):
        w = OmeTiffWrapper("data/test.ome.tif", offsets_path="data/offsets.json", name="Test")

        raster_json = w._create_raster_json(
            "http://localhost:8000/raster_img",
            "http://localhost:8000/raster_offsets/offsets.json"
        )

        self.assertEqual(raster_json, {
            'images': [
                {
                    'metadata': {
                        'omeTiffOffsetsUrl': 'http://localhost:8000/raster_offsets/offsets.json'
                    },
                    'name': 'Test',
                    'type': 'ome-tiff',
                    'url': 'http://localhost:8000/raster_img'
                }
            ],
            'schemaVersion': '0.0.2'
        })

        obj_file_defs, obj_routes = w.get_raster(8000, 'A', 0)

        self.assertEqual(obj_file_defs, [
            {
                'fileType': 'raster.json',
                'type': 'raster',
                'url': 'http://localhost:8000/A/0/raster'
            }
        ])
    
    def test_omezarr_store(self):
        z = zarr.open('data/test.ome.zarr')
        w = OmeZarrWrapper(z)

        raster_json = w._create_raster_json(
            "http://localhost:8000/raster_img"
        )
        
        # TODO
        # self.assertEqual(raster_json, {})

        obj_file_defs, obj_routes = w.get_raster(8000, 'A', 0)
        self.assertEqual(obj_file_defs, [
            {
                'fileType': 'raster.json',
                'type': 'raster',
                'url': 'http://localhost:8000/A/0/raster'
            }
        ])
    
    def test_anndata(self):
        adata = read_h5ad(join('data', 'test.h5ad'))
        w = AnnDataWrapper(adata)

        cells_json = w._create_cells_json()
        cell_sets_json = w._create_cell_sets_json()

        obj_file_defs, obj_routes = w.get_cells(8000, 'A', 0)
        self.assertEqual(obj_file_defs, [{'type': 'cells', 'fileType': 'cells.json', 'url': 'http://localhost:8000/A/0/cells'}])

        obj_file_defs, obj_routes = w.get_cell_sets(8000, 'A', 0)
        self.assertEqual(obj_file_defs, [{'type': 'cell-sets', 'fileType': 'cell-sets.json', 'url': 'http://localhost:8000/A/0/cell-sets'}])

    def test_snaptools(self):
        mtx = mmread(join('data', 'test.snap.mtx'))
        barcodes_df = pd.read_csv(join('data', 'test.snap.barcodes.txt'), header=None)
        bins_df = pd.read_csv(join('data', 'test.snap.bins.txt'), header=None)
        clusters_df = pd.read_csv(join('data', 'test.snap.clusters.csv'), index_col=0)

        zarr_filepath = join('data', 'test_out.snap.multivec.zarr')

        w = SnapToolsWrapper(mtx, barcodes_df, bins_df, clusters_df)
        w._create_genomic_multivec_zarr(zarr_filepath)

        z = zarr.open(zarr_filepath, mode='r')

        self.assertEqual(z['chromosomes/1/5000'][0,:].sum(), 17.0)
        self.assertEqual(z['chromosomes/1/10000'][0,:].sum(), 17.0)
        self.assertEqual(z['chromosomes/1/5000'][:,2].sum(), 7.0)
        self.assertEqual(z['chromosomes/2/5000'][:,2].sum(), 4.0)
        