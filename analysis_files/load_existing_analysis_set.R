#Sourcing the function to calculate the full permutation sets
source('./functions/libraries.R')
source('./functions/three-ex-function.R')
source('./functions/plot_all_members.R')


load_experiment <- 'experiment_first-ten-thousand'

Experiment_ID <- load_experiment
data_path <- paste0('./data_files/',Experiment_ID)
image_path <- paste0('./image_files/',Experiment_ID)

full_output <- read_csv(paste0('./data_files/',Experiment_ID,'/full_output.csv'))

rows <- read_csv(paste0('./data_files/',Experiment_ID,'/z_and_k_values.csv'))


#Arranging row-wise output
rows <- rows %>% unique() %>%
  arrange(k_value)

#Analyzing row-output trends
trends <- rows %>% group_by(k_value) %>%
  count() %>% arrange(-n)

#Full data for trends
trend_ids <- rows %>% filter(k_value %in% trends$k_value[1:10])
full_trends_data <- full_output %>% filter(original_number %in% trend_ids$z_value)


tiff(paste0(image_path,"/top3_zoomed_distribution.tiff"),width = 1000, height = 1000)


par(mfrow=c(1,3))
plot_all_members_black(as.numeric(trends$k_value[1]),rows)
plot_all_members_black(as.numeric(trends$k_value[2]),rows)
plot_all_members_black(as.numeric(trends$k_value[3]),rows)

dev.off()
