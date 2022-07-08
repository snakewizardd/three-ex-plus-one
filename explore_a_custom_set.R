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

values <- ceiling(runif(full_dimensions)*10000)

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

plot(rows$z_value,rows$k_value)

rpivotTable(rows)

