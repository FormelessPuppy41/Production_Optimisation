import matplotlib
import matplotlib.pyplot as plt
import plotly.express as px
import pandas as pd


# https://github.com/apexcharts/apexchpiarts.js/issues/705
# https://stackoverflow.com/questions/63793981/formatting-multilevel-axes-labels-with-plotly
# Multi category on y axis python graph. 

#https://www.youtube.com/watch?v=BWbPgVmh-bk
#!!!!!!!
#https://www.datacamp.com/tutorial/how-to-make-gantt-chart-in-python-matplotlib
#!!!!!!!
#https://towardsdatascience.com/gantt-charts-with-pythons-matplotlib-395b7af72d72

#TODO:
# COULD ALSO ADD A STEAMLIT PAGE, WITH A DATAFRAME LIKE THE ONE FOR RECO. SO, CONDITIONAL FORMATTING ON STARTING AND ENDING DATE. 
# BUT FIRST MOST IMPORTANT IS A PRODUCT FOR TESTING, LATER THE FANCY STUFF CAN BE ADDED.

class GanttChart:
    def __init__(self, dataframe: pd.DataFrame):
        self.df = dataframe
        self.plt = plt
    
    def show_plt(self):
        self.plt.show()

    def convert_dataframe(self, specific_orders: pd.DataFrame):
        if isinstance(self.df, pd.DataFrame):
            self.df = self.df.copy().stack()
        else:
            self.df = self.df.copy()

        self.df = self.df[self.df != 0.0]
        grouped = self.df.groupby(['order_suborder', 'time']).sum()
        self.grouped_df = grouped.reset_index()

        # Obtain the unique orders and suborders
        orders = []
        suborders = []
        for order_suborder in specific_orders.index:
            orders.append(specific_orders.loc[order_suborder].iloc[0])
            suborders.append(specific_orders.loc[order_suborder].iloc[1])

        self.orders = list(set(orders))
        self.suborders = list(set(suborders))

        # Adding the specific_orders to the solution.
        self.specific_solution = pd.merge(self.grouped_df.set_index('order_suborder'), specific_orders, left_index=True, right_index=True)
        print("************************")
        print(self.specific_solution)
        self.specific_solution = self.specific_solution.reset_index().set_index(['Order_number', 'Sub_order']).drop(['order_suborder'])
        print(self.specific_solution)


    def create_ganttchart(self):
        fig, ax = self.plt.subplots(figsize=(12, 8))

        """
        What needs to happen is:
        grouped data for each single order, then combinations for each suborder. 

        """
        order_subset = self.grouped_df.copy()

        #order_subset = order_subset.reset_index().set_index(['Order_number', 'Sub_order', 'time'])

        y_pos = 0
        for order in self.orders:
            for suborder in self.suborders:
                bar_height = 0.4
                try:
                    time = order_subset.loc[(order, suborder)]['time']
                    ax.barh(y=y_pos, left=time, width=pd.to_timedelta('1h'),  height=bar_height, alpha=0.6, label=f'Order {order}')
                    y_pos += 1
                except:
                    pass

        # Customize the plot
        ax.set_xlabel('Time')
        ax.set_ylabel('Order / Suborder')
        ax.set_title('Order Scheduling Gantt Chart')
        ax.set_xlim(pd.Timestamp('2023-08-21 00:00'), pd.Timestamp('2023-08-23 23:00'))
        ax.xaxis.grid(True)
        ax.xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%H:%M'))
        self.plt.xticks(rotation=0)
        ax.legend()
        self.plt.tight_layout()
