from pymote.algorithm import NetworkAlgorithm


class ReadSensors(NetworkAlgorithm):

    """Read all sensors and save data in memory for latter usage."""
    
    def run(self):
        if not hasattr(self, 'sensorReadingsKey'):
            self.sensorReadingsKey = 'sensorReadings'
        for node in self.network.nodes():
            node.memory.update({self.sensorReadingsKey:
                                node.compositeSensor.read()})
