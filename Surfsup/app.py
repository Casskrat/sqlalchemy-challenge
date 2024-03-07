# Import the dependencies.

import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, distinct
from flask import Flask, jsonify


#################################################
# Database Setup
#################################################

engine = create_engine("sqlite:///Resources/hawaii.sqlite")
# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)
# Save references to each table
measurement = Base.classes.measurement
station = Base.classes.station
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
def welcome():
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/start/end"
    )
@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    date_q = session.query(measurement.date, measurement.prcp).\
        filter(measurement.date >= "2016-08-24").\
        all()
    session.close()
    precip_list = []
    for date,prcp  in date_q:
        precip_dict = {}
        precip_dict["date"] = date
        precip_dict["prcp"] = prcp
               
        precip_list.append(precip_dict)
    return jsonify(precip_list)

@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    sel = [measurement.station]
    stations = session.query(*sel).\
        group_by(measurement.station).all()
    session.close()
    
    stations_list = list(np.ravel(stations)) 
    return jsonify(stations_list)

@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    temp = session.query(measurement.date,  measurement.tobs,measurement.prcp).\
                filter(measurement.date >= '2016-08-23').\
                filter(measurement.station=='USC00519281').\
                order_by(measurement.date).all()
    session.close()
    temp_list = []
    for prcp, date,tobs in temp:
        temp_dict = {}
        temp_dict["prcp"] = prcp
        temp_dict["date"] = date
        temp_dict["tobs"] = tobs
        
        temp_list.append(temp_dict)
    return jsonify(temp_list)
@app.route("/api/v1.0/<start>")
def Start_date(start):
    session = Session(engine)
    start_q = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).\
                filter(measurement.date >= start).all()
    session.close()
    start_obs = []
    for min, avg, max in start_q:
        start_obs_dict = {}
        start_obs_dict["min_temp"] = min
        start_obs_dict["avg_temp"] = avg
        start_obs_dict["max_temp"] = max
        start_obs.append(start_obs_dict) 
    return jsonify(start_obs)

@app.route("/api/v1.0/<start>/<end>")
def Start_end_date(start, end):
    session = Session(engine)
    end_q= session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).\
                filter(measurement.date >= start).filter(measurement.date <= end).all()
    session.close()
    end_list = []
    for min, avg, max in end_q:
        end_dict = {}
        end_dict["min_temp"] = min
        end_dict["avg_temp"] = avg
        end_dict["max_temp"] = max
        end_list.append(end_dict) 
    

    return jsonify(end_list)


if __name__ == '__main__':
    app.run(debug=True)