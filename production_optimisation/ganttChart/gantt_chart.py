import matplotlib
import matplotlib.pyplot as plt
import plotly.express as px
import pandas as pd


class GanttChart:
    def __init__(self, dataframe: pd.DataFrame):
        self.df = dataframe
        self.plt = plt
    
    def show_plt(self):
        self.plt.show()

    def convert_dataframe(self):
        self.df = self.df.copy().stack()
        self.df = self.df[self.df != 0.0]
        grouped = self.df.groupby(['order_suborder', 'time']).sum()
        self.grouped_df = grouped.reset_index()
        print(self.grouped_df)
        

    def create_ganttchart(self):
        fig, ax = self.plt.subplots(figsize=(12, 8))

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
        ax.set_xlim(pd.Timestamp('2023-08-21 00:00'), pd.Timestamp('2023-08-23 23:00')) #FIXME automatically change to starting and ending date.
        ax.xaxis.grid(True)

        # Format x-axis labels to show time
        ax.xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%H:%M'))

        # Rotate x-axis labels for better visibility
        self.plt.xticks(rotation=0)

        # Add legend
        ax.legend()

        self.plt.tight_layout()