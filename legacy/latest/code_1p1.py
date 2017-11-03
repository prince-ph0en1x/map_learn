## Code to generate hex tile probability

## \date: 21-10-2017
## \author: Aritra Sarkar (prince-ph0en1x)

'''

Version Plan:

* Denote obstacles as place cell of type 0
* Seperate matrix representing annotations for place cells (objects of interest in specific context)
> Episodic memory where overlaps in place cells over time forms grid cells (semantic memory)
* Find A* path from annoted current location (at map mid for rotation simplicity) to target
* Case 1: In rotated map (about current location) find angle of min SSG, rotate previous path to get new path
* Case 2: Add/remove obstacles on original path in warehouse map, compare how many changes tolerable where small path change (D* lite) advantagious over recalculaing A*
* 

'''

# commandline help: python3 code_1p1.py

from graphics import *
import math
import random
from PIL import Image
import re
import timeit

sz = 600	# Arbitarily chosen constant
pno = 3		# Project number

'''	~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ @$ ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''

# Take an image of any size > 600x600, scale and save black-white greyscale threshold image.
def bwscaledMap(fname, trshld):
	
	imgfile = Image.open("images/"+str(fname))
	rgbfile = imgfile.convert('RGB')

	win = GraphWin("Print Map", sz, sz)

	xscale = imgfile.size[0]/sz
	yscale = imgfile.size[1]/sz
	for ypix in range (0,imgfile.size[1],yscale):
		for xpix in range (0,imgfile.size[0],xscale):
			pt = Point(xpix/xscale,ypix/yscale)
			rr = 0
			gg = 0
			bb = 0
			for yypix in range (0,yscale,1):
				for xxpix in range (0,xscale,1):
					c1, c2, c3 = rgbfile.getpixel((xpix,ypix))
					rr = rr + c1
					gg = gg + c2
					bb = bb + c3
			rr = rr / (xscale*yscale)
			gg = gg / (xscale*yscale)
			bb = bb / (xscale*yscale)
			if (rr > trshld and gg > trshld and bb > trshld):
				pt.setOutline("white")
			else:
				pt.setOutline("black")
			pt.draw(win)

	win.getMouse() # pause for click in window
	
	win.postscript(file = "temp.eps", pageheight = sz-1, pagewidth = sz-1)
	epsimg = Image.open("temp.eps")
	epsimg.save("images/world00"+str(pno)+"_bw.png","png")
	win.close()

'''	~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ @$ ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''

# Take output image from bwscaledMap and render red-blue map inside circle
def drawMap(fname):
	
	imgfile = Image.open("images/"+str(fname))
	rgbfile = imgfile.convert('RGB')

	win = GraphWin("Print Map", sz, sz)

	#	https://stackoverflow.com/questions/13537483/when-saving-turtle-graphics-to-an-eps-file-the-background-color-shows-on-the-s
	rr = Rectangle(Point(0,0), Point(sz,sz))	
	rr.setOutline("white")
	rr.setFill("white")
	rr.draw(win)
	
	cc = Circle(Point(sz/2,sz/2), sz/2)
	cc.setOutline("red")
	cc.setFill("red")
	cc.draw(win)
	
	scale = math.sqrt(2)
	ypix = 0
	while (ypix < imgfile.size[1]):
		xpix = 0
		while (xpix < imgfile.size[0]):
			c1, c2, c3 = rgbfile.getpixel((xpix,ypix))
			if (c1 < 250):
				pt = Point((xpix-sz/2)/scale+sz/2,(ypix-sz/2)/scale+sz/2)
				pt.setOutline("blue")
				pt.draw(win)
			xpix = xpix + scale
		ypix = ypix + scale
	
	win.postscript(file = "temp.eps", pageheight = sz-1, pagewidth = sz-1)
	epsimg = Image.open("temp.eps")
	epsimg.save("images/world00"+str(pno)+"_0.png","png")
	win.close()

'''	~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ @$ ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''

# Take output image from drawMap and render rotated version
def turnMap(ang):

	# TODO : Merge with drawmap

	win = GraphWin("Print Map", sz, sz)

	imgfile = Image.open("images/world00"+str(pno)+"_0.png")
	rgbfile = imgfile.convert('RGB')
	
	rr = Rectangle(Point(0,0), Point(sz,sz))
	rr.setOutline("white")
	rr.setFill("white")
	rr.draw(win)

	xrotc = sz/2
	yrotc = sz/2
	arot = ang*math.pi/180
	
	# start = timeit.timeit()
	for ypix in range (0,imgfile.size[1]):
		for xpix in range (0,imgfile.size[0]):
			c1, c2, c3 = rgbfile.getpixel((xpix,ypix))
			xxx = xpix - xrotc
			yyy = ypix - yrotc			
			xnew = +yyy * math.sin(arot) + xxx * math.cos(arot)	# 3 shear rotation no used as problem with 180 deg - tan(90)
			ynew = +yyy * math.cos(arot) - xxx * math.sin(arot)
			p1 = Point(xnew + xrotc,ynew + yrotc)
			p1.setOutline(color_rgb(c1,c2,c3))
			p1.draw(win)
	# end = timeit.timeit()
	# print end - start
			
	win.postscript(file = "temp.eps", pageheight = sz-1, pagewidth = sz-1)
	epsimg = Image.open("temp.eps")
	epsimg.save("images/world00"+str(pno)+"_"+str(ang)+".png","png")
	win.close()

'''	~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ @$ ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''

