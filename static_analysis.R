source('./three-ex-function.R')

#Constructing two matrices
#1. the matrix to contain all the random values to try
#2. The matrix to store the results of our operations

#Starting with arbitrary x = 100, y= 100 parameters
#Can be adjusted******
xmin=-2
xmax=2
nx=1000
x <- seq(xmin, xmax, length.out=nx)

ymin=-1.5
ymax=1.5
ny=900
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

noteworthy <- rows %>% filter(k_value %in% top$k_value)

#####

#Outputting raw data from 10k observations
write_csv(rows,'./output_files/full_data.csv')
write_csv(top,'./output_files/top_trends.csv')
write_csv(noteworthy,'./output_files/combinations_top_trends.csv')


