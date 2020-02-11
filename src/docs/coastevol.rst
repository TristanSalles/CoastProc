Quantifying coastal changes
=================

The coastal region is the most heavily urbanised land zone in the world and is regarded as a critical resource in view of its recreational, environmental and economic importance.

.. important::
  Yet, ocean coasts are affected by variations in mean sea level, extreme waves, storm surges and river flow through a range of physical processes. Recent intensification in mean wave energy, extreme coastal wave energy and oceanic wind speeds, coupled with rising sea levels, suggest that coastal areas will be exposed to increasing hazards in coming decades. It is therefore critical to observe and quantify changes along coastlines vulnerable to extreme as well as subtle changes in oceanographic forcing.


Sediment transport
-----------

Siliciclastic sand
*****

Calcareous sediment
*****

Nearshore and beach processes
-----------

Wave runup
*****

**Wave runup** refers to the final part of a wave's journey as it travels from offshore onto the beach. It is observable by anyone who goes to the beach and watches the edge of the water *runup* and *rundown* the beach. It is comprised of two components:

* **setup**: the height of the time averaged superelevation of the mean water level above the Still Water Level (**SWL**)
* **swash**: the height of the time varying fluctuation of the instantaneous water level about the setup elevation

Setup, swash and other components of Total Water Level (**TWL**) rise are shown in this handy figure below from `Vitousek et al. (2017) <https://www.nature.com/articles/s41598-017-01362-7>`_.


.. image:: images/runup.jpg
  :scale: 24 %
  :alt: The water-level components that contribute to coastal flooding.
  :align: center


Wave runup can contribute a significant portion of the increase in TWL in coastal storms causing erosion and inundation. For example, `Stockdon et al. (2006) <https://doi.org/10.1016/j.coastaleng.2005.12.005>`_ collated data from numerous experiments, some of which showed wave runup 2% excedence heights in excess of 3 m during some storms.

Given the impact such a large increase in TWL can have on coastlines, there has been much research conducted to try improve our understanding of wave runup processes.

.. note::
  Although there are many processes which can influence wave runup (such as nonlinear wave transformation, wave reflection, three-dimensional effects, porosity, roughness, permeability and groundwater), **many attempts have been made to derive empirical relationships based on easily measurable parameters**.

Typically, empirical wave runup models include:

* :math:`H_{s}`: significant wave height
* :math:`T_{p}`: peak wave length
* :math:`\beta`: beach slope

The **py-wave-runup** (`here <https://github.com/chrisleaman/py-wave-runup>`_) is a Python package that implements different published wave runup empirical models based on :math:`H_{s}`, :math:`T_{p}`, and :math:`\beta`.


.. raw:: html

    <div style="text-align: center; margin-bottom: 2em;">
    <iframe width="100%" height="550" src="https://py-wave-runup.readthedocs.io/en/latest/models.html?rel=0" frameborder="0" allow="accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>
    </div>


Using **py-wave-runup** , we will evaluate the accuracy of the `Stockdon et al. (2006) <https://doi.org/10.1016/j.coastaleng.2005.12.005>`_ runup
model. To do this, we will use the compiled wave runup observations provided by `Power
et al (2018) <https://doi.org/10.1016/j.coastaleng.2018.10.006>`_.

The Stockdon et al (2006) wave runup model comprises of two relationships, one for
dissipative beaches (*i.e.* Iribarren number :math:`\zeta < 0.3`):

.. math::
  R_{2} = 0.043(H_{s}L_{p})^{0.5}

and a seperate relationship for intermediate and reflective beaches (*i.e.* Iribarren number
:math:`\zeta > 0.3`):


.. math::
  R_{2} = 1.1 \left( 0.35 \beta (H_{s}L_{p})^{0.5} + \frac{H_{s}L_{p}(
    0.563 \beta^{2} +0.004)^{0.5}}{2} \right)


Beach profiles
*****

Sandy coastlines typically comprise two key parts: a **beach** and **dune**.

