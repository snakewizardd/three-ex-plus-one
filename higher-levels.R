source('./three-ex-function.R')

xmin=-2
xmax=2
nx=100
x <- seq(xmin, xmax, length.out=nx)

ymin=-3
ymax=3
ny=100
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

all_combined <- function(){
  plot(NULL,xlim=c(0,commonality+nrow(uncommon_steps_a)), 
       ylim=c(0,max(a$capture_number,b$capture_number)),
       main="",xlab="",ylab="",col.axis='blue',
       sub="")
  title(main = paste0('This is the number at which they converge- Iteration: ',
                      commonality,
                      ' Magnitude: ',uncommon_steps_a[nrow(uncommon_steps_a),'capture_number']
  ), 
  sub = '', 
  xlab = paste0('Iteration: ',commonality), 
  ylab = paste0('Magnitude: ',uncommon_steps_a[nrow(uncommon_steps_a),'capture_number']))
  abline(v=commonality,col='purple')
  abline(h=uncommon_steps_a[nrow(uncommon_steps_a),'capture_number'],col='purple')
  points(a$capture_number)
  lines(a$capture_number, col = 'red')
  points(b$capture_number)
  lines(b$capture_number, col='green')
  
  
}

