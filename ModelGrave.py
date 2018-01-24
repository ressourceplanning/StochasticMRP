import cplex

class ModelGrave(object):
    M = cplex.infinity

    # constructor

    def __init__(self, instance, owner ):

        self.Instance = instance
        self.Owner = owner
        self.nrvaluesS = 6
        self.NrVariable = self.Instance.NrProduct * self.nrvaluesS  * self.nrvaluesS
        self.Cplex = cplex.Cplex()
        self.XSSI = [ [ [ p + s * self.Instance.NrProduct  + si * self.nrvaluesS  * self.Instance.NrProduct
                     for p in range( self.Instance.NrProduct ) ]
                   for s in range( self.nrvaluesS ) ]
                 for si in range( self.nrvaluesS ) ]


    def ComputeSSI(self):
        self.CreateVariable()
        self.CreateConstraints()
        s, si = self.Solve()

        return s, si

    def CreateVariable( self ):
        costXSSI = [   sum ( self.Owner.GetCostGrave(s, si, p, t) for t in self.Instance.TimeBucketSet )
                         for si in range(self.nrvaluesS)
                         for s in range(self.nrvaluesS)
                         for p in range(self.Instance.NrProduct) ]

        NameXSSI = [ "Namepssi_%s_%s_%s"%(p, s, si)
                     for si in range(self.nrvaluesS)
                     for s in range(self.nrvaluesS)
                     for p in range(self.Instance.NrProduct) ]


        self.Cplex.variables.add(costXSSI,
                                 types=['B'] * self.NrVariable )
    def CreateConstraints(self):


        for p in range(self.Instance.NrProduct):
             vars = [ self.XSSI[si][s][p] for s in range(self.nrvaluesS)  for si in range(self.nrvaluesS) ]
             coeff = [1]* len(vars)

             self.Cplex.linear_constraints.add( lin_expr=[ cplex.SparsePair(vars, coeff) ],
                                                senses=[ "E" ],
                                                rhs=[ 1 ] )

        for p in range(self.Instance.NrProduct):
            for s in range(self.nrvaluesS):
                for si in range(self.nrvaluesS):
                     if( ( self.Instance.HasExternalDemand[p] and s > 0 )
                         or ( s - si > self.Instance.Leadtimes[p] )
                         or ( si > s ) ):
                        vars = [self.XSSI[si][s][p]]
                        coeff = [1]

                        self.Cplex.linear_constraints.add(lin_expr=[cplex.SparsePair(vars, coeff)],
                                                          senses=["E"],
                                                          rhs=[0])

    def Solve(self):
        self.Cplex.objective.set_sense(self.Cplex.objective.sense.minimize)
        #if Constants.Debug:
        #    self.Cplex.write("mrp.lp")

        # name = "mrp_log%r_%r_%r" % ( self.Instance.InstanceName, self.Model, self.DemandScenarioTree.Seed )
        # file = open("/tmp/thesim/CPLEXLog/%s.txt" % self.logfilename, 'w')
        self.Cplex.set_log_stream( None )
        self.Cplex.set_results_stream( None )
        self.Cplex.set_warning_stream( None )
        self.Cplex.set_error_stream( None )

        # tune the paramters
        self.Cplex.parameters.timelimit.set(100)
        self.Cplex.parameters.mip.limits.treememory.set(700000000.0)
        self.Cplex.parameters.threads.set(1)
        #self.TuneCplexParamter()

        #if self.YFixHeuristic:
        #    self.Cplex.parameters.lpmethod.set(self.Cplex.parameters.lpmethod.values.barrier)
        #    self.Cplex.parameters.threads.set(1)

        #end_modeling = time.time();

        self.Cplex.solve()


        # Handle the results
        sol = self.Cplex.solution
        xssi = [ i for i in range( self.NrVariable ) ]

        values = sol.get_values(xssi)

        xssivalues = [[[ values [ p + s * self.Instance.NrProduct + si * self.nrvaluesS * self.Instance.NrProduct]
                       for p in range(self.Instance.NrProduct)]
                      for s in range(self.nrvaluesS)]
                     for si in range(self.nrvaluesS)]



        S = [ -1 for p in range(self.Instance.NrProduct)]
        SI = [ -1 for p in range(self.Instance.NrProduct)]

        for p in range(self.Instance.NrProduct):
            for s in range(self.nrvaluesS):
                for si in range(self.nrvaluesS):
                    if xssivalues[si][s][p] > 0.9:
                        SI[p]= si
                        S[p] = s

        return S, SI