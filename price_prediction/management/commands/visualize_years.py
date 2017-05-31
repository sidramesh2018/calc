import plotly
from plotly.graph_objs import Bar,Layout,Scatter, Box, Annotation,Marker,Font,XAxis,YAxis 
import shutil
from price_prediction.models import LaborCategory
from inflation_calc import inflation
from django.core.management import BaseCommand
import datetime as dt

def bar_plot(data,filename):
    filename = "/Users/ericschles/Documents/projects/calc/price_prediction/"+filename
    data.sort()
    x_vals = [elem for elem in data]
    y_vals = [elem for elem in data]
        
    plotly.offline.plot({
        "data":[Bar(x=x_vals,y=y_vals)],
        "layout":Layout(
            title=filename.split(".")[0],
            xaxis={"showticklabels":False}
        )
    },auto_open=False)
    shutil.move("temp-plot.html",filename)

class Command(BaseCommand):
    def handle(self, *args, **options):
        labor_objects = LaborCategory.objects.all()
        frequency_by_year = {}
        base_year = 1992
        i = inflation.Inflation()
        print("got to 4loop")
        for obj in labor_objects:
            if not obj.date.year in frequency_by_year.keys():
                if obj.price > 501.00:
                    continue
                frequency_by_year[obj.date.year] = [i.inflate(round(float(obj.price),2), obj.date, dt.date(year=base_year, month=1, day=1), 'United States')]
            else:
                frequency_by_year[obj.date.year].append(i.inflate(round(float(obj.price),2), obj.date, dt.date(year=base_year, month=1, day=1), 'United States'))
        
        for key in frequency_by_year.keys():
            bar_plot(frequency_by_year[key],str(key)+"_viz.html") 
