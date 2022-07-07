source('./three-ex-function.R')

full_data <- read_csv('./output_files/full_data.csv')

one_twenty_five <- full_data %>% filter(k_value == 125)

analysis <- NULL

for (number in one_twenty_five$z_value) {
  
  data <- calc(number)
  
  table <- table(data$capture_state) %>% as.data.frame() %>% t() %>% as.data.frame() %>%
    mutate(number_considered = number) %>% select(number_considered,everything())
  
  
  analysis <- rbind(analysis,table)
  
  
}

analysis <- analysis %>% filter(V1 != 'END') %>% select(-V1)

colnames(analysis) <- c('NUMBER', 'EVEN', 'ODD')

#Note: We are back to 5 - seems like standard deviations


#####
a <- calc(1276689)

b <- calc(343632835)


nrow(a) == nrow(b)

common_steps_b <- b[which(b$capture_number %in% a$capture_number),]
common_steps_a <- a[which(b$capture_number %in% a$capture_number),]

common_steps_a == common_steps_b

uncommon_steps_b <- b[-which(b$capture_number %in% a$capture_number),]
uncommon_steps_a <- a[-which(b$capture_number %in% a$capture_number),]

#checking the even/odd distributions
table(uncommon_steps_a$capture_state)
table(uncommon_steps_b$capture_state)

#It's within 5 now

par(mfrow=c(1,2))

plot(uncommon_steps_a$capture_iteration,factor(uncommon_steps_a$capture_state,
                                               levels=c('ODD','EVEN')))
plot(uncommon_steps_b$capture_iteration,factor(uncommon_steps_b$capture_state,
                                               levels=c('ODD','EVEN')))

#Even distribution now

#Factorizing

uncommon_steps_a$to_factor <- factor(uncommon_steps_a$capture_state,
                                     levels=c('ODD','EVEN')) %>% as.numeric() 

uncommon_steps_a$to_factor <- ifelse(uncommon_steps_a$to_factor == 2,0,uncommon_steps_a$to_factor)

uncommon_steps_b$to_factor <- factor(uncommon_steps_b$capture_state,
                                     levels=c('ODD','EVEN')) %>% as.numeric()

uncommon_steps_b$to_factor <- ifelse(uncommon_steps_b$to_factor == 2,0,uncommon_steps_b$to_factor)

### Useful visualizations
rpivotTable(data = uncommon_steps_a,
            rows=c('capture_state'),
            cols=c('capture_iteration'),
            vals = c('capture_number'),
            rendererName = 'Line Chart',
            aggregatorName = 'Sum')

rpivotTable(data = uncommon_steps_b,
            rows=c('capture_state'),
            cols=c('capture_iteration'),
            vals = c('capture_number'),
            rendererName = 'Line Chart',
            aggregatorName = 'Sum')
