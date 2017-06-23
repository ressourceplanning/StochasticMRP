import pandas as pd
import numpy as np
import openpyxl as opxl

import math
from ScenarioTree import ScenarioTree
from ScenarioTreeNode import ScenarioTreeNode
from Scenario import Scenario
import cPickle as pickle
import os
from random import randint
from Tool import Tool
import random
import math
from Constants import Constants

class MRPInstance:

    FileName = "./Instances/MSOM-06-038-R2.xls"

    #This function print the instance on the screen
    def PrintInstance( self ):
        print "instance: %s" %self.InstanceName
        print "instance with %d products and %d time buckets" % ( self.NrProduct, self.NrTimeBucket );
        print "requirements: \n %r" % (pd.DataFrame( self.Requirements, index = self.ProductName, columns = self.ProductName ) );
        aggregated = [ self.Leadtimes, self.StartingInventories, self.InventoryCosts,
                       self.SetupCosts, self.BackorderCosts]
        col = [ "Leadtimes", "StartingInventories", "InventoryCosts", "SetupCosts", "BackorderCosts" ]
        print "Per product data: \n %r" % ( pd.DataFrame( aggregated, columns = self.ProductName, index = col ).transpose() );
        print "capacity: \n %r"%(pd.DataFrame( self.Capacity ) );
        print "processing time: \n %r"%(pd.DataFrame( self.ProcessingTime, index = self.ProductName ) );

        #self.DemandScenarioTree.Display()
        # Print the set of scenario
        #print "Print the scenarios:"
        #for s in self.Scenarios:
        #    s.DisplayScenario()



    #This function define the current instance as a  small one, used to test the model
    def DefineAsSmallIntance(self ):
        self.InstanceName = "SmallIntance"
        self.Distribution = "Normal"
        self.ProductName = [ "P1", "P2", "P3", "P4", "P5" ]
        self.NrProduct = 5
        self.NrTimeBucket = 6
        self.NrTimeBucketWithoutUncertainty = 3
        self.NrResource = 5
        self.Gamma = 0.9
        self.Requirements = [ [ 0, 1, 1, 0, 0 ],
                              [ 0, 0, 0, 1, 0 ],
                              [ 0, 0, 0, 0, 0 ],
                              [  0, 0, 0, 0, 1 ],
                              [ 0, 0, 0, 0, 0 ] ]
        self.Leadtimes = [0, 1, 1, 1, 1]
        self.ProcessingTime =[ [1, 0, 0, 0, 0],
                               [0, 2, 0, 0, 0],
                               [0, 0, 5, 0, 0],
                               [0, 0, 0, 1, 2],
                               [0, 0, 0, 1, 5] ]

        self.YearlyAverageDemand = [10, 0, 0, 0, 0]
        self.ForecastedAverageDemand = [ [10, 0, 0, 0, 0],
                                         [10, 0, 0, 0, 0],
                                         [10, 0, 0, 0, 0],
                                         [10, 0, 0, 0, 0],
                                         [10, 0, 0, 0, 0] ]
        self.ForecastError = [0.5, 0, 0, 0, 0]
        self.RateOfKnownDemand = 0.0
        self.YearlyStandardDevDemands = [5, 0, 0, 0, 0]
        self.ForcastedStandardDeviation = [ [5, 0, 0, 0, 0],
                                            [5, 0, 0, 0, 0],
                                            [5, 0, 0, 0, 0],
                                            [5, 0, 0, 0, 0],
                                            [5, 0, 0, 0, 0] ]

        self.StartingInventories = [10.0, 100.0, 100.0, 100.0, 100.0]
        self.InventoryCosts = [15.0, 4.0, 3.0, 2.0, 1.0]
        self.SetupCosts = [10000.0, 1.0, 1.0, 1.0, 1.0]
        self.BackorderCosts = [100000.0, 0.0, 0.0, 0.0, 0.0]  # for now assume no external demand for components
        self.Capacity = [ 15, 15, 15, 15, 15 ]
        self.LostSaleCost = [1000.0, 0.0, 0.0, 0.0, 0.0]
        self.ComputeInstanceData()

     # This function defines a very small instance, this is usefull for debugging.
    def DefineAsSuperSmallIntance(self ):
        self.InstanceName = "SuperSmallIntance"
        self.Distribution = "Normal"
        self.ProductName = [ "P1", "P2" ]
        self.NrProduct = 2
        self.NrTimeBucket = 6
        self.NrTimeBucketWithoutUncertainty = 3
        self.NrResource = 2
        self.Gamma = 0.9
        self.Requirements = [ [ 0, 1 ],
                              [ 0, 0 ] ]
        self.Capacity = [ 15, 50 ]
        self.Leadtimes = [ 1, 1 ]
        self.ProcessingTime = [ [ 1, 0 ],
                                [ 0, 1 ] ]

        self.YearlyAverageDemand = [ 10, 0 ]
        self.ForecastedAverageDemand =  [ [ 10, 0 ],
                                          [ 10, 0 ],
                                          [ 10, 0 ],
                                          [10, 0],
                                          [10, 0],
                                          [10, 0]
                                          ]
        self.ForecastError = [ 0.5, 0 ]
        self.RateOfKnownDemand = 0.0
        self.YearlyStandardDevDemands = [5, 0]
        self.ForcastedStandardDeviation = [ [ 5, 0 ],
                                            [5, 0],
                                            [5, 0],
                                            [5, 0],
                                            [5, 0],
                                            [ 5, 0 ] ]

        self.StartingInventories = [ 10.0, 10.0 ]
        self.InventoryCosts = [ 10.0, 5.0 ]
        self.SetupCosts = [ 5.0, 5.0 ]
        self.BackorderCosts = [ 100.0, 0.0 ]  # for now assume no external demand for components
        self.LostSaleCost = [1000.0, 0.0]
        self.ComputeInstanceData()

    #This function compute the data required to solve the instance ( indices of the variable, cretae the scenarios, level in the supply chain, .... )
    def ComputeInstanceData(self):
        self.ComputeIndices()
        self.ComputeLevel()
        self.ComputeMaxLeadTime()
        self.RequieredProduct = [ [ q for q in self.ProductSet  if self.Requirements[ q ][ p ] > 0.0 ]
                                                                    for p in self.ProductSet ]
        self.ComputeHasExternalDemand()
    #Constructor
    def __init__( self ):
        self.InstanceName = ""
        self.NrProduct = -1
        self.NrTimeBucket = -1
        self.NrTimeBucketWithoutUncertainty = -1
        self.NrResource = -1
        self.LostSaleCost = []
        self.Gamma = 0
        self.ProductSet = []
        self.ProductWithExternalDemand = []
        #The table below give an index to each product with an external demand.
        self.ProductWithExternalDemandIndex = []
        self.ProductWithoutExternalDemandIndex = []
        self.TimeBucketSet = []
        self.ResourceSet = []
        self.YearlyAverageDemand = []
        self.ForecastedAverageDemand = []
        self.ProcessingTime = []
        self.YearlyStandardDevDemands = []
        self.ForecastError = -1
        self.RateOfKnownDemand = -1
        self.ForcastedStandardDeviation = []
        self.Requirements = []
        self.Leadtimes = []
        self.StartingInventories = []
        self.InventoryCosts = []
        self.SetupCosts = []
        self.BackorderCosts = []
        self.HasExternalDemand = []
        #The set of product which are required for production of each product.
        self.RequieredProduct = []

        self.ProductName = ""
        #Compute some statistic about the instance
        self.MaxLeadTime = -1
        self.NrLevel = -1
        self.Level = [] # The level of each product in the bom
        self.MaxLeadTimeProduct = [] #The maximum leadtime to the component for each product
       # self.DemandScenarioTree = ScenarioTree( instance = self )


        #If this is true, a single scenario with average demand is generated
        self.Average = False
        self.LoadScenarioFromFile = False
        self.BranchingStrategy = 3

    #Compute the lead time from a product to its component with the largest sum of lead time
    def ComputeMaxLeadTime( self ):
        self.MaxLeadTimeProduct = [ 0 for p in self.ProductSet ]
        levelset = sorted( set(  self.Level ), reverse=True )
        for l in levelset:
            prodinlevel = [ p for p in self.ProductSet if  self.Level[ p ] == l ]
            for p in prodinlevel:
                parents = [ q for q in self.ProductSet if self.Requirements[ p ][ q ] > 0 ]
                if len( parents ) > 0 :
                    self.MaxLeadTimeProduct[ p ] = max( [ self.MaxLeadTimeProduct [ q ] for q in parents ] );
                self.MaxLeadTimeProduct[p] =  self.MaxLeadTimeProduct[p] + self.Leadtimes[ p ]
        self.MaxLeadTime = max( self.MaxLeadTimeProduct[p] for p in self.ProductSet )

    #This function compute at which level each node is in the supply chain
    def ComputeLevel( self ) :
        #Maximum lead time and maximum number of level.
        #Get the set of nodes without children
        currentlevelset = [ p for p in self.ProductSet if sum( self.Requirements[ q ][ p ]
                                                              for q in self.ProductSet  ) == 0 ];
        currentlevel = 1
        self.Level = [ 0 for p in self.ProductSet ]
        while len(currentlevelset) > 0 :
            nextlevelset = []
            for p in currentlevelset:
                self.Level[ p ] = currentlevel
                childrenofp = [ q for q in self.ProductSet
                                   if self.Requirements[ p ][ q ] == 1];
                nextlevelset = nextlevelset + childrenofp
            currentlevelset = set( nextlevelset )
            currentlevel = currentlevel + 1

        self.NrLevel = max( self.Level[ p ] for p in self.ProductSet )

    def ComputeHasExternalDemand(self):
        self.HasExternalDemand = [  self.YearlyAverageDemand[p] > 0
                                    for p in self.ProductSet ]
        self.ProductWithExternalDemand = [ p for p in self.ProductSet if  self.HasExternalDemand[p] ]
        self.ProductWithoutExternalDemand = [p for p in self.ProductSet if not self.HasExternalDemand[p]]

        index = 0
        self.ProductWithExternalDemandIndex = [ 0 for p in self.ProductSet ]
        for p in self.ProductWithExternalDemand:
            self.ProductWithExternalDemandIndex[p] = index
            index = index + 1

        index = 0
        self.ProductWithoutExternalDemandIndex = [ 0 for p in self.ProductSet ]
        for p in self.ProductWithoutExternalDemand:
            self.ProductWithoutExternalDemandIndex[p] = index
            index = index + 1


    #Compute the start of index and the number of variables for the considered instance
    def ComputeIndices( self ):
        self.TimeBucketSet = range( self.NrTimeBucket )
        self.ResourceSet = range( self.NrResource )
        self.ProductSet = range( self.NrProduct )



    #This function load the scenario tree from a fil
    def LoadFromFile( self ):
        filepath = './Instances/' + self.InstanceName + '_Scenario%s.pkl'%self.ScenarioNr
        try:
          with open( filepath, 'rb') as input:
              result = pickle.load( input )
          return result
        except: 
          print "file %r not found" %(filepath)


    #This funciton read the instance from the file ./Instances/MSOM-06-038-R2.xlsx
    def ReadFromFile( self, instancename, distribution):
        wb2 = opxl.load_workbook( "./Instances/MSOM-06-038-R2.xlsx" )
        #The supplychain is defined in the sheet named "01_LL" and the data are in the sheet "01_SD"
        supplychaindf = Tool.ReadDataFrame( wb2, instancename + "_LL" )
        datasheetdf = Tool.ReadDataFrame( wb2, instancename + "_SD" )
        datasheetdf = datasheetdf.fillna(0)
        #read the data
        self.ProductName = list( datasheetdf.index.values )
        self.InstanceName = instancename
        #This set of instances assume no capacity
        self.NrResource =  len( self.ProductName )
        self.NrProduct = len( self.ProductName )
        self.NrTimeBucket = 0
        self.ComputeIndices()

        self.Distribution = distribution

        #Get the average demand, lead time
        self.Leadtimes = [randint( 1, 1 ) for p in self.ProductSet]

        #self.Leadtimes =  [  int ( math.ceil( datasheetdf.get_value( self.ProductName[ p ], 'stageTime' ) ) ) for p in self.ProductSet ]
        print " CAUTION: LEAD TIME ARe MODIFIED"
        #Compute the requireement from the supply chain. This set of instances assume the requirement of each arc is 1.
        self.Requirements = [ [ 0 ] * self.NrProduct for _ in self.ProductSet ]
        for i, row in supplychaindf.iterrows():
            self.Requirements[ self.ProductName.index( row.get_value('destinationStage' ) ) ][ self.ProductName.index( i ) ] = 1
        #Assume an inventory holding cost of 0.1 per day for now
        holdingcost = 0.1 / 250
        self.InventoryCosts = [ 0.0 ] * self.NrProduct
        #The cost of the product is given by  added value per stage. The cost of the product at each stage must be computed
        addedvalueatstage = [ datasheetdf.get_value( self.ProductName[ p ], 'stageCost' ) for p in self.ProductSet ]
        level = [ datasheetdf.get_value( self.ProductName[ p ], 'relDepth' ) for p in self.ProductSet    ]
        levelset = sorted( set( level ), reverse=True )
        for l in levelset:
            prodinlevel =  [ p for p in self.ProductSet  if level[p] == l ]
            for p in prodinlevel:
                addedvalueatstage[p] = sum(addedvalueatstage[ q ] * self.Requirements[p][q] for q in self.ProductSet ) + \
                                            addedvalueatstage[ p ]
                self.InventoryCosts[p] = holdingcost *  addedvalueatstage[ p ]


        self.ComputeLevel()
        self.ComputeMaxLeadTime( )
        # Consider a time horizon of 20 days plus the total lead time
        self.NrTimeBucket =  2 * self.MaxLeadTime
        self.NrTimeBucketWithoutUncertainty = self.MaxLeadTime
        self.ComputeIndices()


        #Generate the sets of scenarios
        self.YearlyAverageDemand = [ datasheetdf.get_value( self.ProductName[ p ], 'avgDemand') for p in self.ProductSet ]
        if distribution == Constants.SlowMoving:
            self.YearlyAverageDemand = [ 1 if datasheetdf.get_value( self.ProductName[ p ], 'avgDemand') > 0 else 0 for p in self.ProductSet]

        if distribution == Constants.Uniform:
            self.YearlyAverageDemand = [0.5 if datasheetdf.get_value(self.ProductName[p], 'avgDemand') > 0 else 0 for p in
                                  self.ProductSet]

        self.YearlyStandardDevDemands = [ datasheetdf.get_value( self.ProductName[ p ], 'stdDevDemand') for p in self.ProductSet ]

        stationarydistribution = ( self.Distribution == Constants.Normal ) or ( self.Distribution == Constants.SlowMoving ) or ( self.Distribution == Constants.Lumpy ) or ( self.Distribution == Constants.Uniform )

        if stationarydistribution:
            self.ForecastedAverageDemand = [ self.YearlyAverageDemand  for t in self.TimeBucketSet ]
            self.ForcastedStandardDeviation = [ self.YearlyStandardDevDemands for t in self.TimeBucketSet ]
            self.ForecastError =   [ self.YearlyStandardDevDemands[p] / self.YearlyAverageDemand[p] for t in self.TimeBucketSet ]
            self.RateOfKnownDemand = 0.0
        else:
            self.ForecastError = [ 0.25 for p in self.ProductSet ]
            self.RateOfKnownDemand = [ math.pow( 0.9, t+1) for t in self.TimeBucketSet ]
            self.ForecastedAverageDemand = [ [ np.floor( np.random.normal(self.YearlyAverageDemand[p], self.YearlyStandardDevDemands[p], 1).clip( min=0.0) ).tolist()[0]
                                               if self.YearlyStandardDevDemands[p] > 0 else float(self.YearlyAverageDemand[p])
                                               for p in self.ProductSet ] for t in self.TimeBucketSet ]

            self.ForcastedStandardDeviation = [ [ (1-self.RateOfKnownDemand[t]) *  self.ForecastError[p] *  self.ForecastedAverageDemand[t][p]
                                                 for p in self.ProductSet ] for t in self.TimeBucketSet ]

        #demand = ScenarioTreeNode.CreateDemandNormalDistributiondemand( self, 1, average = False, slowmoving = slowmoving )
        #self.FirstPeriodDemand = [ demand[p][0] for p in self.ProductSet ]

        # The data below are generated a according to the method given in "multi-item capacited lot-sizing with demand uncertainty, P Brandimarte, IJPR, 2006"


        dependentaveragedemand = [ self.YearlyAverageDemand[p] for p in self.ProductSet ]
        levelset = sorted(set(level), reverse=False)
        for l in levelset:
            prodinlevel = [p for p in self.ProductSet if level[p] == l]
            for p in prodinlevel:
                dependentaveragedemand[p] = sum(dependentaveragedemand[q] * self.Requirements[q][p] for q in self.ProductSet) + \
                                                dependentaveragedemand[p]
        # Assume a starting inventory is the average demand during the lead time
        self.StartingInventories = [   int( random.uniform( 0.75, 1.5 ) * dependentaveragedemand[ p ] * (self.Leadtimes[ p ] )  )   for p in self.ProductSet ]

        #This set of instances assume no setup
        self.SetupCosts =  [   ( ( ( dependentaveragedemand[ p ] / 2 ) * 0.25 *  self.InventoryCosts[p]  ) * random.uniform( 0.8, 1.2 ) )  for p in self.ProductSet ]

        self.ProcessingTime = [ [ randint( 1, 5 )
                                    if (p == k )   else 0.0
                                    for p in self.ProductSet ]
                                for k in range(self.NrResource) ]
        capacityfactor = 1.8;
        self.Capacity =  [ capacityfactor * sum ( dependentaveragedemand[ p ] * self.ProcessingTime[ p ][k] for p in self.ProductSet ) for k in range( self.NrResource ) ]

        # Gamma is set to 0.9 which is a common value (find reference!!!)
        self.Gamma = 0.9
        #Back order is twice the  holding cost as in :
        # Solving the capacitated lot - sizing problem with backorder consideration CH Cheng1 *, MS Madan2, Y Gupta3 and S So4
        # See how to set this value
        self.BackorderCosts = [ 10 * self.InventoryCosts[p]  for p in self.ProductSet ]
        self.LostSaleCost = [ 100 * self.InventoryCosts[p]  for p in self.ProductSet ] # [ randint( 200, 300 ) for p in self.ProductSet ]
        self.SaveCompleteInstanceInExelFile()
        self.ComputeInstanceData()


    #Save the scenario tree in a file
    #def SaveCompleteInstanceInFile( self ):
    #    result = None
    #    filepath = '/tmp/thesim/' + self.InstanceName + '_%r.pkl'%self.NrScenarioPerBranch
    #    try:
    #      with open( filepath, 'wb') as output:
    #           pickle.dump(self, output, pickle.HIGHEST_PROTOCOL)
    #    except:
    #      print "file %r not found" %(filepath)


    #Save the Instance in an Excel  file
    def SaveCompleteInstanceInExelFile( self ):
        writer = pd.ExcelWriter("./Instances/" + self.InstanceName + "_" + self.Distribution + ".xlsx",  engine='openpyxl' )

        general = [ self.InstanceName, self.NrProduct, self.NrTimeBucket, self.NrResource, self.Gamma, self.Distribution,  self.NrTimeBucketWithoutUncertainty  ]
        columnstab = [ "Name", "NrProducts", "NrBuckets", "NrResources", "Gamma", "Distribution", "NrTimeBucketWithoutUncertainty" ]
        generaldf = pd.DataFrame(general, index=columnstab )
        generaldf.to_excel( writer, "Generic" )

        requirementdf = pd.DataFrame( self.Requirements, index = self.ProductName, columns = self.ProductName )
        requirementdf.to_excel(writer, "Requirement")

        productdata = [ self.Leadtimes, self.StartingInventories, self.InventoryCosts,
                        self.SetupCosts, self.BackorderCosts, self.YearlyAverageDemand, self.YearlyStandardDevDemands,
                        self.LostSaleCost ]
        col = [ "Leadtimes", "StartingInventories", "InventoryCosts", "SetupCosts", "BackorderCosts", "AverageDemand", "StandardDevDemands", "LostSale" ]
        productdatadf = pd.DataFrame( productdata, columns=self.ProductName, index=col).transpose();
        productdatadf.to_excel(writer, "Productdata")

        capacitydf = pd.DataFrame( self.ForecastedAverageDemand, index=self.TimeBucketSet, columns = self.ProductName  )
        capacitydf.to_excel(writer, "ForecastedAverageDemand")

        capacitydf = pd.DataFrame( self.ForcastedStandardDeviation, index=self.TimeBucketSet, columns = self.ProductName  )
        capacitydf.to_excel(writer, "ForcastedStandardDeviation")

        capacitydf = pd.DataFrame( self.Capacity )
        capacitydf.to_excel(writer, "Capacity")

        requirementdf = pd.DataFrame(self.ProcessingTime, index=self.ProductName )
        requirementdf.to_excel(writer, "ProcessingTime")

        writer.save()


    #Save the Instance in an Excel  file
    def ReadInstanceFromExelFile( self, instancename, distribution ):
        wb2 = opxl.load_workbook("./Instances/" + instancename+ "_" + distribution + ".xlsx")

        # The supplychain is defined in the sheet named "01_LL" and the data are in the sheet "01_SD"
        Genericdf = Tool.ReadDataFrame(wb2, "Generic")
        self.InstanceName = Genericdf.get_value( 'Name', 0 )
        self.NrProduct = Genericdf.get_value('NrProducts', 0)
        self.NrTimeBucket = Genericdf.get_value('NrBuckets', 0)
        self.NrTimeBucketWithoutUncertainty = Genericdf.get_value('NrTimeBucketWithoutUncertainty', 0)
        self.NrResource = Genericdf.get_value('NrResources', 0)
        self.Gamma =  Genericdf.get_value('Gamma', 0)
        self.Distribution =  Genericdf.get_value('Distribution', 0)

        Productdatadf = Tool.ReadDataFrame(wb2, "Productdata")
        self.ProductName = list(Productdatadf.index.values)
        self.Leadtimes = Productdatadf[ 'Leadtimes' ].tolist()
        self.InventoryCosts = Productdatadf[ 'InventoryCosts' ].tolist()
        self.YearlyAverageDemand = Productdatadf[ 'AverageDemand' ].tolist()
        self.YearlyStandardDevDemands = Productdatadf[ 'StandardDevDemands' ].tolist()
        self.BackorderCosts = Productdatadf['BackorderCosts'].tolist()
        self.StartingInventories = Productdatadf['StartingInventories'].tolist()
        self.SetupCosts = Productdatadf['SetupCosts'].tolist()
        self.LostSaleCost = Productdatadf['LostSale'].tolist()
        self.ComputeIndices()
        Requirementdf = Tool.ReadDataFrame( wb2, "Requirement" )
        self.Requirements = [ [ Requirementdf.get_value( q, p ) for p in self.ProductName ] for q in self.ProductName ]

        Capacitydf = Tool.ReadDataFrame(wb2, "Capacity")
        self.Capacity = [ Capacitydf.get_value( k, 0 ) for k in self.ResourceSet ]

        Processingdf = Tool.ReadDataFrame( wb2, "ProcessingTime" )
        self.ProcessingTime = [[Processingdf.get_value(p, k) for p in self.ProductName] for k in self.ResourceSet]

        forecastedavgdemanddf = Tool.ReadDataFrame(wb2, "ForecastedAverageDemand")
        self.ForecastedAverageDemand = [ [ forecastedavgdemanddf.get_value(t, p) for p in self.ProductName] for t in self.TimeBucketSet ]

        forecastedstddf = Tool.ReadDataFrame(wb2, "ForcastedStandardDeviation")
        self.ForcastedStandardDeviation = [ [ forecastedstddf.get_value(t, p) for p in self.ProductName] for t in self.TimeBucketSet ]


        self.ComputeLevel()
        self.ComputeMaxLeadTime()
        self.ComputeIndices()
        self.ComputeInstanceData()