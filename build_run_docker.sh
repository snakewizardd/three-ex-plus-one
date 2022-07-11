docker build -t rstudio .
docker run -d -p 8787:8787 -v $(pwd):/home/rstudio -e PASSWORD=snakewizardd rstudio .