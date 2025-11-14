import sys
# caution: path[0] is reserved for script path (or '' in REPL)
sys.path.insert(1, '../../cpp/n2yo-satellite-api/cmake-build-release')
import n2yoSatelliteApi

import matplotlib
matplotlib.use('TkAgg') # Set interactive backend first
from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from datetime import datetime
from Satellite import Satellite

# Create the figure and axis FIRST
plt.style.use('dark_background')
fig = plt.figure(figsize=(24, 16))
ax = fig.add_subplot(111)

# Create basemap
map = Basemap(projection='robin', lon_0=0, resolution='c', ax=ax)
map.drawmapboundary(fill_color='aqua')
map.bluemarble()
map.drawcountries()

# Read the config file for the 2yo-satellite-api
config = n2yoSatelliteApi.Config()
ok = config.read("../../cpp/n2yo-satellite-api/config.txt")

if ok:
    dataReceiver = n2yoSatelliteApi.DataReceiver(config)
    satellitesToPlot = []
    satPlotsToClear = []
    dayNightIndications = []
    date = datetime.now()
    TOTAL_TRACKABLE_SATELLITES = 80
    
    # Plot Observer position
    lxpt, lypt = map(config.getConfigValues().observerLon, config.getConfigValues().observerLat)
    map.plot(lxpt, lypt, marker = '*', color = "orange", markersize = 8)
    plt.text(lxpt + 20000, lypt + 10000, "You are here")

    # Track some random satellites that pass over
    satellites = dataReceiver.getSatellitesAbove()
    print("Getting satellites above...")
    for sat in satellites.satellitesAbove:
        print(f"sat id {sat.satId} sat name {sat.satName}")
        satellite = Satellite(sat.satId, sat.satName, config)
        if len(satellitesToPlot) <= TOTAL_TRACKABLE_SATELLITES:
            satellitesToPlot.append(satellite)
        else:
            break
    
    # Track the ISS
    ISS = Satellite(25544, "ISS", config)
    satellitesToPlot.append(ISS)

    # Set initial day/night cycle
    day_night = map.nightshade(date)
    dayNightIndications.append(day_night)
 
    def update(frame):              
        # remove the last drawn plot of each satellite
        for plot in satPlotsToClear:
            plot[0][0].remove()
            plot[1].remove()
        satPlotsToClear.clear()
        
        # plot current position of each satellite and draw trajectory
        for sat in satellitesToPlot: 
            if sat.trajectoryEndPointUpdated:
                if sat.trajectoryLineSet:
                    sat.trajectoryLine[0].remove()
                
                trajectory = sat.getTrajectory()
                sat.trajectoryLine = map.drawgreatcircle(trajectory["startLon"], 
                                    trajectory["startLat"], 
                                    trajectory["endLon"], 
                                    trajectory["endLat"],
                                    del_s=1,
                                    linewidth=2, 
                                    color='green')
                sat.trajectoryLineSet = True
                              
            pos = sat.getSatellitePosition()
            lon = pos["lon"]
            lat = pos["lat"]
            xpt, ypt = map(lon, lat)
            plot = map.plot(xpt, ypt, 'rD', markersize = 6)
            text = plt.text(xpt + 20000, ypt + 10000, sat.name)

            satPlotsToClear.append((plot, text)) 

        # update day/night cycle
        for cycle in dayNightIndications:
            cycle.remove()
        del dayNightIndications[0]
               
        date = datetime.now()
        day_night = map.nightshade(date)
        dayNightIndications.append(day_night)
  
    
    plt.title("Satellite Tracker")
    ani = animation.FuncAnimation(
    fig,
    update,
    #init_func=init,
    interval=1000,
    blit=False)

    plt.show()