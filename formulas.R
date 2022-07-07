#Load libraries
library(dplyr)
library(jsonlite)
library(ggplot2)
library(esquisse)
library(tidyr)
library(rpivotTable)

#Create function to iterate 3x+1 and kill it when appropriately

#It returns a nice data frame
calc <- function(number){
  
  capture_number <- c()
  capture_iteration <- c()
  capture_state <- c()
  
  counter <- 1
  
  while(number != 1){
    
    state_even <- (number %% 2 ==0)
    capture_number[counter] <- number
    capture_iteration[counter] <- counter  
    capture_state[counter] <- ifelse(state_even,'EVEN','ODD')
    #check even/odd state
    
    number <- ifelse(state_even,
                     (number / 2),
                     (3*number + 1))
    
    counter <- counter + 1
    
  }
  
  output <- data.frame(capture_iteration,capture_state,capture_number)
  
  final_row <- data.frame(capture_iteration = nrow(output) + 1,
                          capture_state = 'END',
                          capture_number = 1)
  
  output_final <- rbind(output,final_row)
  
  return(output_final)
  
}

#Constructing two matrices
#1. the matrix to contain all the random values to try
#2. The matrix to store the results of our operations
xmin=-2
xmax=2
nx=100
x <- seq(xmin, xmax, length.out=nx)

ymin=-1.5
ymax=1.5
ny=100
y <- seq(ymin, ymax, length.out=ny)


z <- matrix(ceiling(runif(length(x)*length(y))*1000000000), nrow=length(x), ncol=length(y))
k <- matrix(0.0, nrow=length(x), ncol=length(y))

####

#Ensuring we are not considering any 1s by accident
index <- which(z[,] != 1)

#Running the matrix-wise operation and outputting to k
for(index_number in index){
      
k[index_number] <-  max(calc(z[index_number])$capture_iteration)
      
}

#Formatting the dataset into readable format

rows <- NULL

for(row in 1:dim(z)[1]){
  
  for(col in 1:dim(z)[2]){
    
    rows <- rbind(rows,data.frame(z_value = z[row,col], k_value = k[row,col]))
    
  }
  
}
  
########

#Analyzing the top trends
top <- rows %>% group_by(k_value) %>%
    count() %>%
  arrange(-n) 

top <- top[1:15,]

noteworthy <- rows %>% filter(k_value %in% top$k_value)

#####

#Running the analysis of top trends 100 times and rbinding

repeat_this <- function(){
  #Constructing two matrices
  #1. the matrix to contain all the random values to try
  #2. The matrix to store the results of our operations
  xmin=-2
  xmax=2
  nx=100
  x <- seq(xmin, xmax, length.out=nx)
  
  ymin=-1.5
  ymax=1.5
  ny=100
  y <- seq(ymin, ymax, length.out=ny)
  
  
  z <- matrix(ceiling(runif(length(x)*length(y))*1000000000), nrow=length(x), ncol=length(y))
  k <- matrix(0.0, nrow=length(x), ncol=length(y))
  
  ####
  
  #Ensuring we are not considering any 1s by accident
  index <- which(z[,] != 1)
  
  #Running the matrix-wise operation and outputting to k
  for(index_number in index){
    
    k[index_number] <-  max(calc(z[index_number])$capture_iteration)
    
  }
  
  #Formatting the dataset into readable format
  
  rows <- NULL
  
  for(row in 1:dim(z)[1]){
    
    for(col in 1:dim(z)[2]){
      
      rows <- rbind(rows,data.frame(z_value = z[row,col], k_value = k[row,col]))
      
    }
    
  }
  
  ########
  
  #Analyzing the top trends
  top <- rows %>% group_by(k_value) %>%
    count() %>%
    arrange(-n) 
  
  top <- top[1:15,]
  
  return(top)
}

capture_tops <- NULL

for(i in 1:100){
  
  capture_tops <- rbind(capture_tops,repeat_this())
  
}
  
  
