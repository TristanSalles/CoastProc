#################################################
#  Short docker file to distribute some notebooks
#################################################
ARG FROMIMG_ARG=tristansalles/coastproc:2021-1
FROM ${FROMIMG_ARG}

RUN python3 -m pip install --no-cache-dir cftime==1.0.4.2 netcdf4==1.4.3

##################################################
# Non standard as the files come from the packages

# change ownership of everything
USER jovyan

# Non standard as the files come from the packages
##################################################
ARG IMAGENAME_ARG
ARG PROJ_NAME_ARG=CoastProc
ARG NB_PORT_ARG=8888
ARG NB_PASSWD_ARG=""
ARG NB_DIR_ARG="Notebooks"
ARG START_NB_ARG="0-StartHere.ipynb"

# The args need to go into the environment so they
# can be picked up by commands/templates (defined previously)
# when the container runs
ENV IMAGENAME=$IMAGENAME_ARG
ENV PROJ_NAME=$PROJ_NAME_ARG
ENV NB_PORT=$NB_PORT_ARG
ENV NB_PASSWD=$NB_PASSWD_ARG
ENV NB_DIR=$NB_DIR_ARG
ENV START_NB=$START_NB_ARG

## NOW INSTALL NOTEBOOKS
# Trust all notebooks
RUN find -name \*.ipynb  -print0 | xargs -0 jupyter trust

# expose notebook port server port
EXPOSE $NB_PORT

# note we use xvfb which to mimic the X display for lavavu
ENTRYPOINT ["/usr/local/bin/xvfbrun.sh"]

# launch notebook
CMD /home/jovyan/CoastProc/Docker/scripts/run-jupyter.sh