# Generate Hex grid image of input map from drawMap/turnMap
def hexprob(d,fname):
	
	# d = vertex to vertex distance of hex
	
	# TODO: Update to hex prob in hex grid, not circle

	imgfile = Image.open("images/world00"+str(pno)+"_"+str(fname)+".png")
	rgbfile = imgfile.convert('RGB')
	
	file = open("world003_"+str(fname)+"_"+str(d)+".txt","w")
	
	win = GraphWin("Print Map", sz, sz)
	rad = d/2 	#	d/(2*math.cos(30*2*math.pi/360))
	xmax = int(math.ceil(imgfile.size[0]/d))+1
	ymax = int(math.ceil(imgfile.size[1]/(d*math.sqrt(3)/2)))+1
	print(math.sqrt(3)/2)
	for ys in range (0,ymax):
		for xs in range (-xmax,xmax):
			xc = (xs + float(ys)/2)*d
			yc = (ys*math.sqrt(3)/2)*d
			if (xc >= 0 and xc <= sz and yc >= 0 and yc <= sz):	# Elements hex outside draw area
				ptot = 0
				pblu = 0
				for ypix in range (int(yc-rad),int(yc+rad)):	# change from square grid to hex grid
					for xpix in range (int(xc-rad),int(xc+rad)):
						if (xpix >= 0 and xpix < sz and ypix >= 0 and ypix < sz):
							ptot = ptot + 1
							c1, c2, c3 = rgbfile.getpixel((xpix,ypix))
							if (c1 == 255):
								pblu = pblu + 1
				prob = float(pblu)/ptot
				file.write(str(xs)+","+str(ys)+","+str(prob)+"\n")
				cc = Circle(Point(xc,yc), rad)
				cc.setOutline(color_rgb(int(prob*255),int(prob*255),255))
				cc.setFill(color_rgb(int(prob*255),int(prob*255),255))
				cc.draw(win)		
	
	file.close()
	win.postscript(file = "temp.eps", pageheight = sz-1, pagewidth = sz-1)
	epsimg = Image.open("temp.eps")
	epsimg.save("images/world00"+str(pno)+"_"+str(fname)+"_"+str(d)+"h.png","png")
	win.close()
	return

'''	~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ @$ ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''

# From output of hexprob text file, generate border cells
def hexBorder(d,fname):

	# d = vertex to vertex distance of hex

	file = open("world00"+str(pno)+"_"+str(fname)+"_"+str(d)+".txt","r")
	
	win = GraphWin("Print Map", sz, sz)
	gap = 1		# gap between hex boundaries
	hxvl1 = []
	lno = 0
	for line in file:
		hxvl1.append([])
		hxvl1[lno].extend(list(map(float,re.findall('-?[0-9|\'.\']+', line))))	# Lambda expression on Regex
		lno = lno + 1

	arot = (fname+30)*math.pi/180	# edge aligned form of hex
	agtori = 0
	hxr = d/2 - gap 		# hex radius
	for i in range(len(hxvl1)):
		xc = (hxvl1[i][0] + float(hxvl1[i][1])/2)*d
		yc = (hxvl1[i][1]*math.sqrt(3)/2)*d
		for ang in range (0,6):
			a1 = (math.pi/3+agtori)*ang
			a2 = (math.pi/3+agtori)*(ang+1)
			v1 = Point(xc+hxr*math.cos(a1-arot),yc-hxr*math.sin(a1-arot))
			v2 = Point(xc+hxr*math.cos(a2-arot),yc-hxr*math.sin(a2-arot))
			s1 = Line(v1,v2)
			if (hxvl1[i][2] == 1.0): # ?? remove
				s1.setOutline("red")
			elif (hxvl1[i][2] == 0.0): # ??
				s1.setOutline("blue")
			else:
				s1.setOutline("black")
				s1.draw(win)
		cc = Circle(Point(xc,yc),hxr/2)
		cc.setOutline(color_rgb(int(hxvl1[i][2]*255),int(hxvl1[i][2]*235),235))
		cc.setFill(color_rgb(int(hxvl1[i][2]*255),int(hxvl1[i][2]*235),235))
		cc.draw(win)
	
	file.close()			
	win.postscript(file = "temp.eps", pageheight = sz-1, pagewidth = sz-1)
	epsimg = Image.open("temp.eps")
	epsimg.save("images/world00"+str(pno)+"_"+str(fname)+"_"+str(d)+"hb.png","png")
	win.close()
	return

'''	~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ @$ ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''	
	
