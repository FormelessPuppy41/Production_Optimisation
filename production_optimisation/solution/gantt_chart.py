import matplotlib
import matplotlib.pyplot as plt
import plotly.express as px
import pandas as pd


class GanttChart:
    def __init__(self, dataframe: pd.DataFrame):
        self.dataframe = dataframe.copy().stack()
        self.dataDict = self.dataframe.to_dict()
        print(self.dataframe)
    
    def convert_dataframe(self):
        self.df = pd.DataFrame(self.dataDict.items(), columns=["task", "duration"])
        self.df[["start_time", "empl_line", "order_suborder"]] = pd.DataFrame(self.df["task"].tolist(), index=self.df.index)

        # Filter out tasks with duration = 0
        self.df = self.df[self.df["duration"] > 0]

        # Convert "start_time" to datetime
        self.df["start_time"] = pd.to_datetime(self.df["start_time"])
        

    def create_ganttchart(self):
        fig = px.timeline(self.df, x_start="start_time", x_end="start_time", y="empl_line", title="Gantt Chart")
        fig.update_yaxes(categoryorder="total ascending")

        # Show the Gantt chart
        fig.show(renderer='chrome')