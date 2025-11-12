import sys
# caution: path[0] is reserved for script path (or '' in REPL)
sys.path.insert(1, '../../cpp/n2yo-satellite-api/cmake-build-release')
import n2yoSatelliteApi

import matplotlib
matplotlib.use('TkAgg') # Set interactive backend first
from mpl_toolkits.basemap import Basemap
import numpy as np
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
#map.drawcoastlines()
#map.fillcontinents(color='coral', lake_color='aqua')
#map.drawparallels(np.arange(-90., 120., 30.))
#map.drawmeridians(np.arange(0., 360., 60.))
map.drawmapboundary(fill_color='aqua')
map.bluemarble()
map.drawcountries()


config = n2yoSatelliteApi.Config()

ok = config.read("../../cpp/n2yo-satellite-api/config.txt")

if ok:
    dataReceiver = n2yoSatelliteApi.DataReceiver(config)

    satellitesToPlot = []
    sat_positions_to_clear = []
    sat_orbit_lines = []
    day_night_indications = []
    date = datetime.now()


    satellites = dataReceiver.getSatellitesAbove()
    print("Getting satellites above...")
    for sat in satellites.satellitesAbove:
        print(f"sat id {sat.satId} sat name {sat.satName}")
        satellite = Satellite(sat.satId, sat.satName, config)
        satellitesToPlot.append(satellite)

    day_night = map.nightshade(date)
    day_night_indications.append(day_night)

    # def init():
    #     satellites = dataReceiver.getSatellitesAbove()

    #     for sat in satellites.satellitesAbove:
    #         print(f"sat id {sat.satId} sat name {sat.satName}")
    #         satellite = Satellite(sat.satId, sat.satName, config)
    #         satellitesToPlot.append(satellite)

    #     day_night = map.nightshade(date)
    #     day_night_indications.append(day_night)

    
    def update(frame):            
            
        # remove the last drawn plot of each satellite
        if len(sat_positions_to_clear) > 0:
            for plot in sat_positions_to_clear:
                plot[0].remove()
            sat_positions_to_clear.clear()
        
        # plot current position of each satellite
        for sat in satellitesToPlot:
            print(f"plotting sat name {sat.name}")
            pos = sat.getSatellitePosition()
            lon = pos["lon"]
            lat = pos["lat"]
            xpt, ypt = map(lon, lat)
            plot = map.plot(xpt, ypt, 'rD', markersize = 6)
            sat_positions_to_clear.append(plot) 

        # update day/night cycle
        if len(day_night_indications) != 0:
            for cycle in day_night_indications:
                cycle.remove()
            del day_night_indications[0]
               
        date = datetime.now()
        day_night = map.nightshade(date)
        day_night_indications.append(day_night)
  
    plt.title("Satellite Tracker")

    ani = animation.FuncAnimation(
    fig,
    update,
    #init_func=init,
    interval=1000,
    blit=False)

    plt.show()