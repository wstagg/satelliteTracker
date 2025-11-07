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

# Create the figure and axis FIRST
fig = plt.figure(figsize=(24, 16))
ax = fig.add_subplot(111)

# Create basemap
m = Basemap(projection='robin', lon_0=0, resolution='c', ax=ax)
#m.drawcoastlines()
#m.fillcontinents(color='coral', lake_color='aqua')
#m.drawparallels(np.arange(-90., 120., 30.))
#m.drawmeridians(np.arange(0., 360., 60.))
m.drawmapboundary(fill_color='aqua')
m.bluemarble()
m.drawcountries()


config = n2yoSatelliteApi.Config()

ok = config.read("../../cpp/n2yo-satellite-api/config.txt")

if ok:

    dataReceiver = n2yoSatelliteApi.DataReceiver(config)
    tle = dataReceiver.getTle()

    satName = tle.satName
    sat_positions = []
    sat_positions_to_clear = []
    sat_orbit_lines = []
    day_night_indications = []


    
    def update(frame):            
        
        # if no satellite positions left to plot, get more
        if len(sat_positions) == 0:
            satellitePosition = dataReceiver.getSatellitePosition()
            for pos in satellitePosition.positionData:
                sat_positions.append(pos)
            
            # draw upcoming trajectory 
            orbit_line = m.drawgreatcircle(sat_positions[0].lon, 
                                           sat_positions[0].lat, 
                                           sat_positions[len(sat_positions) - 1].lon, 
                                           sat_positions[len(sat_positions) - 1].lat, 
                                           linewidth=2,
                                           color='r')
            
            sat_orbit_lines.append(orbit_line)

            if len(sat_orbit_lines) > 1:
                sat_orbit_lines[len(sat_orbit_lines) - 2][0].set_color("green")

            if len(sat_orbit_lines) > 40:
                sat_orbit_lines[0][0].remove()
                del sat_orbit_lines[0]
            

            # update day/night indication
            #TODO fix
            # if len(day_night_indications):
            #     day_night_indications[0][0].remove()
            #     del day_night_indications
                
                
            # date = datetime.now()
            # day_night = m.nightshade(date)
            # day_night_indications.append(day_night)
            


        # remove the last drawn plot
        if len(sat_positions_to_clear) > 0:
            for plot in sat_positions_to_clear:
                plot[0].remove()
            del sat_positions_to_clear[0]

        # plot the next satellite position
        if len(sat_positions) > 0:
            # create the plot for the satellite position
            xpt, ypt = m(sat_positions[0].lon, sat_positions[0].lat)
            # delete the position from the positions to plot
            del sat_positions[0]

            plot = m.plot(xpt, ypt, 'rD', markersize = 6)
            sat_positions_to_clear.append(plot) 

            
    plt.title(satName + " TRACKER")

    ani = animation.FuncAnimation(
    fig,
    update,
    # init_func=init,
    interval=1000,
    blit=False)

    plt.show()