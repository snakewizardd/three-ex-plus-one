source('./three-ex-function.R')


repeat_this <- function(){
  #Constructing two matrices
  #1. the matrix to contain all the random values to try
  #2. The matrix to store the results of our operations
  
  #Starting with arbitrary x = 100, y= 100 parameters
  xmin=-2
  xmax=2
  nx=100
  x <- seq(xmin, xmax, length.out=nx)
  
  ymin=-1.5
  ymax=1.5
  ny=100
  y <- seq(ymin, ymax, length.out=ny)
  
  
  #Constructing the random z matrix of test cases
  z <- matrix(ceiling(runif(length(x)*length(y))*1000000000), nrow=length(x), ncol=length(y))
  
  #The capture matrix
  k <- matrix(0.0, nrow=length(x), ncol=length(y))
  
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
  
  #Analyzing the top trends from the 10k observations
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
  
# needed to cancel at 1380 observations
preliminary <- capture_tops %>% group_by(k_value) %>%
  summarize(n = sum(n)) %>% 
  arrange(-n)

write_csv(preliminary,'./output_files/most_common_results_920k_observations.csv')
