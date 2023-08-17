from problem_declaration.models import EWOptimisation

class solvabilityTest:
    def __init__(self):
        pass

    
    class solvabilityTestEW(EWOptimisation):
        def __init__(self, dataframes_class):
            self.dataframes_class
            super().__init__(self, dataframes_class=self.dataframes_class)

        def checkAvailability(self):
            self.dataframes_class.get_dataframe_by_name('df_orders')
