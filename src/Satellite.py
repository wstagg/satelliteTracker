import OrbitFetcher
import numpy as np


MAX_TRAJECTORY_ENDPOINT_UPDATES = 30

class Satellite:
    def __init__(self,_noradId, _satName, _config):
        self.noradId = _noradId
        self.name = _satName
        self.config = _config
        self.dataReceiver = OrbitFetcher.DataReceiver(_config)
        self.satPositions = []
        self.trajectory = {"startLat": 0.0, "startLon": 0.0, "endLat": 0.0, "endLon": 0.0}
        self.trajectoryLineSet = False
        self.trajectoryEndPointUpdateCount = 0
        self.colour = tuple(np.random.random(size=3))
        self.updateSatellitePositions()
        self.setTrajectoryStartPoint(self.satPositions[0].lat, self.satPositions[0].lon)

    def updateSatellitePositions(self):
        print(f"getting positions for {self.noradId} : {self.name}")
        satellitePosition = self.dataReceiver.getSatellitePosition(
             self.config.getConfigValues().apiKey,
             self.noradId,
             self.config.getConfigValues().observerLat,
             self.config.getConfigValues().observerLon,
             self.config.getConfigValues().observerAlt,
             self.config.getConfigValues().seconds)
        
        for pos in satellitePosition.positionData:
                self.satPositions.append(pos)
        
        if len(self.satPositions) > 2:

            if self.trajectoryEndPointUpdateCount >= MAX_TRAJECTORY_ENDPOINT_UPDATES:
                self.setTrajectoryStartPoint(self.satPositions[0].lat, self.satPositions[0].lon)
                self.trajectoryEndPointUpdateCount = 0
            
            self.updateTrajectoryEndPoint(self.satPositions[len(self.satPositions) -1 ].lat, 
                                    self.satPositions[len(self.satPositions) -1 ].lon)

    def getSatellitePosition(self):
        if len(self.satPositions) == 0:
            self.updateSatellitePositions()
        if len(self.satPositions) > 0:
            pos = {"lat": self.satPositions[0].lat, "lon": self.satPositions[0].lon }
            del self.satPositions[0]
            return pos
        
    def setTrajectoryStartPoint(self, startLat, startLon):
        self.trajectory["startLat"] = startLat
        self.trajectory["startLon"] = startLon
    
    def updateTrajectoryEndPoint(self, endLat, endLon):
        self.trajectory["endLat"] = endLat
        self.trajectory["endLon"] = endLon
        self.trajectoryEndPointUpdated = True
        self.trajectoryEndPointUpdateCount +=1
    
    def getTrajectory(self):
        self.trajectoryEndPointUpdated = False
        return self.trajectory
         
         




    

        