def ssgScore(fname):
	hxvl1 = []
	file = open("world00"+str(pno)+"_0.txt","r")
	lno = 0
	for line in file:
		hxvl1.append([])
		hxvl1[lno].extend(list(map(float,re.findall('-?[0-9|\'.\']+', line))))	# Lambda expression on Regex
		lno = lno + 1
	
	hxvl2 = []
	file = open("world00"+str(pno)+"_"+str(fname)+".txt","r")
	lno = 0
	for line in file:
		hxvl2.append([])
		hxvl2[lno].extend(list(map(float,re.findall('-?[0-9|\'.\']+', line))))	# Lambda expression on Regex
		lno = lno + 1
	
	ar = 1	# 1 deg angular resolution for checking
	for ang in range(360/ar+1):
		# WATSON : take average of 7 cells around (a',b')	
		hxvl3 = [0 for x in range(0,len(hxvl1))]	
		for i in range(len(hxvl1)):
			# Find rotated centre of hxvl2
			# Find closest match to this pixel from elements in hxvl2
			# Assign matching hex value as value of original centre in hxvl3
			(ria, rib) = hexrot(hxvl2[i][0],hxvl2[i][1],ang*ar*math.pi/180)
			dmin = 100000
			jmin = 0
			for j in range(len(hxvl1)):
				dij = hexdist(ria,rib,hxvl2[j][0],hxvl2[j][1])
				if (dij < dmin):
					dmin = dij
					jmin = j
			hxvl3[i] = hxvl2[jmin][2]	
		# Find SSG score
		ssg = 0
		for i in range(len(hxvl1)):
			ssg = ssg + pow(hxvl1[i][2]-hxvl3[i],2)		# Decide on correlation score. Now, sum of square deviations
		print ("SSG for Rotation of \t"+str(ang*ar)+" degrees \t= "+str(round(ssg,2)))

'''	~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ @$ ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''

# Find new coordinated in a-b 60deg rotated coordinate system after rotation 	
def hexrot(a,b,ang):
	hxd = 20
	x = hxd * (a + b / 2)
	y = hxd * math.sqrt(3) * b / 2
	xc = sz/2
	yc = sz/2
	xxx = x - xc
	yyy = y - yc
	xnew = + yyy * math.sin(ang) + xxx * math.cos(ang) + xc 
	ynew = + yyy * math.cos(ang) - xxx * math.sin(ang) + yc
	bnew = 2 * (ynew / hxd) / math.sqrt(3)
	anew = (xnew / hxd - bnew / 2)
	return (anew, bnew)

'''	~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ @$ ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''

# Find distance between two coordinates in a-b 60deg rotated coordinate system
def hexdist(a1,b1,a2,b2):
	# { d = sqrt((x2-x1)^2 + (y2-y1)^2) } where, { x = a + b / 2 } and { y = sqrt(3) * b / 2 }
	d =	pow(a1 + b1/2 - a2 - b2/2,2) + 3*pow(0.5*(b2-b1),2) 
	return d

'''	~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ @$ ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''

import heapq

# Priority Queue for A* algorithm
class PriorityQueue:
	def __init__(self):
		self.elements = []
	
	def empty(self):
		return len(self.elements) == 0
	
	def put(self, item, priority):
		heapq.heappush(self.elements, (priority, item))
	
	def get(self):
		return heapq.heappop(self.elements)[1]

'''	~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ @$ ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''

class HexGridDB:
	def __init__(self, aMin, aMax, bMin, bMax):
		self.aMin = aMin
		self.aMax = aMax
		self.bMin = bMin
		self.bMax = bMax
		self.free = []
	
	def in_bounds(self, id):
		(a, b) = id
		return self.aMin <= a < self.aMax and self.bMin <= b < self.bMax
	
	def passable(self, id):
		return id in self.free
	
	def neighbors(self, id):
		(a, b) = id
		results = [(a+1,b), (a,b+1), (a-1,b+1), (a-1,b), (a,b-1), (a+1,b-1)]
		results = filter(self.in_bounds, results)
		results = filter(self.passable, results)
		return results

	def cost(self, from_node, to_node):
		return 1 #self.weights.get(to_node, 1)

