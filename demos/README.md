## Processing scripts for Vitessce demo datasets

Previously, we have developed processing scripts for Vitessce demos in the `vitessce-data` repository. 

However, now we are standardizing the way that we process data stored in common single-cell file formats (.h5ad, .loom, etc.) for the Python package in this repository. Therefore, writing demo dataset processing code in this repository may allow us to iterate more quickly (i.e. a monorepo, which comes with the usual monorepo tradeoffs).

### Setup

Set up the `vitessce-python-dev` environment using the instructions in the repository root README.

### Run

```sh
snakemake -j 1
```