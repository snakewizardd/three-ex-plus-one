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

trends <- rows %>% group_by(k_value) %>%
  count() %>%
  arrange(-n)

plot(trends)
qqplot(trends$k_value,trends$n)

set <- rows %>% filter(k_value %in% '214')


plot(NULL,xlim=c(0,max(set$k_value)), 
     ylim=c(0,max(set$z_value)),
     main="",xlab="",ylab="",col.axis='blue',
     sub="")
title(main = paste0('The set of 214 Iterations'), 
  sub = '', 
  xlab = paste0('Iteration'), 
  ylab = paste0('Magnitude'))
  
  
colors <- c('red','green','blue','purple')


for(i in 1:nrow(set)){
  
  
  data <- calc(set[i,'z_value'])
  
  points(data$capture_number,col =colors[ceiling(runif(1)*4)])
  lines(data$capture_number,col =colors[ceiling(runif(1)*4)])

  
}