'''	~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ @$ ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''

def hexpath(d,fname,start,goal):
	
	# start, goal : coordinates in a-b coordinate system

	# load graph from text file
	hxvl = []
	file = open("world00"+str(pno)+"_"+str(fname)+"_"+str(d)+".txt","r")
	lno = 0
	for line in file:
		hxvl.append([])
		hxvl[lno].extend(list(map(float,re.findall('-?[0-9|\'.\']+', line))))	# Lambda expression on Regex
		lno = lno + 1
	
	amin, amax, bmin, bmax = 1,-1,1,-1
	for i in range (0,len(hxvl)):
		if (hxvl[i][0] < amin):
			amin = hxvl[i][0]
		if (hxvl[i][0] > amax):
			amax = hxvl[i][0]
		if (hxvl[i][1] < bmin):
			bmin = hxvl[i][1]
		if (hxvl[i][1] > bmax):
			bmax = hxvl[i][1]	
	hxdb = HexGridDB(amin,amax,bmin,bmax)

	for i in range (0,len(hxvl)):
		if (hxvl[i][2] == 1.0):
			hxdb.free.append((hxvl[i][0],hxvl[i][1]))

	pq = PriorityQueue()
	pq.put(start, 0)
	came_from = {}
	cost_so_far = {}
	came_from[start] = None
	cost_so_far[start] = 0

	win = GraphWin("Print Map", sz, sz)
	showGrid(win,d,fname,hxvl)
	gxc = (goal[0] + float(goal[1])/2)*d
	gyc = (goal[1]*math.sqrt(3)/2)*d
	cc = Circle(Point(gxc,gyc),4)
	cc.setOutline("green")
	cc.setFill("green")
	cc.draw(win)

	# Run A*
	#	https://www.redblobgames.com/pathfinding/a-star/implementation.html
	while not pq.empty():
		current = pq.get()
		print("Exploring..."+str(current))
		if current == goal:
			print ("   ... goal reached")
			break
		for next in hxdb.neighbors(current):
			new_cost = cost_so_far[current] + hxdb.cost(current, next)
			if next not in cost_so_far or new_cost < cost_so_far[next]:
				cost_so_far[next] = new_cost
				priority = new_cost + heuristic(goal, next)
				pq.put(next, priority)
				came_from[next] = current
				# Show paths
				print ("   ... adding to be explored list : "+str(next))
				x1c = (next[0] + float(next[1])/2)*d
				y1c = (next[1]*math.sqrt(3)/2)*d
				x2c = (current[0] + float(current[1])/2)*d
				y2c = (current[1]*math.sqrt(3)/2)*d
				s1 = Line(Point(x1c,y1c),Point(x2c,y2c))
				s1.setOutline("red")
				s1.draw(win)

	win.getMouse() # pause for click in window
	win.close()
	return

def heuristic(ab1, ab2):
	(a1, b1) = ab1
	(a2, b2) = ab2
	return hexdist(a1,b1,a2,b2)		# for square grid --> abs(a1 - a2) + abs(b1 - b2)

def showGrid(win,d,fname,hxvl1):

	gap = 1		# gap between hex boundaries
	arot = (fname+30)*math.pi/180	# edge aligned form of hex
	agtori = 0
	hxr = d/2 - gap 		# hex radius
	for i in range(len(hxvl1)):
		xc = (hxvl1[i][0] + float(hxvl1[i][1])/2)*d
		yc = (hxvl1[i][1]*math.sqrt(3)/2)*d
		for ang in range (0,6):
			a1 = (math.pi/3+agtori)*ang
			a2 = (math.pi/3+agtori)*(ang+1)
			v1 = Point(xc+hxr*math.cos(a1-arot),yc-hxr*math.sin(a1-arot))
			v2 = Point(xc+hxr*math.cos(a2-arot),yc-hxr*math.sin(a2-arot))
			s1 = Line(v1,v2)
			if (hxvl1[i][2] != 1.0):
				s1.setOutline("black")
				s1.draw(win)
		cc = Circle(Point(xc,yc),hxr/2)
		cc.setOutline(color_rgb(int(hxvl1[i][2]*255),int(hxvl1[i][2]*235),235))
		cc.setFill(color_rgb(int(hxvl1[i][2]*255),int(hxvl1[i][2]*235),235))
		cc.draw(win)		
	return

'''	~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ @$ ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''

# TODO : Revisit later
def annotate(context):
	mycell = (0,0)
	print (mycell)
	if (context == 0):
		tgt = (())
	elif (context == 1):
		tgt = ((),(1,2))
	elif (context == 2):
		tgt = ((1,2),(2,3))
	return tgt 

'''	~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ @$ ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''

hxsz = 20
#drawMap("WorldBWScaled.png");
#hexprob(hxsz,0);
#hexBorder(hxsz,0);
#for i in range(0,360,30):
#turnMap(90);
	#hexprob(20,0);
	#ssgScore(90);
	#hexdraw(20,0);

hexpath(hxsz,0,(0,0),(12,31));	# Some test points : (12,31), (8,19)

#hexprob(20,0);
#anot = annotate(1);
#print anot
#print len(anot)

'''	~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ @$ ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''
