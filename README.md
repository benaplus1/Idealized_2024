File necessary for reproducing the data and figures in the paper "Forest Breeze - Cold Pool Interactions Drive Convective Organization over Heterogeneous Vegetation

Steps to Reproduce Data and Figures

Benjamin Ascher, Stephen M. Saleeby, Peter J. Marinescu, Susan C. van den Heever
Department of Atmospheric Science, Colorado State University

2 September 2024
1.Download this repository containing files for setting up the simulations, data analysis, and plotting.

2.Download the latest version of the RAMS model from the GitHub repository here: https://github.com/RAMSmodel/RAMS/releases/tag/v6.3.04.

3.Compile RAMS on your machine or supercomputer following the instructions in docs/README-FIRST-RAMS.pdf within the RAMS directory.

4.Make folders for the PASTURE, CONIFOREST (coniferous forest), SUBURB, PASTURE-CONIFOREST, SUBURB-CONIFOREST, and SUBURB-PASTURE simulations.

5.Run RAMSIN.pasture with the RUNTYPE set to MKSFC. Set the output file path for this RAMSIN to the PASTURE folder. This will make a uniform flat domain of pasture land with no ocean.

6.Copy the land surface files from PASTURE to the CONIFOREST, SUBURB, PASTURE-CONIFOREST, SUBURB-CONIFOREST, and SUBURB-PASTURE folders. *It’s okay that we’re copying the land surface files; we’ll modify them in python in the next step!*

7.Run idealized_setup.ipynb, which will modify the surface files to be correct for each simulation. 

8.Now you’ll need to run the model in initial mode for each simulation for 1 minute to generate an initial analysis file. Make sure to switch the RUNTYPE in each RAMSIN file to INITIAL; leaving them on MKSFC will create the default surface file, and you’ll have to go through the previous three steps all over again! Set the duration of the simulation to 1 minute. Make sure you do this for all six RAMSINs.

9.Run Idealized_initpert.ipynb. This will slightly perturb the initial potential temperature field in the lowest 1km of the simulation to break the initial homogeneity. 
Rerun the RAMS model for each simulation (all six of them), now with the RUNTYPE in HISTORY mode. Make sure to change the duration of the simulation to 18 hours.

10.Run the post-processing script available from this page: https://zenodo.org/records/10889772 on the output for all simulations. This interpolates data from the native sigma-z coordinates to Cartesian coordinates (although an unnecessary step here, since the perfectly flat topography means that Cartesian and sigma-z coordinates are identical) and calculates many derived quantities which we’ll use in the subsequent analysis. *Required: Python 3.10 or newer, numpy, scipy, pandas, astropy, xarray*
When asked to provide a namelist file, enter the name of the relevant ppf file in the terminal (ex. ppf_idealizedpaper_up for the UP simulation). Do this for all six simulations.

11.Run idealized_PaperFigs.ipynb. Make sure to change the file paths to be appropriate for your machine. *Required: In addition to all packages from step 10, matplotlib, metpy*

12.Run idealized_combplots_paper.py. When asked whether you want to *plot*, *animate*, or *both*, enter *plot* (without asterisks). Enter the following fields: RainRate, LhFlux, ShFlux, SrfPres, SrfTemp, VaporMix, CloudTop. You will need to change the file paths to be appropriate for your machine.

Done!

