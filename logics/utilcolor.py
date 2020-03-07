import numpy as np

class ColorRGB(object):
	def __init__(self, val = np.array([0, 0, 0])):
		self.val = val
	
	@classmethod
	def fromint(cls, color):
		v = np.array([(color >> 16) & 0xFF, (color >> 8) & 0xFF, (color) & 0xFF])
		return cls(v)
	
	@property
	def r(self):
		return self.val[0]
	
	@r.setter
	def r(self, v):
		self.val[0] = v
	
	@property
	def g(self):
		return self.val[1]
	
	@g.setter
	def g(self, v):
		self.val[1] = v
	
	@property
	def b(self):
		return self.val[2]
	
	@b.setter
	def b(self, v):
		self.val[2] = v
	
	