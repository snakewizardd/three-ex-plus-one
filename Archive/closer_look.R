import <- read_csv('./output_files/combinations_top_trends.csv')

two_seventeen <- import %>% filter(k_value %in% '217') %>%
    mutate(length = nchar(z_value))


analysis <- NULL

for (number in two_seventeen$z_value) {

    data <- calc(number)

    table <- table(data$capture_state) %>% as.data.frame() %>% t() %>% as.data.frame() %>%
    mutate(number_considered = number) %>% select(number_considered,everything())


    analysis <- rbind(analysis,table)


}

analysis <- analysis %>% filter(V1 != 'END') %>% select(-V1)

colnames(analysis) <- c('NUMBER', 'EVEN', 'ODD')

write_csv(analysis, './output_files/analyzing_even_odd_trends_217_iterations.csv')


####

one_ninety_nine <- import %>% filter(k_value %in% '199') %>%
    mutate(length = nchar(z_value))


analysis <- NULL

for (number in one_ninety_nine$z_value) {

    data <- calc(number)

    table <- table(data$capture_state) %>% as.data.frame() %>% t() %>% as.data.frame() %>%
    mutate(number_considered = number) %>% select(number_considered, everything())


    analysis <- rbind(analysis, table)


}

analysis <- analysis %>% filter(V1 != 'END') %>% select(-V1)

colnames(analysis) <- c('NUMBER', 'EVEN', 'ODD')

write_csv(analysis, './output_files/analyzing_even_odd_trends_199_iterations.csv')

####

one_eighty_six <- import %>% filter(k_value %in% '186') %>%
    mutate(length = nchar(z_value))


analysis <- NULL

for (number in one_eighty_six$z_value) {

    data <- calc(number)

    table <- table(data$capture_state) %>% as.data.frame() %>% t() %>% as.data.frame() %>%
    mutate(number_considered = number) %>% select(number_considered, everything())


    analysis <- rbind(analysis, table)


}

analysis <- analysis %>% filter(V1 != 'END') %>% select(-V1)

colnames(analysis) <- c('NUMBER', 'EVEN', 'ODD')

write_csv(analysis, './output_files/analyzing_even_odd_trends_186_iterations.csv')

#####

one_sixty_eight <- import %>% filter(k_value %in% '168') %>%
  mutate(length = nchar(z_value))


analysis <- NULL

for (number in one_sixty_eight$z_value) {
  
  data <- calc(number)
  
  table <- table(data$capture_state) %>% as.data.frame() %>% t() %>% as.data.frame() %>%
    mutate(number_considered = number) %>% select(number_considered,everything())
  
  
  analysis <- rbind(analysis,table)
  
  
}

analysis <- analysis %>% filter(V1 != 'END') %>% select(-V1)

colnames(analysis) <- c('NUMBER', 'EVEN', 'ODD')

write_csv(analysis, './output_files/analyzing_even_odd_trends_168_iterations.csv')

###

two_twelve <- import %>% filter(k_value %in% '212') %>%
  mutate(length = nchar(z_value))


analysis <- NULL

for (number in two_twelve$z_value) {
  
  data <- calc(number)
  
  table <- table(data$capture_state) %>% as.data.frame() %>% t() %>% as.data.frame() %>%
    mutate(number_considered = number) %>% select(number_considered,everything())
  
  
  analysis <- rbind(analysis,table)
  
  
}

analysis <- analysis %>% filter(V1 != 'END') %>% select(-V1)

colnames(analysis) <- c('NUMBER', 'EVEN', 'ODD')


write_csv(analysis, './output_files/analyzing_even_odd_trends_212_iterations.csv')

