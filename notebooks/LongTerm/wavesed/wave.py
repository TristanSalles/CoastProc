##~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~##
##                                                                                   ##
##  This file forms part of the Badlands surface processes modelling companion.      ##
##                                                                                   ##
##  For full license and copyright information, please refer to the LICENSE.md file  ##
##  located at the project root, or contact the authors.                             ##
##                                                                                   ##
##~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~##
"""
Regional scale model of wave propogation and associated sediment transport. The wave model
is based on Airy wave theory and takes into account wave refraction based on Huygen's principle.
The sediment entrainment is computed from wave shear stress and transport according to both
wave direction and longshore transport. Deposition is dependent of shear stress and diffusion.
The model is intended to quickly simulate the average impact of wave induced sediment transport
at large scale and over geological time period.
"""

import os
import math
import errno
import numpy as np
import pandas as pd

from pylab import cm
from scipy import interpolate
from scipy.ndimage.filters import gaussian_filter

import cmocean as cmo

from matplotlib.path import Path
from collections import OrderedDict
import skimage.measure

# from legacycontour import _cntr as cntr

import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable

import wavesed.ocean as ocean

from random import *

import warnings

warnings.simplefilter(action="ignore", category=FutureWarning)


def runWaveSed(
    bfile=None,
    rfac=2,
    H0=None,
    dir=None,
    perc=None,
    wbase=None,
    slvl=0.0,
    d50=0.0001,
    tsteps=1000,
    dsteps=1000,
    size=None,
    i1=0,
    i2=-1,
    j1=0,
    j2=-1,
):
    """
    Main entry point for wave and sediment model computation for a given
    set of input forcing conditions.

    Parameters
    ----------
    variable : bfile
        Bathymetry file to load.

    variable: rfac
        Requested resolution factor for wave and sediment transport computation.

    variable: H0
        Wave height values along the boundary.

    variable: dir
        Define wave source directions at boundary
        (angle in degrees counterclock wise from horizontal axis)

    variable: perc
        Percentage of each wave scenario activity (in %)

    variable : wbase
        Maximum depth for wave influence (m).

    variable: slvl
        Sea-level position (m).

    variable: d50
        Sediment average diameter (m).

    variable: tsteps
        Maximum number of steps used to perform sediment transport.

    variable: dsteps
        Maximum number of steps used to perform sediment diffusion.

    variable: size
        Size of the figure.

    variable: imin,imax,jmin,jmax
        Extent of the region to plot.

    Return
    ------
    The function returns 3 varaibles:
        - avewH: average wave height combining all wave scenarios.
        - avewS: average wave shear stress combining all wave scenarios.
        - avedz: average thickness of erosion/deposition combining all wave scenarios.
        - waveparams: main variable from wavesed model run.
    """

    # Define initial model
    waveparams = wave(filename=bfile, wavebase=wbase, resfac=rfac, dia=d50)

    # Find area actually in open ocean
    waveparams.findland(slvl)
    print("+ Preparation of model initial setting completed...")

    nbClims = len(H0)
    for s in range(nbClims):

        frac = perc[s] / 100.0

        # Define wave source direction
        source = waveparams.wavesource(dir[s])

        # Compute wave parameters for given condition
        waveparams.cmptwaves(source, h0=H0[s], sigma=1.0)
        print("- Finished wave computation for scenario ", s)

        if size is not None:
            waveparams.plotData(
                data="travel",
                figsize=size,
                tstep=800,
                vmin=0,
                vmax=0,
                fontsize=10,
                imin=i1,
                imax=i2,
                jmin=j1,
                jmax=j2,
            )

        # Compute sediment transport
        waveparams.cmptsed(sigma=1.0, tsteps=tsteps, dsteps=dsteps)
        print("- Finished sediment transport computation for scenario ", s)

        if size is not None:
            waveparams.plotData(
                data="erodep",
                figsize=size,
                vmin=-2.0,
                vmax=2.0,
                fontsize=10,
                stream=0,
                imin=i1,
                imax=i2,
                jmin=j1,
                jmax=j2,
            )

        if s > 0:
            avedz += waveparams.erodep * frac
            avewH += waveparams.wH * frac
            avewS += waveparams.wS * frac
        else:
            avedz = waveparams.erodep * frac
            avewH = waveparams.wH * frac
            avewS = waveparams.wS * frac

    return avewH, avewS, avedz, waveparams


