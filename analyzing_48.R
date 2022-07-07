source('./three-ex-function.R')

full_data <- read_csv('./output_files/full_data.csv')

forty_eight <- full_data %>% filter(k_value == 48)

analysis <- NULL

for (number in forty_eight$z_value) {
  
  data <- calc(number)
  
  table <- table(data$capture_state) %>% as.data.frame() %>% t() %>% as.data.frame() %>%
    mutate(number_considered = number) %>% select(number_considered,everything())
  
  
  analysis <- rbind(analysis,table)
  
  
}

analysis <- analysis %>% filter(V1 != 'END') %>% select(-V1)

colnames(analysis) <- c('NUMBER', 'EVEN', 'ODD')

#Note: What appeared at higher levels to be a 5 range- this range is 7!!!!


#####
a <- calc(1446)

b <- calc(437446656)


nrow(a) == nrow(b)

common_steps_b <- b[which(b$capture_number %in% a$capture_number),]
common_steps_a <- a[which(b$capture_number %in% a$capture_number),]

common_steps_a == common_steps_b

uncommon_steps_b <- b[-which(b$capture_number %in% a$capture_number),]
uncommon_steps_a <- a[-which(b$capture_number %in% a$capture_number),]

#checking the even/odd distributions
table(uncommon_steps_a$capture_state)
table(uncommon_steps_b$capture_state)

#Wow!! The 7s...

par(mfrow=c(1,2))

plot(uncommon_steps_a$capture_iteration,factor(uncommon_steps_a$capture_state,
                                               levels=c('ODD','EVEN')))
plot(uncommon_steps_b$capture_iteration,factor(uncommon_steps_b$capture_state,
                                               levels=c('ODD','EVEN')))

#Unbelievable

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
