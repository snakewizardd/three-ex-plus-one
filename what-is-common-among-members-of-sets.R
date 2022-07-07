#Taking any two numbers from a given iteration set

a <- calc(776657469)

b <- calc(801307639)

#They should have the same number of iterations
nrow(a) == nrow(b)

#They also should have common steps in the end as they converge to singularity
common_steps_b <- b[which(b$capture_number %in% a$capture_number),]
common_steps_a <- a[which(b$capture_number %in% a$capture_number),]

common_steps_a == common_steps_b

#They will also have uncommon steps, that indicate their unique paths/frequencies
uncommon_steps_b <- b[-which(b$capture_number %in% a$capture_number),]
uncommon_steps_a <- a[-which(b$capture_number %in% a$capture_number),]

#checking the even/odd distributions
table(uncommon_steps_b$capture_state)
table(uncommon_steps_a$capture_state)

#Plotting the even/odd distributions by iteration
par(mfrow=c(1,2))

plot(uncommon_steps_a$capture_iteration,factor(uncommon_steps_a$capture_state,
                                                  levels=c('ODD','EVEN')))
plot(uncommon_steps_b$capture_iteration,factor(uncommon_steps_b$capture_state,
                                               levels=c('ODD','EVEN')))
#####
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

#
#Conclusion: All members of sets share a common structure in their 
#Even/Odd distributions even before they share a similar path
#They are somehow intertwined even in source....