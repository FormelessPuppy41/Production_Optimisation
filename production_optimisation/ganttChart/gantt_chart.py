import matplotlib
import matplotlib.pyplot as plt
import plotly.express as px
import pandas as pd


# https://github.com/apexcharts/apexcharts.js/issues/705
# https://stackoverflow.com/questions/63793981/formatting-multilevel-axes-labels-with-plotly
# Multi category on y axis python graph. 

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



        """y_pos = 0
        #print(order_subset)
        for order_number in self.specific_solution['Order_number'].unique():
            order_subset = self.specific_solution[self.specific_solution['Order_number'] == order_number]

            # Plot the horizontal bars
            ax.barh(
                y=str(order_number),
                left=order_subset['time'],
                width=pd.to_timedelta('1h'),  # Assuming data is hourly
                height=0.6,
                align='center',
                alpha=0.4,
                label=str(order_number)
            )

            # Add the order label
            ax.text(order_subset['time'].min() - pd.to_timedelta('2h'), y_pos, f'Order {order_number}', va='center', ha='right')

            # Increment the y-position for suborders
            y_pos -= 1

            # Loop through suborders within the current order
            for suborder in order_subset['Sub_order']:
                suborder_time = order_subset[order_subset['Sub_order'] == suborder]['time'].min()

                # Plot the suborder label
                ax.text(suborder_time - pd.to_timedelta('2h'), y_pos, suborder, va='center', ha='right')

                # Increment the y-position for the next suborder
                y_pos -= 1"""

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


        """
        for order in self.orders:
            order_subset = order_subset

        # Loop through each unique 'order_suborder'
        for order_suborder in self.grouped_df['order_suborder'].unique():
            subset = self.grouped_df[self.grouped_df['order_suborder'] == order_suborder]
            
            # Plot the horizontal bars
            ax.barh(
                y=order_suborder,
                left=subset['time'],
                width=pd.to_timedelta('1h'),  # Assuming data is hourly
                height=0.6,
                align='center',
                alpha=0.4,
                label=order_suborder
            )

        # Customize the plot
        ax.set_xlabel('Time')
        ax.set_ylabel('Order_Suborder')
        ax.set_title('Order Scheduling Gantt Chart')
        ax.set_xlim(pd.Timestamp('2023-08-21 00:00'), pd.Timestamp('2023-08-23 23:00')) #FIXME: automatically change to starting and ending date.
        ax.xaxis.grid(True)

        # Format x-axis labels to show time
        ax.xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%H:%M'))

        # Rotate x-axis labels for better visibility
        self.plt.xticks(rotation=0)

        # Add legend
        ax.legend()

        self.plt.tight_layout()"""