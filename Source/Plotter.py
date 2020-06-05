import matplotlib.pyplot as plt
import  plotly  as py
import plotly.graph_objs as go
import statistics
class Plotter:
    def __init__(self):
        print("plotter object")
        #self.color1s
        self.maranzanacolor = '#F5815B'
        self.myopiccolor = '#65BC9E'
        self.griacolor = '#8697C3'
        self.tbColor = '#DF7EBA'
        self.defaultColor = '#8A97C5'


    def plotTimeAndCostComparisons(self, ks,maranzana, myopic, gria, maranzana_time, myopic_time, gria_time):
        fig, ax1 = plt.subplots()
        t = ks

        ax1.plot(t, maranzana, self.maranzanacolor)
        ax1.set_xlabel('k')
        # Make the y-axis label, ticks and tick labels match the line color.
        ax1.set_ylabel('cost', color='b')
        ax1.tick_params('y', colors='b')

        ax2 = ax1.twinx()
        s2 = maranzana_time
        ax2.plot(t, s2, 'r.')
        ax2.set_ylabel('Time', color='r')
        ax2.tick_params('y', colors='r')

        fig.tight_layout()
        plt.show()


    def plotCostComparisons(self, ks, maranzana, myopic, gria):
        combined = {}
        combined['k'] = ks
        combined['Maranzana'] = maranzana
        combined['Myopic'] = myopic
        combined['Gria'] = gria
        plt.plot('k', 'Maranzana', data=combined, marker='o', markerfacecolor=self.maranzanacolor, markersize=12, color=self.maranzanacolor, linewidth=4, label="Maranzana")
        plt.plot('k', 'Myopic', data=combined, marker='.', markerfacecolor=self.myopiccolor, markersize=12, color=self.myopiccolor, linewidth=2, label ="Myopic")
        plt.plot('k', 'Gria', data=combined, marker='*',markerfacecolor=self.griacolor, markersize=12,  color=self.griacolor, linewidth=2, linestyle='dashed', label="GRIA")
        plt.legend()
        plt.show()


    def plotTimeAndCostWithPlotly(self, ks,maranzana, myopic, gria, maranzana_time, myopic_time, gria_time, fileName, title):
        trace11 = go.Scatter(
            x=ks,
            y=maranzana,
            mode = 'lines+markers',
            marker=dict(
                size=8,
                color=self.maranzanacolor,
                line=dict(
                    width=5,
                    color = self.maranzanacolor
                )
            ),
            name='Maranzana Cost'
        )
        trace12 = go.Scatter(
            x=ks,
            y=myopic,
            mode='lines+markers',
            marker=dict(
                size=8,
                color=self.myopiccolor,
                line=dict(
                    width=5,
                    color=self.myopiccolor
                )
            ),
            name='Myopic Cost'
        )
        trace13 = go.Scatter(
            x=ks,
            y=gria,
            mode='lines+markers',
            marker=dict(
                size=8,
                color=self.griacolor,
                line=dict(
                    width=5,
                    color=self.griacolor
                )
            ),
            name='GRIA Cost'
        )
        trace21 = go.Scatter(
            x=ks,
            y=maranzana_time,
            name='maranazana_time',
            line=dict(
                color=self.maranzanacolor,
                width=4,
                dash='dot'),
            yaxis='y2'
        )
        trace22 = go.Scatter(
            x=ks,
            y=myopic_time,
            name='Myopic Time',
            line=dict(
                color=self.myopiccolor,
                width=4,
                dash='dot'),
            yaxis='y2'
        )
        trace23 = go.Scatter(
            x=ks,
            y=gria_time,
            name='GRIA Time',
            line=dict(
                color=self.griacolor,
                width=4,
                dash='dot'),
            yaxis='y2'
        )
        data = [trace11, trace12, trace13, trace21, trace22, trace23]
        layout = go.Layout(
            title=title,
            yaxis=dict(
                title='Cost Ratio'
            ),
            yaxis2=dict(
                title='Time (in Seconds)',
                titlefont=dict(
                    color='rgb(4, 12, 73)'
                ),
                tickfont=dict(
                    color='rgb(4, 12, 73)'
                ),
                overlaying='y',
                side='right'
            ),
            legend=dict(x=0.4, y=1.4)
        )
        fig = go.Figure(data=data, layout=layout)
        py.offline.plot(fig, filename= 'plots/' + fileName + '.html')



    def plotVariationAndCalculateVariance(self, title, data, method, fileName ):
        runs = []
        values = []
        for r in data:
            runs.append(r)
            values.append(float(data[r]))

        median = statistics.median(values)
        maxv = max(values)
        minv = min(values)
        print(values)
        stdg = statistics.pstdev(values)
        avg = statistics.mean(values)
        #print("Median = " + str(median))
        #print("Max = " + str(maxv))
        #print("Std = " + str(stdg))
        #print("Avg = " + str(avg))

        #exit(0)
        color = self.defaultColor
        if method =="TB":
            color = self.tbColor
        if method == "Maranzana":
            color = self.maranzanacolor
        if method== "GRIA":
            color = self.griacolor
        trace23 = go.Scatter(
            x=runs,
            y=values,
            name='Cost Function',
            line=dict(
                color=self.griacolor,
                width=4,
                dash='dot')
        )
        layout = go.Layout(
            title=title,
            yaxis=dict(
                title='Cost Ratio'
            ))
        data = [trace23]
        return [median, maxv, minv, stdg, avg]
        #fig = go.Figure(data=data, layout=layout)
        #py.offline.plot(fig, filename='plots/' + fileName + '.html')


    def plotDistributionsForAllKs(self, title, dataDic, fileName):
        # data is a dictionary with data for all ks
        data = []
        for k in dataDic:
            trace = go.Histogram(
            x=dataDic[k],
            opacity=0.75,
            name = str(k)
            )
            data.append(trace)
            layout = go.Layout(barmode='overlay',   title=title,
    xaxis=dict(
        title='Cost Value'
    ),
    yaxis=dict(
        title='Count'
    ))
        fig = go.Figure(data=data, layout=layout)

        py.offline.plot(fig, filename=fileName)









