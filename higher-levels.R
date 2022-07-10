source('./three-ex-function.R')

xmin=-2
xmax=2
nx=500
x <- seq(xmin, xmax, length.out=nx)

ymin=-3
ymax=3
ny=500
y <- seq(ymin, ymax, length.out=ny)

full_dimensions <- length(x) * length(y)

values <- ceiling(runif(full_dimensions)*1000000000000)

z <- matrix(values, 
            nrow=length(x), 
            ncol=length(y))

k <- matrix(0.0, nrow=length(x), ncol=length(y))

index <- which(z[,] != 1)

for(index_number in index){
  
  k[index_number] <-  max(calc(z[index_number])$capture_iteration)
  
}

rows <- NULL

for(row in 1:dim(z)[1]){
  
  for(col in 1:dim(z)[2]){
    
    rows <- rbind(rows,data.frame(z_value = z[row,col], k_value = k[row,col]))
    
  }
  
}

rows <- rows %>% unique()

write_csv(rows,'./new_output_files/higher-order-numbers.csv')

###

rows <- read_csv('./new_output_files/higher-order-numbers.csv')

trends <- rows %>% group_by(k_value) %>%
  count() %>%
  arrange(-n)

write_csv(trends,'./new_output_files/top_trends_up_to_1_trillion.csv')

pdf("./new_output_files/distribution_higher-order.pdf")
plot(trends)
dev.off()

pdf("./new_output_files/qq-distribution_higher-pdf")
qqplot(trends$k_value,trends$n)
dev.off()



set <- rows %>% filter(k_value %in% '258')

write_csv(set,'./new_output_files/higher-order-set-258.csv')


pdf("./new_output_files/set-258.pdf")

plot(NULL,xlim=c(0,max(set$k_value)), 
     ylim=c(0,max(set$z_value)),
     main="",xlab="",ylab="",col.axis='blue',
     sub="")
title(main = paste0('The set of 258 Iterations'), 
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


write_csv(ordered,'./new_output_files/ordered_differences_258.csv')
write_csv(ordered %>% arrange(sep),'./new_output_files/ordered_differences_258_ordered.csv')
