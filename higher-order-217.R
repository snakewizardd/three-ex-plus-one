set <- rows %>% filter(k_value %in% '217')

write_csv(set,'./new_output_files/higher-order-set-217.csv')


plot(NULL,xlim=c(0,max(set$k_value)), 
     ylim=c(0,max(set$z_value)),
     main="",xlab="",ylab="",col.axis='blue',
     sub="")
title(main = paste0('The set of 217 Iterations'), 
      sub = '', 
      xlab = paste0('Iteration'), 
      ylab = paste0('Magnitude'))


colors <- c('red','green','blue','purple')


for(i in 1:nrow(set)){
  
  
  data <- calc(as.numeric(set[i,'z_value']))
  
  points(data$capture_number,col =colors[ceiling(runif(1)*4)])
  lines(data$capture_number,col =colors[ceiling(runif(1)*4)])
  
  
}

ordered <- set %>% arrange(-z_value) 

ordered$sep <- NULL

for(iteration in 2:nrow(ordered)){
  
  ordered[iteration,'sep'] <- ordered[iteration,'z_value'] - (ordered[iteration-1,'z_value']) 
  ordered[iteration,'sep']  <- abs(ordered[iteration,'sep'])
}


write_csv(ordered,'./new_output_files/ordered_differences_217-higher-order.csv')
write_csv(ordered %>% arrange(sep),'./new_output_files/ordered_differences_217_ordered-higher-order.csv')
