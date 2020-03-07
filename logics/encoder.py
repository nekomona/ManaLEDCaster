from logics.utilcolor import ColorRGB

class SampledValue(object):
    def __init__(self, bitwidth = 0, value = 0):
        self.bitwidth = bitwidth
        self.value = value

    def __add__(self, rhs):
        return SampledValue(self.bitwidth + rhs.bitwidth, (self.value << rhs.bitwidth) + rhs.value)

    def __str__(self):
        return ("{0}'h{1:0" + str((self.bitwidth+7)//8) + "X}").format(self.bitwidth, self.value)

    def __repr__(self):
        return self.__str__()

    def toHex(self):
        return ("{:0" + str((self.bitwidth+7)//8) + "X}").format(self.value)

    def toCnum(self):
        return "0x" + self.toHex()

    def toCbytes(self):
        hstr = self.toHex()
        if len(hstr) & 0x01 != 0:
            hstr = "0" + hstr
        vals = ['0x'+hstr[i:i+2] for i in range(0, len(hstr), 2)]
        vals.reverse()
        return vals

class PixelEncoder(object):
	def __init__(self):
		self.bitwidth = 0
		
	def encode(self, value, **kwargs):
		return 0
	
	def encodeColor(self, value, **kwargs):
		return ColorRGB()

class BinaryEncoder(PixelEncoder):
	def __init__(self):
		self.bitwidth = 1
		
		self.threshold = ColorRGB()
		self.colorOn = ColorRGB()
		self.colorOff = ColorRGB()
	
	def encode(self, value, **kwargs):
		if value.r < self.threshold.r:
			return SampledValue(1, 0)
		if value.g < self.threshold.g:
			return SampledValue(1, 0)
		if value.b < self.threshold.b:
			return SampledValue(1, 0)
		return SampledValue(1, 1)
	
	def encodeColor(self, value, **kwargs):
		if value.r < self.threshold.r:
			return self.colorOff
		if value.g < self.threshold.g:
			return self.colorOff
		if value.b < self.threshold.b:
			return self.colorOff
		return self.colorOn

class RGB565Encoder(PixelEncoder):
	def __init__(self):
		self.bitwidth = 16
	
	def encode(self, value, **kwargs):
		return SampledValue(16, ((value.r & 0xF8) << 8) | ((value.g & 0xFC) << 3) | ((value.b & 0xF8) >> 2))
	
	def encodeColor(self, value, **kwargs):
		mval = ColorRGB()
		mval.r = value.r & 0xF8
		mval.g = value.g & 0xFC
		mval.b = value.b & 0xF8
		return mval

class RGB888Encoder(PixelEncoder):
	def __init__(self):
		self.bitwidth = 24
	
	def encode(self, value, **kwargs):
		return SampledValue(24, (value.r << 16) | (value.g << 8) | (value.b) )
	
	def encodeColor(self, value, **kwargs):
		return value


encoderList = [
    "Binary",
    "RGB565",
    "RGB888"
]

class EncoderFactory(object):
    @staticmethod
    def buildEncoder(ind):
        if ind == 0:
            return BinaryEncoder()
        elif ind == 1:
            return RGB565Encoder()
        elif ind == 2:
            return RGB888Encoder()
        else:
            return None
    
    @staticmethod
    def searchEncoder(enc):
        if isinstance(enc, BinaryEncoder):
            return 0
        elif isinstance(enc, RGB565Encoder):
            return 1
        elif isinstance(enc, RGB888Encoder):
            return 2
        else:
            return -1