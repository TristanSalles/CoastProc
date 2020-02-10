Quantifying coastal changes
=================




Sediment transport
-----------

+ Sediment transport
calcSand


Wave run-up
-----------



Pywaverunup
https://www.nature.com/articles/s41598-017-01362-7


Beach changes
-----------

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

For each dataset described above, the true location of the dune toe on each indiviudal profile transect was manually identified and quality checked by multiple experts and verified using satelitte imagery, digital elevation models and/or in-situ observations where available. This resulted in the best possible data to facilitate the creation of the ML models in pybeach. 


Coastsat
https://reader.elsevier.com/reader/sd/pii/S1364815219300490?token=41ACBEB73BC02D030EEA29A1B77DCD96E82C4344932A192C000701A6A5D9CFCF522FA81F1D2690593FEF4D124665119B

cove
https://agupubs.onlinelibrary.wiley.com/doi/epdf/10.1002/2015JF003704

Wavesed
