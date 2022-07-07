source('./libraries.R')

#Create function to iterate 3x+1 and kill it when appropriately

#It returns a nice data frame
calc <- function(number){
  
  capture_number <- c()
  capture_iteration <- c()
  capture_state <- c()
  
  counter <- 1
  
  while(number != 1){
    
    state_even <- (number %% 2 ==0)
    capture_number[counter] <- number
    capture_iteration[counter] <- counter  
    capture_state[counter] <- ifelse(state_even,'EVEN','ODD')
    #check even/odd state
    
    number <- ifelse(state_even,
                     (number / 2),
                     (3*number + 1))
    
    counter <- counter + 1
    
  }
  
  output <- data.frame(capture_iteration,capture_state,capture_number)
  
  final_row <- data.frame(capture_iteration = nrow(output) + 1,
                          capture_state = 'END',
                          capture_number = 1)
  
  output_final <- rbind(output,final_row)
  
  return(output_final)
  
}