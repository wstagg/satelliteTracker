import sys
# caution: path[0] is reserved for script path (or '' in REPL)
sys.path.insert(1, '../../cpp/n2yo-satellite-api/cmake-build-release')
import n2yoSatelliteApi


class Satellite:
    def __init__(self,_noradId, _satName, _config):
        self.noradId = _noradId
        self.name = _satName
        self.config = _config
        self.dataReceiver = n2yoSatelliteApi.DataReceiver(_config)
        self.satPositions = []
        self.updateSatellitePositions()

    def updateSatellitePositions(self):
        satellitePosition = self.dataReceiver.getSatellitePosition(
             self.config.getConfigValues().apiKey,
             self.noradId,
             self.config.getConfigValues().observerLat,
             self.config.getConfigValues().observerLon,
             self.config.getConfigValues().observerAlt,
             self.config.getConfigValues().seconds)
        
        for pos in satellitePosition.positionData:
                self.satPositions.append(pos)

    def getSatellitePosition(self):
        if len(self.satPositions) == 0:
            self.updateSatellitePositions()
        if len(self.satPositions) > 0:
            pos = {"lat": self.satPositions[0].lat, "lon": self.satPositions[0].lon }
            del self.satPositions[0]
            return pos
              
         
         




    

        