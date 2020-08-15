# Import dependencies
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

# Database Setup
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# Reflect an existing database into a new model
Base = automap_base()
# Reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Flask Setup
app = Flask(__name__)

# Flask routes

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end>"
    )

#---------------------------------------------------------
#               PRECIPITATION ROUTE
#---------------------------------------------------------

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create session from Python to the DB
    session = Session(engine)

    """Returns last year of precipitation data"""
    # Query for data
    previous_year = dt.date(2016, 8, 23)
    precip_results = session.query(Measurement.date, Measurement.prcp).\
        filter(func.strftime(Measurement.date) >= previous_year).all()

    session.close()

    # Put query results into a dictionary
    precip_data = {}
    for date, prcp in precip_results:
        precip_data[date] = prcp

    return jsonify(precip_data)

#---------------------------------------------------------
#                   STATIONS ROUTE
#---------------------------------------------------------

@app.route("/api/v1.0/stations")
def stations():
    # Create session from Python to the DB
    session = Session(engine)

    """Returns station list and their activity"""
    # Query for data
    sel_activity = [Measurement.station, func.count(Measurement.prcp)]
    station_activity = session.query(*sel_activity).group_by(Measurement.station).\
        order_by(func.count(Measurement.prcp).desc()).all()

    session.close()

    # Convert query data into list of dictionary items
    station_list = []
    for station, activity in station_activity:
        station_dict = {}
        station_dict["station"] = station
        station_dict["activity"] = activity
        station_list.append(station_dict)

    return jsonify(station_list)

#---------------------------------------------------------
#                   TOBS ROUTE
#---------------------------------------------------------

@app.route("/api/v1.0/tobs")
def tobs():
    # Create session from Python to the DB
    session = Session(engine)

    """Returns most active station's temp measurements for the last year"""
    # Query for data
    previous_year = dt.date(2016, 8, 23)
    active_station_temp_year = session.query(Measurement.date, Measurement.tobs).filter(func.strftime(Measurement.date) >= previous_year).\
        filter(Measurement.station == 'USC00519281').all()

    session.close()

    # Convert query data into list of dictionary items
    temp_year = []
    for date, temp in active_station_temp_year:
        temp_dict = {}
        temp_dict['date'] = date
        temp_dict['temp'] = temp
        temp_year.append(temp_dict)

    return jsonify(temp_year)

#---------------------------------------------------------
#                   START ONLY ROUTE
#---------------------------------------------------------

@app.route("/api/v1.0/<start>")
def temp_sum_start_date(start):
    # Create session from Python to the DB
    session = Session(engine)

    """Returns temp summary from start date"""
    # Query for data
    sel_sum = [Measurement.date,
          func.min(Measurement.tobs),
          func.max(Measurement.tobs),
          func.avg(Measurement.tobs)]
    start_date_summary = session.query(*sel_sum).filter(func.strftime(Measurement.date) >= start).\
        group_by(Measurement.date).all()

    session.close()

    # Convert list of tuples into normal list
    temp_sum = []
    for date, min, max, avg in start_date_summary:
        temp_sum_dict = {}
        temp_sum_dict['date'] = date
        temp_sum_dict['min'] = min
        temp_sum_dict['max'] = max
        temp_sum_dict['avg'] = avg
        temp_sum.append(temp_sum_dict)

    return jsonify(temp_sum)

#---------------------------------------------------------
#                   START & END ROUTE
#---------------------------------------------------------

@app.route("/api/v1.0/<start>/<end>")
def temp_sum_start_end(start, end):
    # Create session from Python to the DB
    session = Session(engine)

    """Returns temp summary from start to end date"""
    # Query for data
    
    sel_sum = [Measurement.date,
          func.min(Measurement.tobs),
          func.max(Measurement.tobs),
          func.avg(Measurement.tobs)]
    start_end_summary = session.query(*sel_sum).filter(func.strftime(Measurement.date) >= start).\
        filter(func.strftime(Measurement.date) <= end).group_by(Measurement.date).all()

    session.close()

    # Convert list of tuples into normal list
    temp_sum = []
    for date, min, max, avg in start_end_summary:
        temp_sum_dict = {}
        temp_sum_dict['date'] = date
        temp_sum_dict['min'] = min
        temp_sum_dict['max'] = max
        temp_sum_dict['avg'] = avg
        temp_sum.append(temp_sum_dict)

    return jsonify(temp_sum)

if __name__ == '__main__':
    app.run(debug=True)


