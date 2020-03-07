class Property(object):
    def __init__(self, typename = "", name = "", readonly = False):
        self.type = typename
        self.name = name
        self.readonly = readonly
     
    def __str__(self):
        return f"{self.name} of {self.type} r/o {self.reandonly}"
    
    def __repr__(self):
        return "Property(" + self.__str__() + ")"


class PropertyContainer(object):
    def __init__(self):
        self.activeTreeLine = None
        self.activeNode = None

#self.property['offPos'] = Property("Pos2D", "Offset Position")
#self.property['encoder'] = Property('Encoder', 'Encoder')
#self.property['sampleShape'] = Property('Shape', 'Sampling Shape')
#self.property['pixelWidth'] = property('Int', 'Pixel Width')
#self.property['sampleHeight'] = property('Real', 'Sampling Height')



