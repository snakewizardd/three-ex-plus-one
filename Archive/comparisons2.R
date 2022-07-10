source('./three-ex-function.R')

full_data <- read_csv('./Archive/output_files/full_data.csv')

a_num <- 898147815
b_num <- 898147791
c_num <- 901347197
d_num <- 929650228

a <- calc(a_num)
b <- calc(b_num)
c <- calc(c_num)
d <- calc(d_num)

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
uncommon_steps_c <- c %>% filter(capture_iteration %in% uncommon_steps_a$capture_iteration)
uncommon_steps_d <- d %>% filter(capture_iteration %in% uncommon_steps_a$capture_iteration)

#checking the even/odd distributions
table(uncommon_steps_b$capture_state)
table(uncommon_steps_a$capture_state)
table(uncommon_steps_c$capture_state)
table(uncommon_steps_d$capture_state)

analysis <- NULL

for (number in c(a_num,b_num,c_num,d_num)) {
  
  data <- calc(number)
  
  table <- table(data$capture_state) %>% as.data.frame() %>% t() %>% as.data.frame() %>%
    mutate(number_considered = number) %>% select(number_considered, everything())
  
  
  analysis <- rbind(analysis, table)
  
  
}

analysis <- analysis %>% filter(V1 != 'END') %>% select(-V1)

colnames(analysis) <- c('NUMBER', 'EVEN', 'ODD')


commonality <- nrow(common_steps) + nrow(uncommon_steps_a) - nrow(common_steps) + 1

a_trajectory <- function(){

plot(a$capture_number,main="",xlab="",ylab="",col.axis='blue',
     sub="",
     xlim=c(0,max(a$capture_iteration)), 
     ylim=c(0,max(a$capture_number,b$capture_number,c$capture_number,d$capture_number)))
title(main = 'All Four Trajectories and the Intersection', 
      sub = '', 
      xlab = 'Iteration', ylab = 'Magnitude')
abline(v= commonality,col='purple')
abline(h=common_steps[1,'capture_number'],col='purple')
lines(a$capture_number,col='red')
points(b$capture_number)
lines(b$capture_number,col='green')
points(c$capture_number)
lines(c$capture_number,col='blue')
points(d$capture_number)
lines(d$capture_number,col='cyan')

}

common_steps_trajectory <- function(){
  
  plot(common_steps$capture_number,main="",xlab="",ylab="",col.axis='blue',
       sub="")
  lines(predict(lm(common_steps$capture_number~common_steps$capture_iteration)))
  title(main = 'These are the common steps that a,b,c,and d share', 
        sub = '', 
        xlab = 'Iteration', ylab = 'Magnitude')
  abline(v= min(common_steps$capture_number),col='purple')
  lines(common_steps$capture_number,col='blue')
  
  
}

par(mfrow=c(1,2))
a_trajectory()
common_steps_trajectory()

