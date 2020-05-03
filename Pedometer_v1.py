from microbit import accelerometer
from microbit import sleep
import math
import utime as ut
class MovingAverage:  #Moving Average filter to detect a "dynamic threshold"
    data_pool = 0  #Size of data_pool -> amount of Samples
    circular_buffer_index = 0 #index to know where to read/write
    moving_average = 0 #moving average value

    def __init__(self, size):
        self.data_pool = [0]*size #initialize an array for all the samples (size of data_pool)

    def add_value(self, value): #adds a new sample to the pool
        self.circular_buffer_index += 1 #move the index
        if self.circular_buffer_index >= len(self.data_pool): #end? -> start at 0
            self.circular_buffer_index = 0
        old_value = self.data_pool[self.circular_buffer_index]/len(self.data_pool) #save the average of old value at index position
        self.data_pool[self.circular_buffer_index] = value #write the new value
        self.moving_average -= old_value #calculate the moving average = n1+n2+...ndata_pool/data_pool
        self.moving_average += value/len(self.data_pool) #middle part stays the same = faster way is to substract the oldest value and add the newest value to moving_average

    def get_average(self):
        return(self.moving_average)

class DynamicThreshold:
    maxi = 0 #Maximum Value
    mini = 2000 #Minimum Value
    dynamic_threshold = 0 #moving average value
    update_rate = 0
    sample_count = 0

    def __init__(self, update):
        self.update_rate = update

    def add_value(self, value):
        if self.sample_count > self.update_rate:
            self.dynamic_threshold = (self.maxi + self.mini) / 2
            self.maxi = 0
            self.mini = 2000
            self.sample_count = 0
        if value > self.maxi:
            self.maxi = value
        if value < self.mini:
            self.mini = value
        self.sample_count += 1
    def get_thres(self):
        return(self.dynamic_threshold)
    def get_min(self):
        return(self.mini)
    def get_max(self):
        return(self.maxi)

class LinearShiftRegister: #Linear-shift-register helps further filtering the data and detecting peaks
    sample_new = 0 #holds the newest sample
    sample_old = 0 #holds the previous sample
    precision = 0 #difference between the previous and the current value in order to be pushed to sample_new
    is_step = False
    step_duration = 0
    def __init__(self, prec):
        self.precision = prec
    def update(self, sample_result, moving_av): #updates the Register and watches for peaks
        self.sample_old = self.sample_new #shift new sample to old one
        if sample_result > self.sample_new + self.precision or sample_result < self.sample_new - self.precision: #is the sample_result precision bigger or smaller
            self.sample_new = sample_result #shift sample result to sample_new
            if self.sample_new < self.sample_old and self.sample_new < moving_av: #is it a downward peak that goes under the moving average?
                self.is_step = True #has to be a step
            else:
                self.is_step = False
                #self.step_duration = 0

        #if self.is_step:
            #self.step_duration += 1
            #if self.step_duration >= 100:
                #self.step_duration = 0
                #self.is_step = False
        return self.is_step

    def ret_new(self):
        return (self.sample_new)
    def ret_old(self):
        return (self.sample_old)

class CountRegulation:
    searching_regulation = True #puts the counter in searching for a rhythmic pattern False = found one
    steps_temp = 0 #holds the temporary steps

    def validate_step(self, interval, regulation):
        #interval = the time between two steps regulation = amount of steps it takes to be a
        #rhythmic pattern
        if self.steps_temp >= regulation: # True = we are in rhythmic pattern now and start back at 0
            self.steps_temp = 0
            self.searching_regulation = False
        if interval >= 10 and interval <= 100: #the step happened in a valid timewindow
            self.steps_temp += 1 #increase steps_temp
            print("Valid Step -------------------  ", self.steps_temp)
            if self.steps_temp >= regulation: #are we in a pattern?
                self.searching_regulation = False #then go in found mode to update frequently

        else:
            self.steps_temp = 0 #means pattern is set to 0 again
            self.searching_regulation = True #we have to search a new one

        if self.searching_regulation == False: #means we are in a pattern and can now update the steps
            return self.steps_temp
        else: #in no pattern yet and will just return 0
            return 0

def quadsum(values):
    sum = 0
    for x in values:
        sum += x*x
    return sum

moving_a = MovingAverage(50) #moving average
dynamic_thres = DynamicThreshold(50) #dynamic_threshold
linear_s = LinearShiftRegister(70) #LinearShiftRegister
count_reg = CountRegulation() #Regulates whether the step is valid
steps = 0 #steps taken
wron_steps = 0 #how many wrong steps
interval = 0 #interval


while True:
    values = accelerometer.get_values() #x, y, z -> tuple
    average = math.sqrt(quadsum(values)/3) #average of the three values
    moving_a.add_value(average) #moving average filter gets the new data
    #dynamic_thres.add_value(average)

    if linear_s.update(average, moving_a.get_average()): #peak went under the moving_average value
        steps += count_reg.validate_step(interval,1)
        print("Steps: ", steps)
        interval = 0
    #if moving_a.get_average() > moving_b.get_average():
     #   display.set_pixel(2,2,9)
    #else:
     #   display.set_pixel(2,2,0)
    #print((average, moving_a.get_average(), linear_s.ret()))
    #1000 if linear_s.update(average, moving_a.get_average()) else 0,
    print((linear_s.ret_new(), moving_a.get_average()))

    #print(dynamic_thres.get_thres())

    sleep(13) #-> 6ms for the calculations + 14 = 20ms = 50Hz
    interval += 1 #one cyle is complete so update the rate
