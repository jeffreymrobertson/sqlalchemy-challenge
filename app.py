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
    station = session.query(Station.name).distinct().all()
    session.close()
    # station_list = [place.asDict() for place in station]
    return jsonify(station.dump())


# @app.route("/api/v1.0/tobs")

# @app.route("/api/v1.0/<start>")

# @app.route("/api/v1.0/<start>/<end>")

if __name__ == '__main__':
    app.run(debug=True)