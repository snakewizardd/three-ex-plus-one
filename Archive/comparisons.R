source('./three-ex-function.R')

a <- calc(1446)

b <- calc(437446656)

####
number_a <- a$capture_number[1]
number_b <- b$capture_number[1]

#They should have the same number of iterations
nrow(a) == nrow(b)

#They also should have common steps in the end as they converge to singularity
common_steps_b <- b[which(b$capture_number %in% a$capture_number),]
common_steps_a <- a[which(b$capture_number %in% a$capture_number),]

common_steps_a == common_steps_b

common_steps <- common_steps_a

#They will also have uncommon steps, that indicate their unique paths/frequencies
uncommon_steps_b <- b[-which(b$capture_number %in% a$capture_number),]
uncommon_steps_a <- a[-which(b$capture_number %in% a$capture_number),]

commonality <- nrow(common_steps) + nrow(uncommon_steps_a) - nrow(common_steps) +1

a_trajectory <- function(){

plot(a$capture_number,main="",xlab="",ylab="",col.axis='blue',
     sub="")
title(main = 'This is a\'s full trajectory', 
      sub = paste0('a: ',number_a), 
      xlab = 'Iteration', ylab = 'Magnitude')
lines(predict(lm(a$capture_number~a$capture_iteration)))
abline(v= commonality,col='purple')
abline(h=uncommon_steps_a[nrow(uncommon_steps_a),'capture_number'],col='purple')
lines(a$capture_number,col='red')

}

uncommon_a_trajectory <- function(){
  
  horizontal <- uncommon_steps_a[nrow(uncommon_steps_a),'capture_iteration']
  
  plot(uncommon_steps_a$capture_number,main="",xlab="",ylab="",col.axis='blue',
       sub="")
  lines(predict(lm(uncommon_steps_a$capture_number~uncommon_steps_a$capture_iteration)))
  title(main = 'These are the uncommon steps that a takes', 
        sub = paste0('a: ',number_a), 
        xlab = 'Iteration', ylab = 'Magnitude')
  abline(v= horizontal,col='purple')
  abline(h=uncommon_steps_a[nrow(uncommon_steps_a),'capture_number'],col='purple')  
  lines(uncommon_steps_a$capture_number,col='red')
  ####
  
}

b_trajectory <- function(){

plot(b$capture_number,main="",xlab="",ylab="",col.axis='blue',
     sub="")
lines(predict(lm(b$capture_number~b$capture_iteration)))
title(main = 'This is b\'s full trajectory', 
      sub = paste0('b: ',number_b), 
      xlab = 'Iteration', ylab = 'Magnitude')
abline(v= commonality,col='purple')
abline(h=uncommon_steps_a[nrow(uncommon_steps_a),'capture_number'],col='purple')
lines(b$capture_number,col='green')


}

uncommon_b_trajectory <- function(){
  
  horizontal <- uncommon_steps_a[nrow(uncommon_steps_a),'capture_iteration']
  
  
  plot(uncommon_steps_b$capture_number,main="",xlab="",ylab="",col.axis='blue',
       sub="")
  lines(predict(lm(uncommon_steps_b$capture_number~uncommon_steps_b$capture_iteration)))
  title(main = 'These are the uncommon steps that b takes', 
        sub = paste0('b: ',number_b), 
        xlab = 'Iteration', ylab = 'Magnitude')
  abline(v= horizontal,col='purple')
  abline(h=uncommon_steps_a[nrow(uncommon_steps_a),'capture_number'],col='purple')  
  lines(uncommon_steps_b$capture_number,col='green')
  ####
  
}

common_steps_trajectory <- function(){

plot(common_steps$capture_number,main="",xlab="",ylab="",col.axis='blue',
     sub="")
lines(predict(lm(common_steps$capture_number~common_steps$capture_iteration)))
title(main = 'These are the common steps that a and b share', 
      sub = paste0('a: ',number_a, " b: ",number_b), 
      xlab = 'Iteration', ylab = 'Magnitude')
abline(v= min(common_steps$capture_number),col='purple')
lines(common_steps$capture_number,col='blue')


}

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
####
####
####
par(mar=c(2,2,2,2))
par(mfrow=c(3,2))

a_trajectory()
b_trajectory()
uncommon_a_trajectory()
uncommon_b_trajectory()
common_steps_trajectory()
all_combined()