.. note::
  The **beach** is the section of sandy coast that is *mostly above water* (depending upon tide) and actively influenced by *waves*, while **dunes** are elevated mounds/ridges of sand at the *back of the beach*.


The interface between the beach and dune is often *characterised by a distinct change in ground slope* (with the dune having a steeper slope than the beach). Dunes are particularly important along sandy coastlines because they provide a natural barrier to coastal hazards such as storm-induced waves and surge. The capacity of sandy dunes to provide coastal hazard protection depends in large part on their geometry.

.. important::
  The location of the **dune toe** (the transition point between the beach and dune) is a key factor used in coastal erosion models and for assessing coastal vulnerability to hazards (`Sallenger, 2000 <https://journals.flvc.org/jcr/article/view/80902>`_).

Domain experts are generally able to identify the location of the dune toe given a 2D beach profile. However, recent improvements in coastal monitoring technologies (such as optical, Lidar, and satellite remote sensing), have resulted in a significant increase in coastal topographic data, for which analysis by an expert is infeasible. As a result, there has been increased need for reliable and efficient algorithms for extracting important features such as dune toes from these large coastal datasets.

There are many different algorithms currently available for automatically detecting the dune toe on 2D cross-shore beach profiles:

1. **Maximum curvature** (`Stockdon et al., 2007 <https://www.sciencedirect.com/science/article/pii/S0025322706003355?via%3Dihub>`_) - the dune toe is defined as the location of maximum slope change;
2. **Relative relief** (`Wernette et al. 2016 <https://www.sciencedirect.com/science/article/pii/S0169555X16300630?via%3Dihub>`_) - the dune toe is defined based on relative relief (the ratio of local morphology to computational scale);
3. **Perpendicular distance** - the dune toe is defined as the point of maximum perpendicular distance from the straight line drawn between the dune crest and shoreline; and,
4. **Machine learning** (ML) using Random Forest classification.


.. image:: images/pybeach.jpg
  :scale: 24 %
  :alt: Example applications of pybeach.
  :align: center


However, as shown in the figure above using **pybeach** code from `Beuzen <https://github.com/TomasBeuzen/pybeach>`_ the performance of these algorithms in extracting dune toe locations on beach profiles varies significantly.  While experts can generally identify the dune toe on a beach profile, it is difficult to develop an algorithm that can consistently and reliably define the dune toe for the large variety of beach profile shapes encountered in nature.

In such cases, the use of machine learning (ML) can help improving toe detection. It consists in *feeding* the ML algorithm with existing dataset. In **pybeach** three pre-trained ML models are provided:

1. a **barrier-island** model. This model was developed using 1046 pre- and post- “Hur- ricane Ivan” airborne LIDAR profiles from Santa-Rosa Island Florida (this data was collected in 2004);
2. a **wave-embayed** model. This model was developed using 1768 pre- and post- “June 2016 storm” airborne LIDAR profiles from the wave-dominated, embayed southeast Australian coastline (this data was collected in 2016).
3. a **mixed** model. Developed using a combination of the two above datasets.

For each dataset described above, the true location of the dune toe on each indiviudal profile transect was manually identified and quality checked by multiple experts and verified using satelite imagery, digital elevation models and/or in-situ observations where available. This resulted in the best possible data to facilitate the creation of the ML models in **pybeach**.


Coastline evolution
-----------

Analysing shoreline changes
*****

Space-borne observations have been employed in a wide range of change detection applications, including the analysis of meandering river morphodynamics, delineation of wetland footprints and identification of oil spills.

.. note::
  Recently, optical imaging satellites have begun to be used to measure the location of the shoreline, which is regarded by coastal managers, planners, engineers and scientists as a key indicator of how coastlines vary and evolve over time.

Nowadays, it is possible to use image composites from satellites to map the position of the shoreline with a horizontal accuracy of the order of half a pixel (i.e., **15 m** for Landsat images and **5 m** for Sentinel-2 images).  Some studies have even managed to detect  shoreline at a sub-pixel resolution technique in low-energy microtidal beach and reported horizontal accuracies of less than 10 m using Landsat 7, Landsat 8 and Sentinel-2 images.

