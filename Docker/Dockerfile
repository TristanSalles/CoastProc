#################################################
#  Short docker file to distribute some notebooks
#################################################

ARG FROMIMG_ARG=tristansalles/coastproc-bundle:2021
FROM ${FROMIMG_ARG}

##################################################
# Non standard as the files come from the packages

USER root

RUN apt-get update -qq && \
    DEBIAN_FRONTEND=noninteractive apt-get install -yq --no-install-recommends \
    gettext && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# change ownership of everything
ENV NB_USER jovyan
RUN chown -R jovyan:jovyan /home/jovyan
USER jovyan

# Non standard as the files come from the packages
##################################################


## These are supplied by the build script
## build-dockerfile.sh

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

# (This is not standard - nothing to do here )

## The notebooks (and other files we are serving up)


# Trust all notebooks
RUN find -name \*.ipynb  -print0 | xargs -0 jupyter trust

# expose notebook port server port
EXPOSE $NB_PORT

VOLUME /home/jovyan/$NB_DIR/share

# note we use xvfb which to mimic the X display for lavavu
ENTRYPOINT ["/usr/local/bin/xvfbrun.sh"]

# launch notebook
CMD /home/jovyan/CoastProc/Docker/scripts/run-jupyter.sh
