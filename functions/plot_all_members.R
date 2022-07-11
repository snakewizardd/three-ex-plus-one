plot_all_members <- function(k_value_input,rows){
  
  set <- rows %>% filter(k_value == k_value_input)
  
  combining <- NULL
  
  for(z_value in set$z_value){
    
    combining <- rbind(combining,calc(z_value))
    
  }
  
  plot(NULL,xlim=c(0,max(combining$capture_iteration)), 
       ylim=c(0,max(combining$capture_number)),
       main="",xlab="",ylab="",col.axis='blue',
       sub="")
  title(main = paste0('The set of ',max(set$k_value),' Iterations'), 
        sub = '', 
        xlab = paste0('Iteration'), 
        ylab = paste0('Magnitude'))
  
  
  colors <- c('red','green','blue','purple')
  
  
  for(i in 1:nrow(set)){
    
    
    data <- calc(as.numeric(set[i,'z_value']))
    
    points(data$capture_number,col =colors[ceiling(runif(1)*4)])
    lines(data$capture_number,col =colors[ceiling(runif(1)*4)])
    
    
  }
  
  
}

plot_all_members_black<- function(k_value_input){
  
  set <- rows %>% filter(k_value %in% k_value_input) %>% slice(1:500)
  
  combining <- NULL
  
  for(z_value in set$z_value){
    
    combining <- rbind(combining,calc(z_value))
    
  }
  
  plot(NULL,xlim=c(0,.5*max(combining$capture_iteration)), 
       ylim=c(0,0.05*max(combining$capture_number)),
       main="",xlab="",ylab="",col.axis='blue',
       sub="")
  title(main = paste0('The set of ',max(set$k_value),' Iterations (n = 500)'), 
        sub = '', 
        xlab = paste0('Iteration'), 
        ylab = paste0('Magnitude'))
  
  
  colors <- c('red','green','blue','purple')
  
  
  for(i in 1:nrow(set)){
    
    
    data <- calc(as.numeric(set[i,'z_value']))
    
    points(data$capture_number,col ='black')
    lines(data$capture_number,col ='black')
    
    
  }
  
  
}
