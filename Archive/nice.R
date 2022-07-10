source('./three-ex-function.R')

full_data <- read_csv('./Archive/output_files/full_data.csv')

data <- full_data %>% filter(k_value == 217) %>% unique()

plot(NULL,xlim=c(0,max(data$k_value)), 
     ylim=c(0,max(data$z_value)),
     main="",xlab="",ylab="",col.axis='blue',
     sub="")

colors <- c('red','blue','green','purple','magenta')

number <- c(data$z_value)

for(number_selected in number){

point_data <- calc(number_selected)

check <- #ifelse(160 %in% point_data$capture_number,'160',
#ifelse(80 %in% point_data$capture_number,'80',
#ifelse(64 %in% point_data$capture_number,'64',
#ifelse(40 %in% point_data$capture_number,'40',
ifelse(16 %in% point_data$capture_number,'16',
'None')
#)
#)
#)
#)

evens_elminated <- ifelse(160 %in% point_data$capture_number,-9,
ifelse(80 %in% point_data$capture_number,-8,
ifelse(64 %in% point_data$capture_number,-6,
ifelse(40 %in% point_data$capture_number,-7,
 ifelse(16 %in% point_data$capture_number,-4,'None')))))

odds_elminated <- ifelse(160 %in% point_data$capture_number,-1,
ifelse(80 %in% point_data$capture_number,-1,
ifelse(64 %in% point_data$capture_number,-1,
ifelse(40 %in% point_data$capture_number,-1,
ifelse(16 %in% point_data$capture_number,0,'None')))))

#print(paste0('Number: ',number_selected))
ifelse(check == 'None',print(paste0(check,' is the factor.')),
       '')
#print(paste0('Evens Eliminated: ',evens_elminated))
#print(paste0('Odds Eliminated: ',odds_elminated))
}

####
even_odd_counts <- point_data %>% group_by(capture_state) %>%
  count() %>%filter(capture_state != 'END')  %>% 
  arrange(capture_state) %>% as.data.frame()

even_count <- even_odd_counts[1,2]
odd_count <- even_odd_counts[2,2]

even_count
odd_count

#####

point_data_even <- calc(number) %>% filter(capture_state == 'EVEN')
point_data_odd <- calc(number) %>% filter(capture_state == 'ODD')

random_color <- colors[counter]

par(mar = c(1,1,1,1))
par(mfrow=c(2,2))


plot(point_data_even$capture_number)
points(point_data_even$capture_number,col = random_color)
lines(point_data_even$capture_number, col =random_color)

random_color <- colors[counter+1]

plot(point_data_odd$capture_number)
points(point_data_odd$capture_number,col = random_color)
lines(point_data_odd$capture_number, col =random_color)

even_odd_counts <- point_data %>% group_by(capture_state) %>%
  count() %>%filter(capture_state != 'END')  %>% 
  arrange(capture_state) %>% as.data.frame()

ratio <- even_odd_counts[1,2] / even_odd_counts [2,2]

random_color <- colors[counter+2]

plot(point_data$capture_number,col=random_color)
lines(point_data$capture_number,col=random_color)

even_count <- even_odd_counts[1,2]
odd_count <- even_odd_counts[2,2]

iteration_start <- 1
path = ifelse(number %% 2 == 0,'EVEN','ODD')
odd_counts_left <- ifelse(path == 'ODD',odd_count - 1)
even_counts_left <- ifelse(path == 'EVEN',even_count - 1)
