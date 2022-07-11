docker build -t rstudio .
docker run --rm  --name rstudio_container\
  -p 127.0.0.1:8787:8787 \
  -v $(pwd):/home/rstudio \
  -e DISABLE_AUTH=true \
  rocker/rstudio