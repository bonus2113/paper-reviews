import numpy as np
import cv2

class SigmaDelta:
	def __init__(self, width, height, firstFrame, n):
		self.width = width
		self.height = height
		self.mt = firstFrame
		self.ot = np.zeros((width, height))
		self.vt = np.zeros((width, height))
		self.n = n
		
	def apply(self, frame):
		ltMask = self.mt < frame
		gtMask = self.mt > frame
		totalMask = ltMask + gtMask * -1
		self.mt = (self.mt + totalMask).astype('uint8')
		self.ot = cv2.absdiff(self.mt, frame)
		
		ltMask = self.vt < self.n * self.ot
		gtMask = self.vt > self.n * self.ot
		totalMask = ltMask + gtMask * -1
		self.vt = np.clip(self.vt + totalMask, 2, 255).astype('uint8')
		
		return ((self.ot > self.vt) * 255).astype('uint8')
		
class ConditionalSigmaDelta:
	def __init__(self, width, height, firstFrame, n):
		self.width = width
		self.height = height
		self.mt = firstFrame
		self.zeros = np.zeros((width, height))
		self.ot = self.zeros
		self.vt = self.zeros
		self.et = np.ones((width, height))
		self.n = n
		
	def apply(self, frame):
		ltMask = self.mt < frame
		gtMask = self.mt > frame
		totalMask = ltMask + gtMask * -1
		totalMask *= self.et != self.zeros
		
		self.mt = (self.mt + totalMask).astype('uint8')
		self.ot = cv2.absdiff(self.mt, frame)
		
		ltMask = self.vt < self.n * self.ot
		gtMask = self.vt > self.n * self.ot
		totalMask = ltMask + gtMask * -1
		self.vt = np.clip(self.vt + totalMask, 2, 255).astype('uint8')
		self.et = ((self.ot > self.vt) * 255).astype('uint8')
		return self.et

def readGray(cap):
	ret, frame = cap.read()
	if not ret:
		return ret, frame
	
	return ret, cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

def main():
	cap = cv2.VideoCapture(0)
	
	width = cap.get(4)
	height = cap.get(3)
	
	print width
	print height
	
	ret, frame = readGray(cap)
	sigmaDelta = ConditionalSigmaDelta(width, height, frame, 5)
	
	while(1):
		ret, frame = readGray(cap)
		if not ret:
			print "Reading frame failed!"
			break
		
		mask = sigmaDelta.apply(frame)
		
		cv2.imshow('frame',mask)
		k = cv2.waitKey(30) & 0xff
		if k == 27:
			break

	cap.release()
	cv2.destroyAllWindows()
	
if __name__ == "__main__":
	main()