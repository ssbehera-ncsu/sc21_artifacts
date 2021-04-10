import random
from math import exp, expm1
#from mpmath import findroot
import re
import numpy as np
#from interval_tree import *
from scipy.optimize import *

class Weibull:
    def __init__(self, shape=1, scale=1, location=0):
        self.type = 'weibull'
        self.shape = shape
        self.scale = scale
        self.location = location

    def get_type(self):
        return self.type

    def cdf(self, x):
        return -expm1(-((x-self.location)/self.scale)**self.shape)

    def pdf(self, x):
        #print self.shape/self.scale, (x-self.location)/self.scale, self.shape-1, -((x-self.location)/self.scale)**(self.shape)
        return (self.shape/self.scale)*((x-self.location)/self.scale)**(self.shape-1)*exp(-((x-self.location)/self.scale)**(self.shape))

    def hazard(self, x):
        #return self.pdf(x)/(1-self.cdf(x))
        return (self.shape/self.scale)*((x/self.scale)**(self.shape-1))
        
    def draw(self):
        return random.weibullvariate(self.scale, self.shape)


class Exponential:
    def __init__(self, rate=1):
        self.type = 'exponential'
        self.rate = rate

    def get_type(self):
        return self.type

    def get_rate(self):
        return self.rate

    def get_mttr(self):
        return 1.0/self.rate

    def cdf(self, x):
        #return 1-exp(-self.rate*x)
        #if x != float('inf'):
        #    print x, self.rate
        return -expm1(-self.rate*x)

    def pdf(self, x):
        return self.rate*exp(-self.rate*x)

    def hazard(self, x):
        return self.rate

    def draw(self):
        return random.expovariate(self.rate)

    def shifted_draw(self, tau):
        return random.expovariate(self.rate)+tau

