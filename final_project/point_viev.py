class OsmPoint:
    def __init__(self, latitude: float, longitude: float, link: int = -1):
        self.link = link
        self.latitude = latitude
        self.longitude = longitude
