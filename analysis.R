#Sourcing the function to calculate the full permutation sets
source('./libraries.R')
source('./functions/three-ex-function.R')

#Creating a random set of data
random_set <- ceiling(runif(1000)*10000)

#Populating a matrix with our z values
z <- matrix(random_set,nrow=100,ncol=10)

#initializing k matrix to store results
k <- matrix(0,nrow=100,ncol=10)

#Creating z/k index 
index <- which(z[,] != 1)

#Performing operations on all members of z and storing max values in k
for(index_number in index){
  
  k[index_number] <-  max(calc(z[index_number])$capture_iteration)
  
}


#Intialzing empty set to contain rows-wise output format from the matrix
rows <- NULL

for(row in 1:dim(z)[1]){
  
  for(col in 1:dim(z)[2]){
    
    rows <- rbind(rows,data.frame(z_value = z[row,col], k_value = k[row,col]))
    
  }
  
}

#Arranging row-wise output
rows <- rows %>% unique() %>%
  arrange(k_value)

#Analyzing row-output trends
trends <- rows %>% group_by(k_value) %>%
  count() %>% arrange(-n)


source('./functions/plot_all_members.R')

par(mfrow=c(1,3))
plot_all_members(as.numeric(trends$k_value[1]),rows)
plot_all_members(as.numeric(trends$k_value[2]),rows)
plot_all_members(as.numeric(trends$k_value[3]),rows)




