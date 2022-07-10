source('./three-ex-function.R')

full_data <- read_csv('./Archive/output_files/full_data.csv')

set <- full_data %>% filter(k_value %in% '217') %>% unique()

ordered <- set %>% arrange(-z_value) 

ordered$sep <- NULL

for(iteration in 2:nrow(ordered)){
  
  ordered[iteration,'sep'] <- ordered[iteration,'z_value'] - (ordered[iteration-1,'z_value']) 
  ordered[iteration,'sep']  <- abs(ordered[iteration,'sep'])
}


write_csv(ordered,'./new_output_files/ordered_differences_217.csv')
