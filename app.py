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
    return (f"Welcome to the Weather API!<br/>"
            f"Available paths:<br/>"
            f"/api/v1.0/precipitation<br/>"
            f"/api/v1.0/stations<br/>"
            f"/api/v1.0/tobs<br/>"
            f"/api/v1.0/<start><br/>"
            f"Note: Date format: (yyyy-mm-dd)<br/>"
            f"/api/v1.0/<start>/<end>")

@app.route("/api/v1.0/precipitation")
def precipitation():
    #starts the session
    session = Session(engine)
    #sets the date
    query_date= dt.date(2017, 8 ,23) - dt.timedelta(days=365)
    #queries the data
    query_data = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= query_date).\
        order_by(Measurement.date).all()
    precipitation = {date:prcp for date,prcp in query_data}
    session.close()
    return jsonify(precipitation)

@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    result = []
    results = session.query(Station.station, Station.id).all()
    #add the station name and id to a dictionairy and add them to a list
    for station, id in results:
        stations_dict = {}
        stations_dict['station'] = station
        stations_dict['id'] = id
        result.append(stations_dict)
    session.close()
    return jsonify(result)


@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    query_date= dt.date(2017, 8 ,23) - dt.timedelta(days=365)
    results = session.query(Measurement.station).\
                order_by(func.count(Measurement.station).desc()).\
                group_by(Measurement.station).first()
    #gets the most active data
    result_one = results[0]
    years_data = session.query(Measurement.date,Measurement.tobs).\
        filter(Measurement.station == result_one).\
        filter(Measurement.date >= query_date)
    most_active = []
    for date, temp in years_data:
        md = {}
        md['date'] = date
        md['tobs'] = temp
        most_active.append(md)
        print(Measurement.date)
    session.close()
    return jsonify(most_active)

        

@app.route("/api/v1.0/<start>")
def tobsave(start): 
    session = Session(engine)
    results = session.query(func.min(Measurement.tobs),func.max(Measurement.tobs),func.avg(Measurement.tobs)).\
                                filter(Measurement.date == start).all()
    tobs_data = []
    for minimum, maximum, average in results:
        result_dic = {}
        result_dic['Minimum Temperature'] = minimum
        result_dic['Maximum Temperature'] = maximum
        result_dic['Average Temperature'] = average
        tobs_data.append(result_dic)
        #if there is data then return the data
        if result_dic['Minimum Temperature']:
            session.close()
            return jsonify(tobs_data)
        #if it doesn't have a value return an error message
        else:
            session.close()
            return jsonify('There is no data for this date please select a new date')
    
        


@app.route("/api/v1.0/<start>/<end>")
def range(start,end):
    most_active = session.query(Measurement.date,func.min(Measurement.tobs),func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
    filter(func.strftime("%Y-%m-%d",Measurement.date)>=start,func.strftime("%Y-%m-%d",Measurement.date)<=end).\
        group_by(Measurement.date).all()
    ave_temp = []
    for date, min, max, ave in most_active:
        result = {}
        result[date] = {"Low": min, "High": max, "Average": ave}
        ave_temp.append(result)
    session.close()
    return jsonify(ave_temp)
if __name__ == '__main__':
    app.run(debug=True)