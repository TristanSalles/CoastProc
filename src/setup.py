"""
Creating PIPY package instruction:

python3 -m pip install --user --upgrade setuptools wheel
python3 setup.py sdist
python3 -m pip install --user --upgrade twine
twine check dist/*
twine upload dist/*
"""

from setuptools import setup, find_packages
from numpy.distutils.core import setup, Extension
from os import path
import io

this_directory = path.abspath(path.dirname(__file__))
with io.open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

if __name__ == "__main__":
    setup(name = 'CoastProc',
          author            = "Tristan Salles",
          author_email      = "tristan.salles@sydney.edu.au",
          url               = "https://github.com/TristanSalles/CoastProc",
          version           = "0.0.3",
          description       = "Coastal Processes, Environments & Systems.",
          long_description  = long_description,
          long_description_content_type='text/markdown',
          packages          = ['CoastProc'],
          install_requires  = [
                        'numpy>=1.15.0',
                        'six>=1.11.0',
                        'setuptools>=38.4.0',
                        'pandas>=0.25',
                        'seaborn>=0.9',
                        'matplotlib>=3.0',
                        'geopy>=1.20',
                        'cartopy>=0.17',
                        'scipy>=1.3',
                        'netCDF4>=1.5.1',
                        'shapely>=1.6.4',
                        'scikit-image>=0.15',
                        'pymannkendall>=0'
                        ],
          python_requires   = '>=3.3',
          package_data      = {'CoastProc': ['Notebooks/notebooks/*ipynb',
                                          'Notebooks/notebooks/*py',
                                          'Notebooks/dataset/*',
                                          'Notebooks/images/*'] },
          include_package_data = True,
          classifiers       = ['Programming Language :: Python :: 3.3',
                               'Programming Language :: Python :: 3.4',
                               'Programming Language :: Python :: 3.5',
                               'Programming Language :: Python :: 3.6']
          )
