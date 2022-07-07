source('./three-ex-function.R')

full_data <- read_csv('./output_files/full_data.csv')

fifty <- full_data %>% filter(k_value == 50)

analysis <- NULL

for (number in fifty$z_value) {
  
  data <- calc(number)
  
  table <- table(data$capture_state) %>% as.data.frame() %>% t() %>% as.data.frame() %>%
    mutate(number_considered = number) %>% select(number_considered,everything())
  
  
  analysis <- rbind(analysis,table)
  
  
}

analysis <- analysis %>% filter(V1 != 'END') %>% select(-V1)

colnames(analysis) <- c('NUMBER', 'EVEN', 'ODD')