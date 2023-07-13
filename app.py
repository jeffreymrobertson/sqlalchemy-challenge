# Import the dependencies.
from flask import Flask, jsonify
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, text, inspect, func
import numpy as np
import pandas as pd
import datetime as dt

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite", echo=False)

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################

app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def home():
    print("Server received request for 'Home' page...")
    return "Welcome to the Weather API!"

@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    query_date= dt.date(2017, 8 ,23) - dt.timedelta(days=365)
    query_data = session.query(Measurement.date, func.sum(Measurement.prcp)).group_by(Measurement.date).order_by(Measurement.date).\
    filter(Measurement.date >= query_date).all()
    session.close()
    year_rain = []
    for date, prcp in query_data:
        total_rain={}
        total_rain[date]=prcp
        year_rain.append(total_rain)
    return jsonify(year_rain)

@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    results = session.query(Station.station).all()
    session.close()
    station = list(np.ravel(results))
    return jsonify(station)


@app.route("/api/v1.0/tobs")
def tobs():
    query_date= dt.date(2017, 8 ,23) - dt.timedelta(days=365)
    mvp = session.query(Station.station,Measurement.date, Measurement.tobs).\
    filter(Station.id == 7 ,Measurement.date >= query_date).all()
    most_active = []
    for station, date, temp in mvp:
        md = {}
        md[date] = temp
        most_active.append(md)
        print(Measurement.date)
    return jsonify(most_active)
        

@app.route("/api/v1.0/<start>")
def tobsave(start): 
    most_active = session.query(Measurement.tobs).\
    filter(func.strftime("%Y-%m-%d",Measurement.date)==start).all()
    ave_temp = []
    for low, high, average in most_active:
        temp_dict = {}
        temp_dict["minimum temperature"]=low
        temp_dict["max temperature"] = high
        temp_dict["average temperature"] = average
        ave_temp.append(temp_dict)
    return jsonify(ave_temp)

@app.route("/api/v1.0/<start>/<end>")
def range(start,end):
    most_active = session.query(Measurement.date,Measurement.tobs).\
    filter(func.strftime("%Y-%m-%d",Measurement.date)>=start,func.strftime("%Y-%m-%d",Measurement.date)<=end).all()
    ave_temp = []
    for date, low, high, average in most_active:
        temp_dict = {}
        temp_dict["date"] = date
        temp_dict["minimum temperature"]=low
        temp_dict["max temperature"] = high
        temp_dict["average temperature"] = average
        ave_temp.append(temp_dict)
    return jsonify(ave_temp)
if __name__ == '__main__':
    app.run(debug=True)