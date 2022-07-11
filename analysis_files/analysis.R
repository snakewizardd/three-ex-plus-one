#Sourcing the function to calculate the full permutation sets
source('./functions/libraries.R')
source('./functions/three-ex-function.R')
source('./functions/plot_all_members.R')


#Creating a random set of data
random_set <- ceiling(runif(1000)*1000)

#Populating a matrix with our z values
z <- matrix(random_set,nrow=100,ncol=10)

#initializing k matrix to store results
k <- matrix(0,nrow=100,ncol=10)

#Creating z/k index 
index <- which(z[,] != 1)

#Empty set to contain full outputs
full_output <- NULL

#Performing operations on all members of z and storing max values in k
for(index_number in index){
  
  k[index_number] <-  max(calc(z[index_number])$capture_iteration)
  full_output <- rbind(full_output,calc(z[index_number]))
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

#Full data for trends
trend_ids <- rows %>% filter(k_value %in% trends$k_value[1:10])
full_trends_data <- full_output %>% filter(original_number %in% trend_ids$z_value)

###############################################

#Create directory for this experiment
Experiment_ID <- ceiling(runif(1)*100000)
data_path <- paste0('./data_files/','experiment_',Experiment_ID)
image_path <- paste0('./image_files/','experiment_',Experiment_ID)

dir_create(data_path)
dir_create(image_path)


###############################################

write_csv(full_output,paste0(data_path,'/full_output.csv'))
write_csv(rows,paste0(data_path,'/z_and_k_values.csv'))
write_csv(trends,paste0(data_path,'/trend_values.csv'))
write_csv(full_trends_data,paste0(data_path,'/top_10_trend_values_full.csv'))
write_csv(as.data.frame(z),paste0(data_path,'/z_matrix.csv'))
write_csv(as.data.frame(k),paste0(data_path,'/k_matrix.csv'))

###############################################
#Plots

tiff(paste0(image_path,"/top3.tiff"),width = 1000, height = 1000)

par(mfrow=c(1,3))
plot_all_members(as.numeric(trends$k_value[1]),rows)
plot_all_members(as.numeric(trends$k_value[2]),rows)
plot_all_members(as.numeric(trends$k_value[3]),rows)

dev.off()

###############################################
tiff(paste0(image_path,"/top3_zoomed_distribution.tiff"),width = 1000, height = 1000)


par(mfrow=c(1,3))
plot_all_members_black(as.numeric(trends$k_value[1]),rows)
plot_all_members_black(as.numeric(trends$k_value[2]),rows)
plot_all_members_black(as.numeric(trends$k_value[3]),rows)

dev.off()


