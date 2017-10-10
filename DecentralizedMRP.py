from scipy import optimize
from scipy.stats import norm
from Constants import Constants
from scipy.integrate import quad
import numpy as np
#This object contains logic and methods to compute the classical MRP in decentralized fashion
class DecentralizedMRP(object):


    # constructor

    def __init__(self, mrpinstance):
        self.Instance =mrpinstance

    def GetDistribution(self, time, product, x):
        if self.Instance.Distribution == Constants.NonStationary:
            return norm.cdf(x, 1,1)#self.Intance.ForecastedAverageDemand[time][product], self.Intance.ForcastedStandardDeviation[time][product])

    def ComputeServiceLevel(self):
        safetystock = [ [ 0.0 for p in self.Instance.ProductSet] for t in self.Instance.TimeBucketSet ]

        for p in self.Instance.ProductSet:
            for t in self.Instance.TimeBucketSet:
                #def normpdf(x, mu, sigma):
                #    u = (x - mu) / abs(sigma)
                #    y = (1 / (np.sqrt(2 * np.pi) * abs(sigma))) * np.exp(-u * u / 2)
                #    return y
                step =0.01
                def dist(a) :
                     return   norm.cdf(a + step, self.Instance.ForecastedAverageDemand[t][p], self.Instance.ForcastedStandardDeviation[t][p] )

                def incrementalcost(x, p, t):
                    if  t < self.Instance.NrTimeBucket - 1:
                        result = self.Instance.InventoryCosts[p] * step * ( dist( x ) ) - self.Instance.BackorderCosts[p] * step * ( 1 - dist( x ) )
                    else :
                        result = self.Instance.InventoryCosts[p] *step *  (dist(x)) - (self.Instance.LostSaleCost[p] )*step *  ( 1 - dist(x))
                    return result

                x = self.Instance.ForecastedAverageDemand[t][p]

                while  incrementalcost(x,p,t) < 0:
                    x+= step
                print "optimized %s, value %r, proba %r, forecast %r std %r" %  (x,incrementalcost(x,p,t), dist(x), self.Instance.ForecastedAverageDemand[t][p], self.Instance.ForcastedStandardDeviation[t][p])

                safetystock[t][p] = x - self.Instance.ForecastedAverageDemand[t][p]

            #quad(lambda a: (x*x - a*x) * dist(a) , 100.0, x)[0] \
                    #quad(lambda a: (a*x - x*x) * dist(a), x, 100000000)[0] #np.inf

            #return quad( lambda a: self.Intance.InventoryCosts[0] *  self.GetDistribution( 0, 0, a), 0, x)[0] \
            #        +  quad(lambda a: self.Intance.BackorderCosts[0] * self.GetDistribution(0, 0, a), x, 10000000)[0]

                         # self.Intance.InventoryCosts[0] * ( self.GetDistribution( 0, 0, x) ) \
                   #+ self.Intance.BackorderCosts[0] * ( 1 -self.GetDistribution( 0, 0, x) )

     # optimize.minimize_scalar(F)


        return safetystock