.. important::
  Satellite remote sensing can provide low-cost long-term shoreline data capable of analysing multi-decadal temporal changes relevant to coastal scientists and engineers at sites where no in-situ field measurements are available.

`CoastSat <https://github.com/kvos/CoastSat>`_ is an example of such open-source package developed at the Water Research Laboratory in Manly that can be used to obtain time-series of shoreline position at any coastline worldwide from 30+ years (and growing) of publicly available satellite imagery.

It enables the non-expert user to extract shorelines from Landsat 5, Landsat 7, Landsat 8 and Sentinel-2 images. The shoreline detection algorithm implemented in **CoastSat** is optimised for sandy beach coastlines. It combines a sub-pixel border segmentation and an image classification component, which refines the segmentation into four distinct categories such that the shoreline detection is specific to the sand/water interface.

.. raw:: html

    <div style="text-align: center; margin-bottom: 2em;">
    <iframe width="100%" height="450" src="https://www.youtube.com/embed/YK_d08BHids?rel=0" frameborder="0" allow="accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>
    </div>

The toolbox has three main functionalities:

1. assisted retrieval from Google Earth Engine of all available satellite images spanning the user-defined region of interest and time period.
2. automated extraction of shorelines from all the selected images using a sub-pixel resolution technique
3. intersection of the 2D shorelines with user-defined shore-normal transects


.. image:: images/coastsat.jpg
  :scale: 20 %
  :alt: Example region of interest within RGB image located at Narrabeen-Collaroy in southeast Australia, Sentinel-2.
  :align: center


Embayed beaches
*****

The curved planform morphology of embayed beaches can be observed at various length-scales at coast- lines, from a few hundred meters to several kilometers (Figure 1). These log spiral-shaped [LeBlond, 1972], crenulate-shaped [Silvester and Ho, 1972], hook-shaped [Rea and Komar, 1975], or zeta-shaped [Zenkovich, 1967] bays occur in the lee of headlands or man-made coastal structures where erosion and/or littoral drift is inhibited in the face of a dominant direction of wave incidence [Yasso, 1965]. A highly concave portion of shoreline forms on the downdrift side of the headland where the coastline is shadowed from the dominant wave direction and subject to waves that diffract around the headland [e.g., Yasso, 1965; LeBlond, 1972; Rea and Komar, 1975; Hsu et al., 2010].


.. image:: images/cove1.jpg
  :scale: 20 %
  :alt: crenulated bay shapes at different scales
  :align: center

Examples of crenulated bay shapes at different scales from `Hurst et al. (2015) <http://onlinelibrary.wiley.com/doi/10.1002/2015JF003704/abstract>`_: *(a) Hathead Bay, Eastern Australia. (b) Flamborough Head and the Holderness Coastline, East Yorkshire, UK. (c) Half Moon Bay, California, USA*.



Embayed beaches tend toward an equilibrium form under a prevailing wave climate. The planform morphology will adjust until gradients in alongshore sediment flux are minimized (net alongshore sediment flux is constant). Alongshore sediment flux will be negligible on an equilibrium coastline when there are no external sediment inputs [Tanner, 1958; LeBlond, 1979; Komar, 1998; Hsu et al., 2010]. Subsequent changes in planform morphology may occur such as beach rotation, driven by changes in wave climate characteristics that alter alongshore [e.g., Turki et al., 2013; Ratliff and Murray, 2014] or cross-shore [e.g., Harley et al., 2011] sediment transport.
One-line models of shoreline evolution can reproduce embayed beach morphology in the lee of a headland or promontory [LeBlond, 1972; Rea and Komar, 1975; Hanson, 1989; Littlewood et al., 2007; Iglesias et al., 2009; Weesakul et al., 2010; Barkwith et al., 2014a, 2014b].

https://agupubs.onlinelibrary.wiley.com/doi/epdf/10.1002/2015JF003704

Regional scale models
*****

Wavesed
