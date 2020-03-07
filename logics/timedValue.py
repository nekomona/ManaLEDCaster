import globals
import threading
import bisect

def binary_search(arr, x, lo=0, hi=None):
    hi = hi if hi is not None else len(arr)
    pos = bisect.bisect_left(arr, x, lo, hi)
    return pos if pos != hi and arr[pos] == x else -1

class TimedValue(object):
    def __init__(self):
        pass

    def resetFrameLimit(self):
        pass

    def getValue(self, frame):
        pass

    def setValue(self, frame, value):
        pass
    
    def clearValue(self, frame):
        pass

class TimedInterpolatableValue(TimedValue):
    def __init__(self):
        self.keyframes = []
        self.values = {}

        self.wrlock = threading.Lock()

    def resetFrameLimit(self):
        pass

    def getValue(self, frame):
        pass

    def setValue(self, frame, value):
        with self.wrlock:
            iind = bisect.bisect_left(self.keyframes, frame)
            if iind >= len(self.keyframes) or self.keyframes[iind] != frame:
                self.keyframes.insert(iind, frame)
            self.values[frame] = value

    def clearValue(self, frame):
        with self.wrlock:
            iind = bisect.bisect_left(self.keyframes, frame)
            if iind < len(self.keyframes) and self.keyframes[iind] == frame:
                self.keyframes.pop(iind)
                self.values.pop(frame)

class TimedDiscreteValue(TimedValue):
    def __init__(self):
        if globals.frameLength:
            self.values = [None] * globals.frameLength
        
    def resetFrameLimit(self):
        if globals.frameLength:
            if globals.frameLength > len(self.values):
                self.values.extend( [None]*(globals.frameLength - len(self.values)) )
            elif globals.frameLength < len(self.values):
                self.values = self.values[:globals.frameLength]

    def getValue(self, frame):
        return self.values[frame]

    def setValue(self, frame, value):
        self.values[frame] = value

    def clearValue(self, frame):
        self.values[frame] = None

class TimedSampledPoint(TimedDiscreteValue):
    def __init__(self):
        pass

    def resetFrameLimit(self):
        pass

    def getValue(self, frame):
        pass

class TimedSampleArea(TimedDiscreteValue):
    def __init__(self):
        pass

    def resetFrameLimit(self):
        pass

    def getValue(self, frame):
        pass