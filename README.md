TruckSTM %%%% -- Please read the paper for full details.

##Defining states###
1> States need to be defined in the "state_defs" directory under the current working directory.
2> Please follow the definition format from paper.
3> Two sample json definitions are provided in the "state_defs" directory for reference.
4> After creating a new state definition file, please put the file name in the conf.cfg file in this directory.

##Creating message sources#####
1> In the input_readers directory, locate the reader.py file. The function has a get_data function.
2> Create a new function to read from an source.
3> call the function from the get_data method. 
4> Do pass the input_q and put messages into it.

##Extending TruckSTM ######
1> Every module in Truck STM contains three default functions:- communicate, startup and process.
2> DO NOT modify the communicate function. MAke any startup changes to startup function and pass any arguments to it from the startup function, if required. 
3> Make any runtime changes in the process function.

### HAPPY TRUCK VISUALIATION #####
