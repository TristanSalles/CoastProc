#################################################
#  Short docker file to distribute some notebooks
#################################################
ARG FROMIMG_ARG=tristansalles/geos3009:latest
FROM ${FROMIMG_ARG}

# Jovyan user / group

ENV NB_USER jovyan
ENV NB_UID 1000
ENV HOME /home/${NB_USER}

RUN adduser --disabled-password \
    --gecos "Default user" \
    --uid ${NB_UID} \
    ${NB_USER} || true  # dont worry about the error ... keep building

RUN usermod -a -G jovyan jovyan || true

USER root

WORKDIR /home/jovyan


USER jovyan
RUN git clone --single-branch --branch xbeach https://github.com/TristanSalles/CoastProc.git

# change ownership of everything
ENV NB_USER jovyan
RUN chown -R jovyan:jovyan /home/jovyan

USER root
RUN chown -R jovyan:jovyan /home/jovyan/CoastProc
RUN chown -R jovyan:jovyan /home/jovyan/CoastProc/scripts
RUN chown -R jovyan:jovyan /home/jovyan/CoastProc/Notebooks
RUN chown -R jovyan:jovyan /home/jovyan/CoastProc/Notebooks/notebooks
RUN chown -R jovyan:jovyan /home/jovyan/CoastProc/Notebooks/notebooks/DelflandStorm
RUN chown -R jovyan:jovyan /home/jovyan/CoastProc/Notebooks/notebooks/NourishmentCase

USER jovyan
# Non standard as the files come from the packages
##################################################
ARG IMAGENAME_ARG
ARG PROJ_NAME_ARG=CoastProc
ARG NB_PORT_ARG=8888
ARG NB_PASSWD_ARG=""
ARG NB_DIR_ARG=""
ARG START_NB_ARG=""

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

#USER root
#RUN chown -R jovyan:jovyan /home/jovyan/CoastProc/scripts

#USER jovyan
#RUN /home/jovyan/CoastProc/scripts/run-jupyter.sh

CMD jupyter-notebook --ip='0.0.0.0' --no-browser --NotebookApp.token=$NB_PASSWD --NotebookApp.default_url='/tree/'
