from microbit import accelerometer
from microbit import sleep
import math

class MovingAverage:  #Moving Average filter to detect a "dynamic threshold"
    samples = 0
    circular_buffer_index = 0 #index to know where to read/write
    moving_average = 0 #moving average value

    def __init__(self, size):
        self.samples = [0]*size #initialize an array for all the samples (size of samples)

    def add_sample(self, value): #adds a new sample to the pool
        self.circular_buffer_index += 1 #move the index
        if self.circular_buffer_index >= len(self.samples): #end? -> start at 0
            self.circular_buffer_index = 0
        old_value = self.samples[self.circular_buffer_index]/len(self.samples) #save the average of old value at index position
        self.samples[self.circular_buffer_index] = value #write the new value
        self.moving_average -= old_value #calculate the moving average = n1+n2+...nsamples/samples
        self.moving_average += value/len(self.samples) #middle part stays the same = faster way is to substract the oldest value and add the newest value to moving_average

    def get_average(self):
        return(self.moving_average)


class LinearShiftRegister: #Linear-shift-register helps further filtering the data and detecting peaks
    sample_new = 0 #holds the newest sample
    sample_old = 0 #holds the previous sample
    precision = 0 #difference between the previous and the current value in order to be pushed to sample_new
    is_step = False

    def __init__(self, prec):
        self.precision = prec

    def _is_step(self, sample_result, moving_av): #updates the Register and watches for peaks
        self.sample_old = self.sample_new #shift new sample to old one
        if sample_result > self.sample_new + self.precision or sample_result < self.sample_new - self.precision: #is the sample_result precision bigger or smaller
            self.sample_new = sample_result #shift sample result to sample_new
            if self.sample_new < self.sample_old and self.sample_new < moving_av: #is it a downward peak that goes under the moving average?
                self.is_step = True #has to be a step
            else:
                self.is_step = False
        return self.is_step

    def get_newsample(self):
        return (self.sample_new)
    def get_oldsample(self):
        return (self.sample_old)

steps_temp = 0 #holds the temporary steps

#class CountRegulation:


def quadsum(values):
    sum = 0
    for x in values:
        sum += x*x
    return sum

moving_a = MovingAverage(50) #moving average
linearshift_reg = LinearShiftRegister(70) #LinearShiftRegister
#count_reg = CountRegulation() #Regulates whether the step is valid
steps = 0 #steps taken
interval = 0 #interval


while True:
    Accelerometer = accelerometer.get_values() #x, y, z -> tuple
    AccelerometerAverage = math.sqrt(quadsum(Accelerometer)/3) #average of the three values
    moving_a.add_sample(AccelerometerAverage) #moving average filter gets the new data

    if linearshift_reg._is_step(AccelerometerAverage, moving_a.get_average()): #peak went under the moving_average value
        print("Steps: ", steps)

    print((moving_a.get_average(), linearshift_reg.get_oldsample()))

    sleep(13) #-> 6ms for the calculations + 14 = 20ms = 50Hz
