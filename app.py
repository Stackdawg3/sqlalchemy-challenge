import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///titanic.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
measurement = base.classes.measurement
station = base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end><br/>"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query all date and prcp
    results = session.query(measurement.date, measurement.prcp).all()

    session.close()

    # Convert list of tuples into normal dictionary
    precipitation_data = dict(np.ravel(results))

    return jsonify(precipitation_data)


@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query all stations
    results = session.query(station.station).group_by(station.station).all()

    session.close()

    # Convert list of tuples into normal list
    station_data = list(np.ravel(results))

    return jsonify(station_data)



@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query dates and temps
    active_stations = session.query(measurement.station, func.count(measurement.station)).\
        group_by(measurement.station).order_by(func.count(measurement.station).desc()).all()
    
    most_active = active_stations[0][0]

    # Temp for previous year
    year_ago = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    year_temp = session.query(measurement.date, measurement.tobs).filter(measurement.date > year_ago).\
        filter(measurement.station == most_active).order_by(measurement.date).all()

    station_temp = pd.DataFrame(year_temp, columns=['date', 'tobs'])
    station_temp = station_temp.set_index('date')
    station_temp = station_temp.dropna()

    session.close()

    # Convert list of tuples into normal list
    station_temp = list(np.ravel(results))

    return jsonify(station_data)  

@app.route("/api/v1.0/<start>")
def start():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query all stations
    start_date = session.query(measurement.date).order_by(measurement.date.asc()).first()

    low_temp = session.query(func.min(measurement.tobs)).filter(measurement.date >= start_date).all()
    high_temp = session.query(func.max(measurement.tobs)).filter(measurement.date >= start_date).all()
    avg_temp = session.query(func.avg(measurement.tobs)).filter(measurement.date >= start_date).all()

    session.close()

    # Convert list of tuples into normal list
    temp_dict = {}
    temp_dict["TMIN"] = low_temp[0][0]
    temp_dict["TAVG"] = round(avg_temp[0][0],1)
    temp_dict["TMAX"] = high_temp[0][0]

    return jsonify(temp_dict) 

@app.route("/api/v1.0/<start>/<end>")
def start_end():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query all stations
    start_date = session.query(measurement.date).order_by(measurement.date.asc()).first()
    last_date = session.query(measurement.date).order_by(measurement.date.desc()).first()

    low_temp = session.query(func.min(measurement.tobs)).\
        filter((measurement.date >= start_date),(measurement.date <= last_date)).all()
    high_temp = session.query(func.max(measurement.tobs)).\
        filter((measurement.date >= start_date),(measurement.date <= last_date)).all()
    avg_temp = session.query(func.avg(measurement.tobs)).\
        filter((measurement.date >= start_date),(measurement.date <= last_date)).all()

    session.close()

    # Convert list of tuples into normal list
    temp_dict = {}
    temp_dict["TMIN"] = low_temp[0][0]
    temp_dict["TAVG"] = round(avg_temp[0][0],1)
    temp_dict["TMAX"] = high_temp[0][0]

    return jsonify(temp_dict) 

if __name__ == '__main__':
    app.run(debug=True)
