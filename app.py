from flask import Flask, jsonify

import numpy as np
import pandas as pd
import datetime as dt

import sqlalchemy as sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, inspect, func


#################################################
# Database Setup
#################################################
engine = create_engine('sqlite:///Resources/hawaii.sqlite', connect_args = {'check_same_thread': False})
session = Session(bind = engine)
conn = engine.connect()
Base = automap_base()
Base.prepare(engine, reflect = True)
Measurement = Base.classes.measurement
Station = Base.classes.station

latest_date_str = session.query(Measurement).order_by(Measurement.date.desc()).first().date
latest_date = dt.datetime.strptime(latest_date_str, '%Y-%m-%d')
one_year_ago_date = latest_date - dt.timedelta(days = 365)


#################################################
# Flask Setup
#################################################

app = Flask(__name__)

#################################################
# Flask Routes
#################################################

@app.route('/')
def index():
    return ('Welcome to the Hawaii Climate App!<br/>'
    'Available Routes:<br>'
    '/api/v1.0/precipitation<br>'
    '/api/v1.0/stations<br>'
    '/api/v1.0/tobs<br>'
    '/api/v1.0/&lt;start&gt;<br>'
    '/api/v1.0/&lt;start&gt;/&lt;end&gt;<br>'
    )
##################################################
# Flask Routes: Precipitation API
##################################################  
 
@app.route('/api/v1.0/precipitation')
def precipitation():
    results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= one_year_ago_date).all()
    prec = {result[0]:result[1] for result in results}
    return jsonify(prec)

##################################################
# Flask Routes: Stations API
################################################# 

@app.route('/api/v1.0/stations')
def stations():
    results = session.query(Station.station).all()
    final_result = list(np.ravel(results))
    return jsonify(stations = final_result)

##################################################
# Flask Routes: TOBS API for Station USC00519281
################################################# 

@app.route('/api/v1.0/tobs')
def tobs():
    results = session.query(Measurement.tobs).filter(Measurement.station == 'USC00519281').filter(Measurement.date > one_year_ago_date).all()
    final_result = list(np.ravel(results))
    return jsonify(temps = final_result)

##################################################
# Flask Routes: API For Start Date values: TMIN, TAVG, and TMAX 
################################################# 

@app.route("/api/v1.0/<startdate>")
def tobs_by_date(startdate):
    """Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.
    When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date."""

    return jsonify(session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= startdate).all())

##################################################
# Flask Routes: API For Start Date/End Date values: TMIN, TAVG, and TMAX 
################################################# 

@app.route("/api/v1.0/<startdate>/<enddate>")
def tobs_by_date_range(startdate, enddate):
    """Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.
        When given the start and the end date, calculate the TMIN, TAVG, and TMAX for dates between the start and end date inclusive."""

    return jsonify(session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= startdate).filter(Measurement.date <= enddate).all())


if __name__ == "__main__":
    app.run(debug=True)