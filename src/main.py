import sys
# caution: path[0] is reserved for script path (or '' in REPL)
sys.path.insert(1, '../../cpp/n2yo-satellite-api/cmake-build-release-with-pybindings')
import OrbitFetcher
import matplotlib
matplotlib.use('TkAgg')
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from cartopy.feature.nightshade import Nightshade
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from datetime import datetime
from Satellite import Satellite

# Create the figure and axis
plt.style.use('dark_background')
fig = plt.figure(figsize=(24, 16))
ax = fig.add_subplot(111, projection=ccrs.Robinson())

# Set up the map
ax.set_global()
ax.add_feature(cfeature.BORDERS, edgecolor='white', linewidth=0.5)
ax.stock_img()  # Blue marble-style background

# Read the config file
config = OrbitFetcher.Config()
ok = config.read("../../cpp/n2yo-satellite-api/config.txt")

if ok:
    dataReceiver = OrbitFetcher.DataReceiver(config)
    satellitesToPlot = []
    satPlotsToClear = []
    dayNightIndications = []
    date = datetime.now()
    TOTAL_TRACKABLE_SATELLITES = 80
    
    # Plot Observer position
    observer_lon = config.getConfigValues().observerLon
    observer_lat = config.getConfigValues().observerLat
    ax.plot(observer_lon, observer_lat, marker='*', color='orange', 
            markersize=8, transform=ccrs.PlateCarree())
    ax.text(observer_lon + 2, observer_lat + 1, "You are here", 
            transform=ccrs.PlateCarree())
    
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
    day_night = ax.add_feature(Nightshade(date, alpha=0.3))
    dayNightIndications.append(day_night)
    
    def update(frame):              
        # Remove the last drawn plot of each satellite
        for plot in satPlotsToClear:
            plot[0].remove()
            plot[1].remove()
        satPlotsToClear.clear()
        
        # Plot current position of each satellite and draw trajectory
        for sat in satellitesToPlot: 
            if sat.trajectoryEndPointUpdated:
                if sat.trajectoryLineSet:
                    sat.trajectoryLine.remove()
                
                trajectory = sat.getTrajectory()
                # Draw great circle trajectory
                sat.trajectoryLine = ax.plot(
                    [trajectory["startLon"], trajectory["endLon"]], 
                    [trajectory["startLat"], trajectory["endLat"]],
                    linewidth=2, 
                    color=sat.colour,
                    alpha=0.6,
                    transform=ccrs.Geodetic()
                )[0]
                sat.trajectoryLineSet = True
            
            pos = sat.getSatellitePosition()
            lon = pos["lon"]
            lat = pos["lat"]
            
            plot = ax.plot(lon, lat, marker='D', color=sat.colour, 
                          markersize=6, transform=ccrs.PlateCarree())[0]
            text = ax.text(lon + 2, lat + 1, sat.name, 
                          transform=ccrs.PlateCarree())
            satPlotsToClear.append((plot, text)) 
        
        # Update day/night cycle
        for cycle in dayNightIndications:
            cycle.remove()
        dayNightIndications.clear()
        
        date = datetime.now()
        day_night = ax.add_feature(Nightshade(date, alpha=0.3))
        dayNightIndications.append(day_night)
        
        ax.set_title("Satellite Tracker")
    
    ani = animation.FuncAnimation(
        fig,
        update,
        interval=1000,
        blit=False
    )
    
    plt.show()