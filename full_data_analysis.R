#Sourcing the function to calculate the full permutation sets
source('./libraries.R')
source('./functions/three-ex-function.R')

full_data <- read_csv('./data_files/full_data.csv')

rows <- full_data

full_output <- NULL

for(z_value in full_data$z_value){
  
  full_output <- rbind(full_output,calc(z_value))
  
}


#Analyzing row-output trends
trends <- rows %>% group_by(k_value) %>%
  count() %>% arrange(-n)

#Full data for trends
trend_ids <- rows %>% filter(k_value %in% trends$k_value[1:10])
full_trends_data <- full_output %>% filter(original_number %in% trend_ids$z_value)

#Create directory for this experiment
Experiment_ID <- 'large_data_up_to_1B'
data_path <- paste0('./data_files/','experiment_',Experiment_ID)
image_path <- paste0('./image_files/','experiment_',Experiment_ID)

dir_create(data_path)
dir_create(image_path)

write_csv(full_output,paste0(data_path,'/full_output.csv'))
write_csv(rows,paste0(data_path,'/z_and_k_values.csv'))
write_csv(trends,paste0(data_path,'/trend_values.csv'))
write_csv(full_trends_data,paste0(data_path,'/top_10_trend_values_full.csv'))
write_csv(as.data.frame(z),paste0(data_path,'/z_matrix.csv'))
write_csv(as.data.frame(k),paste0(data_path,'/k_matrix.csv'))



