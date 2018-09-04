
# coding: utf-8

# In[ ]:


import numpy as np
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, and_

from flask import Flask, jsonify


dates = [
    {"start": "2017-02-01", "end": "2017-02-28"},
    {"start": "2017-06-01", "end": ""}
]



app = Flask(__name__)


@app.route("/")
def home():
    print("Server received request for 'Home' page...")
    return (
        "<h1>Step 4: Climate App</h1><br/>"
        "Menu:<br/>"
        "<a href='/'>Home</a><br/>"
        "<a href='/api/v1.0/precipitation'>Precipitation</a> - /api/v1.0/precipitation<br/>"
        "<a href='/api/v1.0/stations'>Stations</a> - /api/v1.0/stations<br/>"
        "<a href='/api/v1.0/tobs'>Temperature Observations</a> - /api/v1.0/tobs<br/>"
        "<a href='/api/v1.0/2017-06-01'>Start Date Only</a><br/>"
        "<a href='/api/v1.0/2017-03-01/2017-05-31'>Start Date and End Date</a><br/>"
    )
@app.route("/api/v1.0/precipitation")
def precip():
    print("Server received request for 'Precipitation' page...")
    
####Database connection
    engine = create_engine('sqlite:///Resources/hawaii.sqlite')
    Base = automap_base()
    Base.prepare(engine, reflect=True)
    Measurement = Base.classes.measurements
    session = Session(bind=engine)

####Find last date in the database
    lastDate = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
####NOTE: Above line prints to ('2017-8-23').  Having issues coverting to a format where I use dt.date function used in next line.
    prevYearPrcp = dt.date(2017,8,23) - dt.timedelta(days=365)  
    results = session.query(Measurement.date, Measurement.prcp).filter(func.strftime("%Y-%m-%d", Measurement.date) > prevYearPrcp).order_by(Measurement.date).all()

####Put the results of the query into a list and then use jsoonify to return the output
    prpcResults = []
    for prcpRecord in results:
        prcp_dict = {}
        #prcp_dict["Date"] = prcpRecord.date
        #prcp_dict["Precipitation"] = prcpRecord.prcp
        prcp_dict[prcpRecord.date] = prcpRecord.prcp
        prpcResults.append(prcp_dict)
    
    return jsonify(prpcResults)
    

@app.route("/api/v1.0/stations")
def stations():    
    print("Server received request for 'Stations' page...")

####Database connection
    engine = create_engine('sqlite:///Resources/hawaii.sqlite')
    Base = automap_base()
    Base.prepare(engine, reflect=True)
    Station = Base.classes.stations
    session = Session(bind=engine)
    
    ####  The way the instructions read is to only a list of stations.  The two lines below line generate ONLY the station
    ####  column in the list.  To me this wasn't useful.  Decided to code this section to pull ALL data from the station table.
    #     allStations = session.query(Station.station).all()
    #     lstStations = list(np.ravel(allStations))

    allStations = session.query(Station).all()
    lstStations = []
    for station in allStations:
        station_dict = {}
        station_dict['station'] = station.station
        station_dict['name'] = station.name
        station_dict['lat'] = station.latitude
        station_dict['lng'] = station.longitude
        station_dict['elevation'] = station.elevation
        lstStations.append(station_dict)
    
    return jsonify(lstStations)

@app.route("/api/v1.0/tobs")
def tobs():    
    print("Server received request for 'Temperatures Observation' page...")

####Database connection
    engine = create_engine('sqlite:///Resources/hawaii.sqlite')
    Base = automap_base()
    Base.prepare(engine, reflect=True)
    Measurement = Base.classes.measurements
    session = Session(bind=engine)   
    
    ####Find last date in the database
    lastDate = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
####NOTE: Above line prints to ('2017-8-23').  Having issues coverting to a format where I use dt.date function used in next line.
    prevYearTemp = dt.date(2017,8,23) - dt.timedelta(days=365)  
    results = session.query(Measurement.date, Measurement.tobs).filter(func.strftime("%Y-%m-%d", Measurement.date) > prevYearTemp).order_by(Measurement.date).all()

    
    ####Put the results of the query into a list and then use jsonify to return the output
    tobsResults = []
    for tobsRecord in results:
        prcp_dict = {}
        #prcp_dict["Date"] = prcpRecord.date
        #prcp_dict["Precipitation"] = prcpRecord.prcp
        prcp_dict[tobsRecord.date] = tobsRecord.tobs
        tobsResults.append(prcp_dict)
    
    return jsonify(tobsResults)

@app.route("/api/v1.0/<start>")
def start(start):
    print("Server received request for 'Start Date' page...")

####Database connection
    engine = create_engine('sqlite:///Resources/hawaii.sqlite')
    Base = automap_base()
    Base.prepare(engine, reflect=True)
    Measurement = Base.classes.measurements
    session = Session(bind=engine)
    
    results = session.query(Measurement.date, func.avg(Measurement.tobs).label("tavg"), 
    func.min(Measurement.tobs).label("tmin"), func.max(Measurement.tobs).label("tmax")).\
    group_by(Measurement.date).\
    order_by(Measurement.date).\
    filter(func.strftime("%Y-%m-%d", Measurement.date) >= start).all()
    
    dateResults = []
    for date in results:
        date_dict = {}
        date_dict["Date"] =  date.date
        date_dict["TAVG"] = date.tavg
        date_dict["TMIN"] = date.tmin
        date_dict["TMAX"] = date.tmax
        dateResults.append(date_dict)

    return jsonify(dateResults)
    
@app.route("/api/v1.0/<start>/<end>")
def startend(start, end):
    print("Server received request for 'Start/End' page...")

####Database connection
    engine = create_engine('sqlite:///Resources/hawaii.sqlite')
    Base = automap_base()
    Base.prepare(engine, reflect=True)
    Measurement = Base.classes.measurements
    session = Session(bind=engine)

    results = session.query(Measurement.date, func.avg(Measurement.tobs).label("tavg"), 
    func.min(Measurement.tobs).label("tmin"), func.max(Measurement.tobs).label("tmax")).\
    group_by(Measurement.date).\
    order_by(Measurement.date).\
    filter(and_(func.strftime("%Y-%m-%d", Measurement.date) >= start, func.strftime("%Y-%m-%d", Measurement.date) <= end)).all()
    
    dateResults = []
    for date in results:
        date_dict = {}
        date_dict["Date"] =  date.date
        date_dict["TAVG"] = date.tavg
        date_dict["TMIN"] = date.tmin
        date_dict["TMAX"] = date.tmax
        dateResults.append(date_dict)

    return jsonify(dateResults)

if __name__ == "__main__":
    app.run(debug=True)

