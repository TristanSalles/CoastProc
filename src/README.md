# CoastProc - _Coastal Processes, Environments & Systems_

## Installation

### Dependencies

You will need **Python 3.5+**.
Also, the following packages are required:

 - [`numpy`](http://numpy.org)
 - [`scipy`](https://scipy.org)
 - [`pandas`](https://pandas.pydata.org/)
 - [`scikit-image`](https://scikit-image.org/)
 - [`seaborn`](https://seaborn.pydata.org)
 - [`geopy`](https://pypi.org/project/geopy/)
 - [`cartopy`](https://scitools.org.uk/cartopy/docs/latest/)
 - [`netCDF4`](https://pypi.org/project/netCDF4/)
 - [`shapely`](https://pypi.org/project/Shapely/)
 - [`pymannkendall`](https://pypi.org/project/pymannkendall/)

### Installing using pip

You can install `CoastProc` using the
[`pip package manager`](https://pypi.org/project/pip/) with your version of Python:

```bash
python3 -m pip install CoastProc
```

### Installing using Docker

A more straightforward installation which does not depend on specific compilers relies on the [docker](http://www.docker.com) virtualisation system.

To install the docker image and test it is working:

```bash
   docker pull tsalles/coastproc:latest
   docker run --rm tsalles/coastproc:latest help
```

To build the dockerfile locally, we provide a script. First ensure you have checked out the source code from github and then run the script in the Docker directory. If you modify the dockerfile and want to push the image to make it publicly available, it will need to be retagged to upload somewhere other than the current repository.

```bash
git checkout https://github.com/TristanSalles/CoastProc.git
cd CoastProc
source Docker/build-dockerfile.sh
```

## Usage

### Binder & docker container

Launch the demonstration at [mybinder.org](https://mybinder.org/v2/gh/TristanSalles/CoastProc/binder?filepath=Notebooks%2F0-StartHere.ipynb)

[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/TristanSalles/CoastProc/binder?filepath=Notebooks%2F0-StartHere.ipynb)

Another option will be to use the Docker container available through Kitematic **tsalles/coastproc**.

[![Docker Cloud Automated build](https://img.shields.io/docker/automated/tsalles/coastproc)](https://hub.docker.com/r/tsalles/coastproc)

### License

This program is free software: you can redistribute it and/or modify it under the terms of the **GNU Lesser General Public License** as published by the **Free Software Foundation**, either version 3 of the License, or (at your option) any later version.

  > This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more details.
  You should have received a copy of the GNU Lesser General Public License along with this program.  If not, see http://www.gnu.org/licenses/lgpl-3.0.en.html.


  1. Young, I. R. and Donelan, M., 2018. On the determination of global ocean wind and wave climate from satellite observations. **Remote Sensing of Environment** 215, 228–241.
