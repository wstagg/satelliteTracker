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

# Create the figure and axis FIRST
fig = plt.figure(figsize=(24, 16))
ax = fig.add_subplot(111)

# Create basemap
m = Basemap(projection='robin', lon_0=0, resolution='c', ax=ax)
#m.drawcoastlines()
#m.fillcontinents(color='coral', lake_color='aqua')
#m.drawparallels(np.arange(-90., 120., 30.))
#m.drawmeridians(np.arange(0., 360., 60.))
#m.drawmapboundary(fill_color='aqua')
m.bluemarble()
m.drawcountries()


config = n2yoSatelliteApi.Config()

ok = config.read("../../cpp/n2yo-satellite-api/config.txt")

if ok:

    dataReceiver = n2yoSatelliteApi.DataReceiver(config)
    tle = dataReceiver.getTle()

    satName = tle.satName
    sat_data = []
    sat_positions = []
    sat_positions_to_clear = []
    sat_data.append(sat_positions)
    sat_data.append(sat_positions_to_clear)

    
    def update(frame):            
        # if no satellite positions left to plot, get more
        if len(sat_data[0]) == 0:
            satellitePosition = dataReceiver.getSatellitePosition()
            sat_data[0] = satellitePosition.positionData
            print(f"num of positions {len(sat_data[0])}")

        # remove the last drawn plot
        if len(sat_data[1]) > 0:
            for plot in sat_data[1]:
                plot[0].remove()
            del sat_data[1][0]

        if len(sat_data[0]) > 0:
            # create the plot for the satellite position
            xpt, ypt = m(sat_data[0][0].lon, sat_data[0][0].lat)
            # delete the position from the positions to plot
            del sat_data[0][0]

            plot = m.plot(xpt, ypt, 'ro', markersize = 6)
            sat_data[1].append(plot) 

            
    plt.title(satName + " TRACKER")

    ani = animation.FuncAnimation(
    fig,
    update,
    # init_func=init,
    interval=1000,
    blit=False)

    plt.show()