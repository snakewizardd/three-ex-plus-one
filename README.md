# Collatz Conjecture

You can start by cloning this repository. 

Install Docker and build the docker image. You can use the shell script which will mount your working directory and run the daemonized container.

The advantage to this set up is that it is 100% reproducible and portable.

You can then navigate and explore with me as I continue to try to make sense of the Collatz Conjecture.

# Repo Structure

You will find in this repository some different sections

- Docker and Readme 
  - This is to get anyone introduced and started
- Analysis Files 
  - These are the scripts that are used to generate/analyze data and images
- Data Files
  - I have set up some structure where each 'experiment' or category of data will be properly catalogued here
  - The goal is to make everything transparent, portable, reproducible.
- Image files
  - I hope to produce both lower quality and higher quality images PNG/TIFF'
  - This section adheres to the same file structure as the data files
- Functions
  - The functions that are used throughought the analysis scripts
  - *If you are not using the custom Docker image, you will need to make sure you have the necessary libraries- I usually refer to them all at once in the libraries.R file
- Website
  - I set up a basic website using surge.sh which just converts some markdown into a nice, readable, searchable etc bookdown
  - URL: https://three-ex-plus-one.surge.sh
  
# My Current Approach

I am currently hoping to explore the nature of the sets of numbers that comprise "k'th" iterations

I think its a pretty logical place to start, plus I have some evidence already from the visualizations and some perusing online that there are most certainly notable trends within these sets as it pertains to the even/odd distributions, the max values, and the curved nature of their interlocking plots.

I am hypothesizing this has something to do with a higher-dimensional plane or curved geometry- TBC...