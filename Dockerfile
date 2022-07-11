FROM rocker/rstudio:latest

RUN apt-get update && apt-get install -y \
    sudo \
    pandoc \
    pandoc-citeproc \
    libcurl4-gnutls-dev \
    libcairo2-dev \
    libxt-dev \
    libssl-dev \
    libssh2-1-dev \
    default-jdk \ 
    r-cran-rjava \
    libgdal-dev \
    libproj-dev \
    software-properties-common \
    curl

RUN R -e "install.packages('dplyr', repos ='http://cran.rstudio.com/')"
RUN R -e "install.packages('jsonlite', repos ='http://cran.rstudio.com/')"
RUN R -e "install.packages('ggplot2', repos ='http://cran.rstudio.com/')"
RUN R -e "install.packages('esquisse', repos ='http://cran.rstudio.com/')"
RUN R -e "install.packages('tidyr', repos ='http://cran.rstudio.com/')"
RUN R -e "install.packages('rpivotTable', repos ='http://cran.rstudio.com/')"
RUN R -e "install.packages('readr', repos ='http://cran.rstudio.com/')"
RUN R -e "install.packages('tidyjson', repos ='http://cran.rstudio.com/')"
RUN R -e "install.packages('fs', repos ='http://cran.rstudio.com/')"