class wave:
    """
    Class for building wave based on linear wave theory.
    """

    def __init__(
        self, filename=None, wavebase=10.0, resfac=1, dia=0.0001, Ce=1.0, Cd=30.0
    ):
        """
        Initialization function.

        Parameters
        ----------
        variable : filename
            Bathymetry file to load.

        variable : wavebase
            Maximum depth for wave influence (m) [Default is 10].

        variable: resfac
            Requested resolution factor for wave and sediment transport computation.

        variable: dia
            Sediment average diameter (m).

        variable: Ce
            Sediment entrainment coefficient [Default is 1.].

        variable: Cd
            Sediment diffusion coefficient [Default is 30.].
        """

        # Gravity [L/T2]
        self.grav = 9.81
        # Sea water density [M/L3]
        self.rhow = 1027
        # Sediment density [M/L3]
        self.rhos = 2650
        # Porosity
        self.poro = 0.4
        # Bottom friction coefficient
        self.fric = 0.032
        # Kinematic viscosity water (20C) [m2/s]
        self.nu = 1.004 * 1.0e-6

        self.dia = dia
        self.Ce = Ce
        self.Cd = Cd

        # Non-dimensional diameter
        self.ds = dia * np.power(
            self.grav * (self.rhos / self.rhow - 1) / (self.nu * self.nu), 1.0 / 3.0
        )

        # Van Rijn formula
        if self.ds <= 4.0:
            self.tau_cr = 0.24 * np.power(self.ds, -1.0)
        elif self.ds <= 10.0:
            self.tau_cr = 0.14 * np.power(self.ds, -0.64)
        elif self.ds <= 20.0:
            self.tau_cr = 0.04 * np.power(self.ds, -0.1)
        elif self.ds <= 150.0:
            self.tau_cr = 0.013 * np.power(self.ds, 0.29)
        else:
            self.tau_cr = 0.045

        # Bed load sediment transport coefficient (Camenen & Larson, 2005)
        # self.Cb = 12./(self.grav*np.sqrt(self.rhow)*(self.rhos-self.rhow))

        self.wavebase = wavebase
        self.resfac = resfac
        if not os.path.isfile(filename):
            raise RuntimeError(
                "The given file cannot be found or the path is incomplete!"
            )

        data = pd.read_csv(
            filename,
            sep=r"\s+",
            engine="c",
            header=None,
            na_filter=False,
            dtype=np.float,
            low_memory=False,
        )

        rectX = data.values[:, 0]
        rectY = data.values[:, 1]
        rectZ = data.values[:, 2]

        minX = rectX.min()
        maxX = rectX.max()
        minY = rectY.min()
        maxY = rectY.max()
        self.dx = rectX[1] - rectX[0]

        self.nx = int(round((maxX - minX) / self.dx + 1))
        self.ny = int(round((maxY - minY) / self.dx + 1))

        self.regX = np.linspace(minX, maxX, self.nx)
        self.regY = np.linspace(minY, maxY, self.ny)
        self.regZ = np.reshape(rectZ, (self.nx, self.ny), order="F")

        self.xi, self.yi = np.meshgrid(self.regX, self.regY)
        self.XY = np.column_stack((rectX, rectY))

        self.sealvl = 0.0
        self.inland = None
        self.depth = None
        self.sear = None
        self.seac = None
        self.landc = None
        self.landr = None
        self.transX = None
        self.transY = None
        self.Hent = None
        self.dz = None
        self.erodep = None
        self.wS = None
        self.wH = None

        if self.resfac <= 1:
            self.sdx = self.dx
            self.resfac = 1
            self.diff = np.zeros(self.regZ.shape)
        else:
            self.sdx = self.dx * self.resfac
            self.snx = int(round((maxX - minX) / self.sdx + 1))
            self.sny = int(round((maxY - minY) / self.sdx + 1))
            self.sregX = np.linspace(minX, maxX, self.snx)
            self.sregY = np.linspace(minY, maxY, self.sny)

            self.sxi, self.syi = np.meshgrid(self.sregX, self.sregY)
            interfunction = interpolate.RectBivariateSpline(
                self.regX, self.regY, self.regZ
            )
            self.sregZ = interfunction(self.sregX, self.sregY)
            self.sXY = np.column_stack((self.sxi.flatten(), self.syi.flatten()))
            self.diff = np.zeros(self.sregZ.shape)

        return

    def wavesource(self, dir=0.0):
        """
        This function defines wave source boundary conditions from input directions.

        Parameters
        ----------

        variable: dir
            Wave direction from input condition.
        """

        if self.resfac == 1:
            src = np.zeros(self.regZ.shape)
        else:
            src = np.zeros(self.sregZ.shape)

        src.fill(-2)
        # East
        if dir == 0:
            src[-1, :] = 0
        # North
        elif dir == 90:
            src[:, -1] = 0
        # West
        elif dir == 180:
            src[0, :] = 0
        # South
        elif dir == 270:
            src[:, 0] = 0
        # North-East
        elif dir > 0 and dir < 90:
            src[-1, -1] = 0
        # North-West
        elif dir > 90 and dir < 180:
            src[0, -1] = 0
        # South-West
        elif dir > 180 and dir < 270:
            src[0, 0] = 0
        # South-East
        elif dir > 270:
            src[-1, 0] = 0

        src[self.landr, self.landc] = -2

        return src

    def compute_shoreline(self, mlen=0.0):
        """
        This function computes the shoreline position for a given sea-level.

        Parameters
        ----------

        variable: mlen
            Minimum island perimeter length to consider.
        """

        # c = cntr.Cntr(self.xi, self.yi, self.regZ.T)
        # contour = c.trace(self.sealvl)

        contour = skimage.measure.find_contours(self.regZ.T, self.sealvl)
        for c in range(len(contour)):
            contour[c] = np.fliplr(contour[c] * self.sdx)

        nseg = len(contour) // 2
        contours, codes = contour[:nseg], contour[nseg:]
        contourList = []
        start = True

        # Loop through each contour
        for c in range(len(contours)):
            tmpts = contours[c]
            closed = False
            if tmpts[0, 0] == tmpts[-1, 0] and tmpts[0, 1] == tmpts[-1, 1]:
                closed = True

            # Remove duplicate points
            # unique = OrderedDict()
            # for p in zip(tmpts[:,0], tmpts[:,1]):
            #     unique.setdefault(p[:2], p)
            pts = tmpts  # np.asarray(unique.values())

            if closed:
                cpts = np.zeros((len(pts) + 1, 2), order="F")
                cpts[0 : len(pts), 0:2] = pts
                cpts[-1, 0:2] = pts[0, 0:2]

                # Get contour length
                arr = cpts
                val = (arr[:-1, :] - arr[1:, :]).ravel()
                dist = val.reshape((arr.shape[0] - 1, 2))
                lgth = np.sum(np.sqrt(np.sum(dist ** 2, axis=1)))
            else:
                lgth = 1.0e8
                cpts = pts

            if len(cpts) > 2 and lgth > mlen:
                contourList.append(cpts)
                if start:
                    contourPts = cpts
                    start = False
                else:
                    contourPts = np.concatenate((contourPts, cpts))

        return contourPts, contourList

    def findland(self, lvl=0.0):
        """
        This function computes the land IDs as well as the lake IDs.

        Parameters
        ----------
        variable: lvl
            Sea-level position.
        """

        self.sealvl = lvl

        # Specify land/sea areas
        if self.resfac == 1:
            tmpZ = self.regZ
            tmpxi = self.xi
            tmpXY = self.XY
        else:
            tmpZ = self.sregZ
            tmpxi = self.sxi
            tmpXY = self.sXY

        self.inland = np.ones(tmpZ.shape)
        self.depth = self.sealvl - tmpZ
        self.sear, self.seac = np.where(self.depth > 0)
        self.inland[self.sear, self.seac] = 0
        self.landr, self.landc = np.where(self.depth <= 0)

        xy, xylist = self.compute_shoreline(0.0)

        # Find lakes and assign IDs as land
        for p in range(len(xylist)):
            if (
                xylist[p][0, 0] == xylist[p][-1, 0]
                and xylist[p][0, 1] == xylist[p][-1, 1]
            ):
                mpath = Path(xylist[p])
                mask_flat = mpath.contains_points(tmpXY)
                ar = mask_flat.reshape(tmpxi.shape).astype(int)
                tc, tr = np.where(np.logical_and(ar.T == 1, tmpZ < self.sealvl))
                self.inland[tc, tr] = 1

        return

    def cmptwaves(self, src=None, h0=0.0, sigma=1.0, shadow=0, shoalC=0.99):
        """
        Waves are transformed from deep to shallow water assuming shore-parallel depth contours. The
        orientation of wave fronts is determine by wave celerity and refraction due to depth variations
        and travel time in the domain is calculated from Huygen's principle.

        Parameters
        ----------
        variable: src
            Position of wave boundary condition.

        variable: h0
            Wave height value along the boundary.

        variable: sigma
            Smoothing coefficient.

        variable: shadow
            Considering shadow effect (1) or no shadow (0) [default is 0].

        variable: shoalC
            Coefficent at attenuation in shoaling region [default is 0.99].
        """

        self.waveC, self.waveL, self.travel, self.waveH = ocean.ocean.airymodel(
            self.sdx, shoalC, h0, self.depth, src, self.inland, shadow
        )

        # Breaking wave height
        Hb = np.zeros(self.waveC.shape)
        # McCowan (1894)
        Hb[self.sear, self.seac] = 0.78 * self.depth[self.sear, self.seac]

        # Wave height [L]
        self.waveH = gaussian_filter(self.waveH, sigma=sigma)
        self.waveH[self.landr, self.landc] = 0.0
        breakr, breakc = np.where(self.waveH > Hb)
        self.waveH[breakr, breakc] = Hb[breakr, breakc]

        # Wave direction [radians]
        travel = np.copy(self.travel)
        travel[travel < 0.0] = self.travel.max() + 10.0
        gradx, grady = np.gradient(travel, edge_order=2)
        self.waveD = np.arctan2(grady, gradx)
        self.waveD = self.waveD % (np.pi * 2)

        # Wave power [ML/T3]
        k = np.pi * 2 / self.waveL
        n = 0.5 * (1.0 + 2.0 * k * self.depth / np.sinh(2.0 * k * self.depth))
        self.waveP = (
            self.rhow * self.grav * self.waveC * n * self.waveH * self.waveH / 8.0
        )

        # Wave period [T]
        self.waveT = np.sqrt(2 * np.pi * self.waveL / self.grav)

        # Wave maximum orbital velocity [L/T]
        self.waveU = np.zeros(self.waveC.shape)
        tmp1 = np.pi * self.waveH[self.sear, self.seac]
        tmp2 = np.sinh(
            2
            * np.pi
            * self.depth[self.sear, self.seac]
            / self.waveL[self.sear, self.seac]
        )
        self.waveU[self.sear, self.seac] = tmp1 / (
            self.waveT[self.sear, self.seac] * tmp2
        )

        # Bathymetric contour angle
        if self.resfac > 1:
            tmpZ = self.sregZ
        else:
            tmpZ = self.regZ
        gradx, grady = np.gradient(tmpZ, edge_order=2)
        cDir = np.arctan2(grady, gradx) + np.pi / 2.0
        cDir = cDir % (np.pi * 2)

        # Incidence of wave direction relative to wave front
        # self.incidence = np.min((2.*np.pi-cDir+self.waveD)%np.pi,(2.*np.pi+cDir-self.waveD)%np.pi)

        # Wave transport direction
        self.transpX = np.cos(self.waveD)
        self.transpY = np.sin(self.waveD)

        # Longshore drift contour
        tr, tc = np.where(abs(self.waveD - cDir) > 0.5 * np.pi)
        cDir[tr, tc] = cDir[tr, tc] + np.pi

        # Sediment transport direction
        tmpr, tmpc = np.where(
            np.logical_and(self.depth > 0.0, self.depth < self.wavebase * 0.5)
        )
        self.transpX[tmpr, tmpc] = np.cos(cDir[tmpr, tmpc])
        self.transpY[tmpr, tmpc] = np.sin(cDir[tmpr, tmpc])
        self.transpX[self.landr, self.landc] = 0.0
        self.transpY[self.landr, self.landc] = 0.0

        # Friction factor (Sleath, 1984)
        fric = np.zeros(self.waveC.shape)
        tmp3 = np.log(self.dia / (15.0 * self.depth[self.sear, self.seac]))
        fric[self.sear, self.seac] = 8.0 / 25.0 * np.power(1 + tmp3, -2)

        # Shear stress (N/m2)
        self.waveS = 0.5 * self.rhow * fric * self.waveU * self.waveU

        # Set land values to 0.
        self.waveL[self.landr, self.landc] = 0.0
        self.waveD[self.landr, self.landc] = 0.0
        self.waveT[self.landr, self.landc] = 0.0
        self.waveP[self.landr, self.landc] = 0.0
        self.waveU[self.landr, self.landc] = 0.0
        self.waveS[self.landr, self.landc] = 0.0

        return

    def cmptsed(self, sigma=1.0, tsteps=500, dsteps=1000):
        """
        Compute wave induced sedimentation (erosion/deposition).

        Parameters
        ----------
        variable: sigma
            Smoothing coefficient.

        variable: tsteps
            Maximum number of steps used to perform sediment transport.

        variable: dsteps
            Maximum number of steps used to perform sediment diffusion.
        """

        # Thickness of entrained sediment [L]
        self.waveS[self.waveS < 1.0e-4] = 0.0
        r, c = np.where(self.waveS > 0.0)
        Hent = np.zeros(self.waveS.shape)
        Hent[r, c] = -self.Ce * np.log(
            np.sqrt(np.power(self.tau_cr / self.waveS[r, c], 2))
        )
        Hent[Hent < 0.0] = 0.0
        r, c = np.where(np.logical_and(Hent > 0.0, Hent > 0.25 * self.depth))
        Hent[r, c] = 0.25 * self.depth[r, c]
        if sigma > 0:
            self.Hent = gaussian_filter(Hent, sigma=sigma)
        else:
            self.Hent = Hent
        self.Hent[self.landr, self.landc] = 0.0

        # Proportion of transport in X,Y direction
        tot = np.abs(self.transpX) + np.abs(self.transpY)
        tr, tc = np.where(tot > 0)
        tX = np.zeros(self.waveS.shape)
        tY = np.zeros(self.waveS.shape)
        tX[tr, tc] = self.transpX[tr, tc] / tot[tr, tc]
        tY[tr, tc] = self.transpY[tr, tc] / tot[tr, tc]

        # Compute sediment transport
        dz, dist = ocean.ocean.transport(tsteps, self.depth, self.Hent, tX, tY)

        # Diffuse marine coefficient
        if self.resfac == 1:
            area = self.dx * self.dx
        else:
            area = self.sdx * self.sdx
        CFL = area * area / (4.0 * self.Cd * area)
        Cdiff = self.Cd / area
        maxth = 0.5

        # Perform wave related sediment diffusion
        elev = -self.depth + dz - self.Hent

        # Compute maximum marine fluxes and maximum timestep to avoid excessive diffusion erosion
        ndz = ocean.ocean.diffusion(elev, dz, Cdiff, maxth, CFL, dsteps)

        # Distribute sediment
        if sigma > 0.0:
            val = gaussian_filter(ndz + dist, sigma=sigma)
            totval = np.sum(val)
            frac = np.sum(ndz + dist) / totval
            val = frac * val
        else:
            val = ndz + dist

        self.dz = val - self.Hent

        r, c = np.where(np.logical_and(self.dz > 0, self.depth < -2.0))
        self.dz[r, c] = 0.0

        if self.resfac == 1:
            self.regZ = self.regZ + self.dz
            self.depth = self.sealvl - self.regZ
            self.erodep = self.dz
            self.wS = self.waveS
            self.wH = self.waveH
        else:
            self.sregZ = self.sregZ + self.dz
            self.depth = self.sealvl - self.sregZ
            self.interpolate()

        return

    def interpolate(self):
        """
        Interpolate dataset to finer resolution. The interpolated dataset are:
            - erosion/deposition
            - wave height
            - wave induced shear stress
        """

        # Erosion depostion values
        fct1 = interpolate.RectBivariateSpline(self.sregX, self.sregY, self.dz)
        self.erodep = fct1(self.regX, self.regY)
        # Update elevation according to erosion deposition values
        self.regZ += self.erodep
        lr, lc = np.where(self.regZ > self.sealvl)
        # Wave height
        fct2 = interpolate.RectBivariateSpline(self.sregX, self.sregY, self.waveH)
        self.wH = fct2(self.regX, self.regY)
        self.wH[lr, lc] = 0.0
        self.wH[self.wH < 0.0] = 0
        # Wave induced shear stress
        fct3 = interpolate.RectBivariateSpline(self.sregX, self.sregY, self.waveS)
        self.wS = fct3(self.regX, self.regY)
        self.wS[lr, lc] = 0.0

        return

    def outputCSV(self, filename=None, seddata=0):
        """
        Output wave parameters in a CSV file.

        Parameters
        ----------
        variable: filename
            Name of the output file.

        variable: seddata
            Flag to output either coarse grid wave and sediment data (seddata=0)
            or fine grid only sediment data (seddata=1).
        """

        if seddata == 0:
            if self.resfac > 1:
                tx = self.sxi
                ty = self.syi
                tz = self.sregZ
            else:
                tx = self.xi
                ty = self.yi
                tz = self.regZ

            df = pd.DataFrame(
                {
                    "X": tx.flatten(),
                    "Y": ty.flatten(),
                    "Z": tz.T.flatten(),
                    "wH": self.waveH.T.flatten(),
                    "wLght": self.waveL.T.flatten(),
                    "wDir": self.waveD.T.flatten(),
                    "wPer": self.waveT.T.flatten(),
                    "wPow": self.waveP.T.flatten(),
                    "uBot": self.waveU.T.flatten(),
                    "Shear": self.waveS.T.flatten(),
                    "ent": self.Hent.T.flatten(),
                    "dz": self.dz.T.flatten(),
                }
            )
            df.to_csv(
                filename,
                columns=[
                    "X",
                    "Y",
                    "Z",
                    "wH",
                    "wLght",
                    "wDir",
                    "wPer",
                    "wPow",
                    "uBot",
                    "Shear",
                    "ent",
                    "dz",
                ],
                sep=",",
                index=False,
            )
        else:
            tx = self.xi
            ty = self.yi
            tz = self.regZ

            df = pd.DataFrame(
                {
                    "X": tx.flatten(),
                    "Y": ty.flatten(),
                    "Z": tz.T.flatten(),
                    "wH": self.wH.T.flatten(),
                    "wS": self.wS.T.flatten(),
                    "erodep": self.erodep.T.flatten(),
                }
            )
            df.to_csv(
                filename,
                columns=["X", "Y", "Z", "wH", "wS", "erodep"],
                sep=",",
                index=False,
            )

        return

    def plotData(
        self,
        data="bathy",
        figsize=(25, 10),
        tstep=10,
        vmin=0,
        vmax=0,
        fontsize=10,
        stream=0,
        imin=0,
        imax=-1,
        jmin=0,
        jmax=-1,
        save=None,
    ):
        """
        Plotting wave parameters.

        Parameters
        ----------
        variable: data
            Name flagging the type of data to plot.

        variable: figsize
            Size of the figure.

        variable: tstep
            Interval in seconds between travel time contour.

        variable: vmin, vmax
            Min/max values for the color bar.

        variable: fontsize
            Label font size.

        variable: stream
            Stream line density for wave or transport directions.

        variable: imin,imax,jmin,jmax
            Extent of the region to plot.

        variable: save
            Name of the png file to save.
        """

        if self.resfac > 1:
            tmpX = self.sregX
            tmpY = self.sregY
            tmpZ = self.sregZ
        else:
            tmpX = self.regX
            tmpY = self.regY
            tmpZ = self.regZ

        fig = plt.figure(figsize=figsize)
        ax1 = plt.gca()

        if data == "bathy":
            if vmin == vmax:
                vmin = (tmpZ.T - self.sealvl).min()
                vmax = -vmin
            ax1.set_title("Bathymetry (m)", fontsize=fontsize)
            im1 = ax1.imshow(
                np.flipud(tmpZ[imin:imax, jmin:jmax].T - self.sealvl),
                interpolation="nearest",
                cmap=cmo.cm.delta,
                vmin=vmin,
                vmax=vmax,
            )

            ax1.contour(
                np.flipud(tmpZ[imin:imax, jmin:jmax].T - self.sealvl),
                0,
                colors="k",
                linewidths=2,
            )

        elif data == "wlength":
            if vmin == vmax:
                vmin = 0
                vmax = self.waveL.max()
            ax1.set_title("Wave length (m)", fontsize=fontsize)
            im1 = ax1.imshow(
                np.flipud(self.waveL[imin:imax, jmin:jmax].T),
                interpolation="nearest",
                cmap=cmo.cm.dense,
                vmin=vmin,
                vmax=vmax,
            )

            ax1.contour(
                np.flipud(tmpZ[imin:imax, jmin:jmax].T - self.sealvl),
                0,
                colors="k",
                linewidths=2,
            )

        elif data == "travel":
            if vmin == vmax:
                vmin = 0
                vmax = self.travel.max()
            ax1.set_title("Wave travel time (s)", fontsize=fontsize)
            im1 = ax1.imshow(
                np.flipud(self.travel[imin:imax, jmin:jmax].T),
                interpolation="nearest",
                cmap=cmo.cm.amp,
                vmin=vmin,
                vmax=vmax,
            )

            levels = np.arange(0, self.travel[imin:imax, jmin:jmax].max(), tstep)
            ax1.contour(
                np.flipud(self.travel[imin:imax, jmin:jmax].T),
                levels,
                colors="k",
                linewidths=0.5,
            )

        elif data == "wcelerity":
            if vmin == vmax:
                vmin = 0
                vmax = self.waveC.max()
            ax1.set_title("Wave celerity (m/s)", fontsize=fontsize)
            im1 = ax1.imshow(
                np.flipud(self.waveC[imin:imax, jmin:jmax].T),
                interpolation="nearest",
                cmap=cmo.cm.tempo,
                vmin=vmin,
                vmax=vmax,
            )

            ax1.contour(
                np.flipud(tmpZ[imin:imax, jmin:jmax].T - self.sealvl),
                0,
                colors="k",
                linewidths=2,
            )

            if stream > 0:

                wDirX = np.cos(self.waveD)
                wDirY = np.sin(self.waveD)
                wDirX[self.landr, self.landc] = 0.0
                wDirY[self.landr, self.landc] = 0.0
                U = wDirX[imin:imax, jmin:jmax]
                V = -wDirY[imin:imax, jmin:jmax]

                sX, sY = np.meshgrid(np.arange(U.shape[0]), np.arange(U.shape[1]))

                ax1.streamplot(
                    sX,
                    sY,
                    np.flipud(U.T),
                    np.flipud(V.T),
                    linewidth=1,
                    density=stream,
                    color="w",
                )

        elif data == "wheight":
            if vmin == vmax:
                vmin = 0
                vmax = self.waveH.max()
            ax1.set_title("Wave height (m)", fontsize=fontsize)
            im1 = ax1.imshow(
                np.flipud(self.waveH[imin:imax, jmin:jmax].T),
                interpolation="nearest",
                cmap=cmo.cm.deep,
                vmin=vmin,
                vmax=vmax,
            )

            ax1.contour(
                np.flipud(tmpZ[imin:imax, jmin:jmax].T - self.sealvl),
                0,
                colors="k",
                linewidths=2,
            )

        elif data == "wpower":
            if vmin == vmax:
                vmin = 0
                vmax = self.waveP.max()
            ax1.set_title("Wave power (kg.m/s3)", fontsize=fontsize)
            im1 = ax1.imshow(
                np.flipud(self.waveP[imin:imax, jmin:jmax].T),
                interpolation="nearest",
                cmap=cmo.cm.matter,
                vmin=vmin,
                vmax=vmax,
            )

            ax1.contour(
                np.flipud(tmpZ[imin:imax, jmin:jmax].T - self.sealvl),
                0,
                colors="k",
                linewidths=2,
            )

        elif data == "ubot":
            if vmin == vmax:
                vmin = 0
                vmax = self.waveU.max()
            ax1.set_title("Wave orbital velocity (m/s)", fontsize=fontsize)
            im1 = ax1.imshow(
                np.flipud(self.waveU[imin:imax, jmin:jmax].T),
                interpolation="nearest",
                cmap=cmo.cm.speed,
                vmin=vmin,
                vmax=vmax,
            )

            ax1.contour(
                np.flipud(tmpZ[imin:imax, jmin:jmax].T - self.sealvl),
                0,
                colors="k",
                linewidths=2,
            )

        elif data == "shear":
            if vmin == vmax:
                vmin = -self.waveS.max()
                vmax = self.waveS.max()
            ax1.set_title("Wave shear stress (N/m2)", fontsize=fontsize)
            im1 = ax1.imshow(
                np.flipud(self.waveS[imin:imax, jmin:jmax].T),
                interpolation="nearest",
                cmap=cmo.cm.balance,
                vmin=vmin,
                vmax=vmax,
            )

            ax1.contour(
                np.flipud(tmpZ[imin:imax, jmin:jmax].T - self.sealvl),
                0,
                colors="k",
                linewidths=2,
            )

        elif data == "ent":
            if vmin == vmax:
                vmin = 0
                vmax = self.Hent.max()
            ax1.set_title("Thickness of entrained sediment (m)", fontsize=fontsize)
            im1 = ax1.imshow(
                np.flipud(self.Hent[imin:imax, jmin:jmax].T),
                interpolation="nearest",
                cmap=cmo.cm.amp,
                vmin=vmin,
                vmax=vmax,
            )

            ax1.contour(
                np.flipud(tmpZ[imin:imax, jmin:jmax].T - self.sealvl),
                0,
                colors="k",
                linewidths=2,
            )

        elif data == "dz":
            if vmin == vmax:
                vmin = self.dz.min()
                vmax = -vmin
            ax1.set_title("Erosion/deposition (m)", fontsize=fontsize)
            im1 = ax1.imshow(
                np.flipud(self.dz[imin:imax, jmin:jmax].T),
                interpolation="nearest",
                cmap=cmo.cm.balance,
                vmin=vmin,
                vmax=vmax,
            )

            ax1.contour(
                np.flipud(tmpZ[imin:imax, jmin:jmax].T - self.sealvl),
                0,
                colors="k",
                linewidths=2,
            )

            if stream > 0:
                U = self.transpX[imin:imax, jmin:jmax]
                V = -self.transpY[imin:imax, jmin:jmax]
                sX, sY = np.meshgrid(np.arange(U.shape[0]), np.arange(U.shape[1]))

                ax1.streamplot(
                    sX,
                    sY,
                    np.flipud(U.T),
                    np.flipud(V.T),
                    linewidth=1,
                    density=stream,
                    color="k",
                )

        elif data == "erodep":
            tmpX = self.regX
            tmpY = self.regY
            tmpZ = self.regZ
            if vmin == vmax:
                vmin = self.erodep.min()
                vmax = -vmin
            ax1.set_title("Erosion/deposition (m)", fontsize=fontsize)
            im1 = ax1.imshow(
                np.flipud(self.erodep[imin:imax, jmin:jmax].T),
                interpolation="nearest",
                cmap=cmo.cm.balance,
                vmin=vmin,
                vmax=vmax,
            )

            ax1.contour(
                np.flipud(tmpZ[imin:imax, jmin:jmax].T - self.sealvl),
                0,
                colors="k",
                linewidths=2,
            )

        elif data == "wH":
            tmpX = self.regX
            tmpY = self.regY
            tmpZ = self.regZ
            if vmin == vmax:
                vmin = 0
                vmax = self.wH.max()
            ax1.set_title("Wave height (m)", fontsize=fontsize)
            im1 = ax1.imshow(
                np.flipud(self.wH[imin:imax, jmin:jmax].T),
                interpolation="nearest",
                cmap=cmo.cm.deep,
                vmin=vmin,
                vmax=vmax,
            )

            ax1.contour(
                np.flipud(tmpZ[imin:imax, jmin:jmax].T - self.sealvl),
                0,
                colors="k",
                linewidths=2,
            )

        elif data == "wS":
            tmpX = self.regX
            tmpY = self.regY
            tmpZ = self.regZ
            if vmin == vmax:
                vmin = -self.wS.max()
                vmax = self.wS.max()
            ax1.set_title("Wave shear stress (N/m2)", fontsize=fontsize)
            im1 = ax1.imshow(
                np.flipud(self.wS[imin:imax, jmin:jmax].T),
                interpolation="nearest",
                cmap=cmo.cm.balance,
                vmin=vmin,
                vmax=vmax,
            )

            ax1.contour(
                np.flipud(tmpZ[imin:imax, jmin:jmax].T - self.sealvl),
                0,
                colors="k",
                linewidths=2,
            )

        elif data == "fbathy":
            tmpX = self.regX
            tmpY = self.regY
            tmpZ = self.regZ
            if vmin == vmax:
                vmin = (tmpZ.T - self.sealvl).min()
                vmax = -vmin
            ax1.set_title("Bathymetry (m)", fontsize=fontsize)
            im1 = ax1.imshow(
                np.flipud(tmpZ[imin:imax, jmin:jmax].T - self.sealvl),
                interpolation="nearest",
                cmap=cmo.cm.delta,
                vmin=vmin,
                vmax=vmax,
            )

            ax1.contour(
                np.flipud(tmpZ[imin:imax, jmin:jmax].T - self.sealvl),
                0,
                colors="k",
                linewidths=2,
            )

        else:
            print("Provided output data name flag is not known! ")
            print("Possible output choice are: ")
            print("   + bathy: coarse bathymetric map")
            print("   + wlength: coarse wave lenght map")
            print("   + travel: coarse wave travel time map")
            print("   + wcelerity: coarse wave celerity map")
            print("   + wheight: coarse wave height map")
            print("   + wpower: coarse wave power map")
            print("   + ubot: coarse wave induced bottom velocity map")
            print("   + shear: coarse wave induced shear stress map")
            print("   + ent: coarse sediment entrainment map")
            print("   + dz: coarse erosion/deposition map")
            print("   + fbathy: fine bathymetric map")
            print("   + erodep: fine erosion/deposition map")
            print("   + wH: fine wave height map")
            print("   + wS: fine wave induced shear stress map")
            plt.close(fig)

            return

        divider1 = make_axes_locatable(ax1)
        cax1 = divider1.append_axes("right", size="5%", pad=0.05)
        cbar1 = plt.colorbar(im1, cax=cax1)

        plt.tight_layout()
        plt.show()
        if save is not None:
            fig.savefig(save, dpi=200, bbox_inches="tight")

        plt.close(fig)

        return
