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
import io

sz = 720	# Arbitarily chosen constant
pno = 4		# Project number

'''	~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ @$ ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''

# Take an image of any size > 600x600, scale and save black-white greyscale threshold image.
def bwscaledMap(fname, trshld):
	
	imgfile = Image.open("images/maps/"+str(fname))
	rgbfile = imgfile.convert('RGB')

	win = GraphWin("Print Map", sz, sz)

	#	https://stackoverflow.com/questions/13537483/when-saving-turtle-graphics-to-an-eps-file-the-background-color-shows-on-the-s
	rr = Rectangle(Point(0,0), Point(sz-1,sz-1))	
	rr.setOutline("white")
	rr.setFill("white")
	rr.draw(win)

	xscale = imgfile.size[0]/sz
	yscale = imgfile.size[1]/sz
	ypix = 0
	while (ypix < imgfile.size[1]-yscale):
		xpix = 0
		while (xpix < imgfile.size[0]-xscale):
			pt = Point(xpix/xscale,ypix/yscale)
			rr = 0
			gg = 0
			bb = 0
			ysc = (int)(math.floor(yscale))
			xsc = (int)(math.floor(xscale))
			xysq = ysc * xsc
			for yypix in range (0,ysc,1):
				for xxpix in range (0,xsc,1):
					c1, c2, c3 = rgbfile.getpixel((xpix+xxpix,ypix+yypix))
					rr = rr + c1
					gg = gg + c2
					bb = bb + c3
			rr = rr / xysq
			gg = gg / xysq
			bb = bb / xysq
			if not(rr > trshld and gg > trshld and bb > trshld):
				pt.setOutline("black")
				pt.draw(win)
			xpix = xpix + xscale
		ypix = ypix + yscale

	#win.getMouse() # pause for click in window
	ps = win.postscript(pagewidth=sz-1, pageheight=sz-1, width=sz-1, height=sz-1)
	epsimg = Image.open(io.BytesIO(ps.encode('utf-8')))
	epsimg.save("images/world00"+str(pno)+"_bw.png","png")
	win.close()

'''	~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ @$ ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''

# Take output image from bwscaledMap and render red-blue map inside circle after rotating by a specified angle
def drawMap(ang):
	
	imgfile = Image.open("images/world00"+str(pno)+"_bw.png")
	rgbfile = imgfile.convert('RGB')

	win = GraphWin("Print Map", sz, sz)

	rr = Rectangle(Point(0,0), Point(sz-1,sz-1))	
	rr.setOutline("white")
	rr.setFill("white")
	rr.draw(win)
	
	rbc = math.floor(sz/2)
	cc = Circle(Point(rbc,rbc),rbc-3)
	cc.setOutline("red")
	cc.setFill("red")
	cc.draw(win)
	
	scale = math.sqrt(2)*(sz/(sz-3))
	xrotc = sz/2
	yrotc = sz/2
	arot = ang*math.pi/180

	ypix = 0
	while (ypix < imgfile.size[1]):
		xpix = 0
		while (xpix < imgfile.size[0]):
			c1, c2, c3 = rgbfile.getpixel((xpix,ypix))
			if (c1 < 250):
				xxx = (xpix-sz/2)/scale+sz/2 - xrotc
				yyy = (ypix-sz/2)/scale+sz/2 - yrotc			
				xnew = +yyy * math.sin(arot) + xxx * math.cos(arot) + xrotc	# 3 shear rotation no used as problem with 180 deg - tan(90)
				ynew = +yyy * math.cos(arot) - xxx * math.sin(arot) + yrotc
				p1 = Point(xnew,ynew)
				p1.setOutline("blue")
				p1.draw(win)
			xpix = xpix + scale	
		ypix = ypix + scale

	ps = win.postscript(pagewidth=sz-1, pageheight=sz-1, width=sz-1, height=sz-1)
	epsimg = Image.open(io.BytesIO(ps.encode('utf-8')))
	epsimg.save("images/world00"+str(pno)+"_"+str(ang)+".png","png")
	win.close()

'''	~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ @$ ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''

# Generate Hex grid image of input map from drawMap/turnMap
def hexProb(hxsz,ang):
	 
	# hxsz = vertex to vertex distance of hex
	
	# TODO: Update to hex prob in hex grid, not circle

	imgfile = Image.open("images/world00"+str(pno)+"_"+str(ang)+".png")
	rgbfile = imgfile.convert('RGB')
	
	file = open("world00"+str(pno)+"_"+str(ang)+"_"+str(hxsz)+".txt","w")
	
	win = GraphWin("Print Map", sz, sz)
	rad = hxsz/2 	#	hxsz/(2*math.cos(30*2*math.pi/360))
	xmax = int(math.ceil(imgfile.size[0]/hxsz))+1
	ymax = int(math.ceil(imgfile.size[1]/(hxsz*math.sqrt(3)/2)))+1
	for ys in range (0,ymax):
		for xs in range (-xmax,xmax):
			xc = (xs + float(ys)/2)*hxsz
			yc = (ys*math.sqrt(3)/2)*hxsz
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
	ps = win.postscript(pagewidth=sz-1, pageheight=sz-1, width=sz-1, height=sz-1)
	epsimg = Image.open(io.BytesIO(ps.encode('utf-8')))
	epsimg.save("images/world00"+str(pno)+"_"+str(ang)+"_"+str(hxsz)+"h.png","png")
	win.close()
	return

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

import time

def hexPath(hxsz,ang,start,goal):
	
	# start, goal : coordinates in a-b coordinate system

	# load graph from text file
	hxvl = []
	file = open("world00"+str(pno)+"_"+str(ang)+"_"+str(hxsz)+".txt","r")
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
	showGrid(win,hxsz,ang,hxvl)
	gxc = (goal[0] + float(goal[1])/2)*hxsz
	gyc = (goal[1]*math.sqrt(3)/2)*hxsz
	cc = Circle(Point(gxc,gyc),4)
	cc.setOutline("green")
	cc.setFill("green")
	cc.draw(win)

	# Run A*
	#	https://www.redblobgames.com/pathfinding/a-star/implementation.html
	# start = timeit.timeit()
	# end = timeit.timeit()
	# print end - start
	while not pq.empty():
		current = pq.get()
		#print("Exploring..."+str(current))
		if current == goal:
			#print ("   ... goal reached")
			break
		for next in hxdb.neighbors(current):
			new_cost = cost_so_far[current] + hxdb.cost(current, next)
			if next not in cost_so_far or new_cost < cost_so_far[next]:
				cost_so_far[next] = new_cost
				priority = new_cost + heuristic(goal, next)
				pq.put(next, priority)
				came_from[next] = current
				#'''
				# Show paths
				#print ("   ... adding to be explored list : "+str(next))
				x1c = (next[0] + float(next[1])/2)*hxsz
				y1c = (next[1]*math.sqrt(3)/2)*hxsz
				x2c = (current[0] + float(current[1])/2)*hxsz
				y2c = (current[1]*math.sqrt(3)/2)*hxsz
				s1 = Line(Point(x1c,y1c),Point(x2c,y2c))
				s1.setOutline("green")
				s1.draw(win)
				# time.sleep(0.1)		# to see animation
				#'''

	# Show and save A* path
	path = reconstruct_path(came_from,start,goal)
	file = open("world00"+str(pno)+"_"+str(ang)+"_"+str(hxsz)+"p1.txt","w")
	for i in range (1,len(path)):
		x1c = (path[i-1][0] + float(path[i-1][1])/2)*hxsz
		y1c = (path[i-1][1]*math.sqrt(3)/2)*hxsz
		x2c = (path[i][0] + float(path[i][1])/2)*hxsz
		y2c = (path[i][1]*math.sqrt(3)/2)*hxsz
		s1 = Line(Point(x1c,y1c),Point(x2c,y2c))
		s1.setOutline("red")
		s1.draw(win)
		file.write(str(path[i])+"\n")
	file.close()

	win.close()
	return

'''	~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ @$ ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''

def reconstruct_path(came_from, start, goal):
    current = goal
    path = [current]
    while current != start:
        current = came_from[current]
        path.append(current)
    path.append(start) # optional
    path.reverse() # optional
    return path

'''	~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ @$ ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''

def heuristic(ab1, ab2):
	(a1, b1) = ab1
	(a2, b2) = ab2
	return hexdist(a1,b1,a2,b2)		# for square grid --> abs(a1 - a2) + abs(b1 - b2)

'''	~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ @$ ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''

def showGrid(win,d,fname,hxvl1):

	gap = 1		# gap between hex boundaries
	arot = (fname+30)*math.pi/180	# edge aligned form of hex
	agtori = 0
	hxr = d/2 - gap 		# hex radius
	for i in range(len(hxvl1)):
		xc = (hxvl1[i][0] + float(hxvl1[i][1])/2)*d
		yc = (hxvl1[i][1]*math.sqrt(3)/2)*d
		if (hxvl1[i][2] <= 1.0):		# to reduce display time make it (< 1.0) from (<= 1.0)
			'''
			for ang in range (0,6):
				a1 = (math.pi/3+agtori)*ang
				a2 = (math.pi/3+agtori)*(ang+1)
				v1 = Point(xc+hxr*math.cos(a1-arot),yc-hxr*math.sin(a1-arot))
				v2 = Point(xc+hxr*math.cos(a2-arot),yc-hxr*math.sin(a2-arot))
				s1 = Line(v1,v2)
				if (hxvl1[i][2] != 1.0):
					s1.setOutline("black")
					s1.draw(win)
			'''
			cc = Circle(Point(xc,yc),hxr/2)
			cc.setOutline(color_rgb(int(hxvl1[i][2]*255),int(hxvl1[i][2]*235),235))
			cc.setFill(color_rgb(int(hxvl1[i][2]*255),int(hxvl1[i][2]*235),235))
			cc.draw(win)		
	return

'''	~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ @$ ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''	

# Find correlation score between 0 deg and rotated hexProb matrix to find rotation angle
def ssgScore(hxsz,ang,ar):
	hxvl1 = []
	file = open("world00"+str(pno)+"_0_"+str(hxsz)+".txt","r")
	lno = 0
	for line in file:
		hxvl1.append([])
		hxvl1[lno].extend(list(map(float,re.findall('-?[0-9|\'.\']+', line))))	# Lambda expression on Regex
		lno = lno + 1
	
	hxvl2 = []
	file = open("world00"+str(pno)+"_"+str(ang)+"_"+str(hxsz)+".txt","r")
	lno = 0
	for line in file:
		hxvl2.append([])
		hxvl2[lno].extend(list(map(float,re.findall('-?[0-9|\'.\']+', line))))	# Lambda expression on Regex
		lno = lno + 1
	
	ssg = [0 for x in range(0,int(360/ar)+1)]
	for rotang in range(0,(int(360/ar)+1)):
		# Find rotated centre of place cells in hxvl2; then find closest match to this pixel from elements in hxvl1 and assign matching hex value as value of original centre
		for i in range(len(hxvl2)):
			if (hxvl2[i][2] < 1.0):
				(ria, rib) = hexrot(hxsz,hxvl2[i][0],hxvl2[i][1],-rotang*ar*math.pi/180)
				jmin = 0
				for j in range(len(hxvl1)):
					if (hxvl1[j][0] == int(round(ria)) and hxvl1[j][1]==int(round(rib))):
						jmin = j
						break
				ssg[rotang] = ssg[rotang] + pow(hxvl1[jmin][2]-hxvl2[i][2],2)		# Decide on correlation score. Now, sum of square deviations
		# print ("SSG for counter rotation of \t"+str(rotang*ar)+" degrees \t= "+str(round(ssg[rotang],2)))
	
	# Find min ssg and confidence score
	#ssg = [2660.1871999999767, 2655.163199999984, 236.33119999999363, 2663.932799999987, 2687.5519999999797, 2405.6943999999994, 2668.905599999985, 2663.37919999999, 1148.286400000016, 2683.8655999999924, 2688.017599999973, 2363.212800000013, 2660.1871999999767]
	minssg = ssg[0]
	ssgang = 0
	for i in range(len(ssg)):
		if (ssg[i] < minssg):
			minssg = ssg[i]
			ssgang = i*ar
	print ("Counter rotation suggested angle from SSG scoring is "+str(ssgang)+" degrees")
	return

'''	~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ @$ ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''

# Find new coordinated in a-b 60deg rotated coordinate system after rotation 	
def hexrot(hxd,a,b,ang):
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

# Translate A* path on 0 deg map to rotated map with its ssg counter angle suggested path rotation
def ssgPath(hxsz,ang,ssgang):

	hxvl = []
	file = open("world00"+str(pno)+"_"+str(ang)+"_"+str(hxsz)+".txt","r")
	lno = 0
	for line in file:
		hxvl.append([])
		hxvl[lno].extend(list(map(float,re.findall('-?[0-9|\'.\']+', line))))	# Lambda expression on Regex
		lno = lno + 1
	
	win = GraphWin("Print Map", sz, sz)
	showGrid(win,hxsz,ang,hxvl)
	
	file = open("world00"+str(pno)+"_0_"+str(hxsz)+"p1.txt","r")
	lno = 0
	path = []
	for line in file:
		path.append([])
		path[lno].extend(list(map(float,re.findall('-?[0-9]+', line))))	# Lambda expression on Regex
		lno = lno + 1
	file.close
	
	for i in range (1,len(path)):
		x1c = (path[i-1][0] + float(path[i-1][1])/2)*hxsz
		y1c = (path[i-1][1]*math.sqrt(3)/2)*hxsz
		x2c = (path[i][0] + float(path[i][1])/2)*hxsz
		y2c = (path[i][1]*math.sqrt(3)/2)*hxsz
		s1 = Line(Point(x1c,y1c),Point(x2c,y2c))
		s1.setOutline("green")
		s1.draw(win)

		(ra1,rb1) = hexrot(hxsz,path[i-1][0],path[i-1][1],ssgang*math.pi/180)
		(ra2,rb2) = hexrot(hxsz,path[i][0],path[i][1],ssgang*math.pi/180)
		x1c = (ra1 + float(rb1)/2)*hxsz
		y1c = (rb1*math.sqrt(3)/2)*hxsz
		x2c = (ra2 + float(rb2)/2)*hxsz
		y2c = (rb2*math.sqrt(3)/2)*hxsz
		s1 = Line(Point(x1c,y1c),Point(x2c,y2c))
		s1.setOutline("red")
		s1.draw(win)

	win.getMouse() # pause for click in window
	ps = win.postscript(pagewidth=sz-1, pageheight=sz-1, width=sz-1, height=sz-1)
	epsimg = Image.open(io.BytesIO(ps.encode('utf-8')))
	epsimg.save("images/world00"+str(pno)+"_"+str(ang)+"_"+str(hxsz)+"p1.png","png")
	win.close()

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
		#continue
	elif (context == 1):
		tgt = ((),(1,2))
	elif (context == 2):
		tgt = ((1,2),(2,3))
	print (len(tgt),tgt)
	return  

'''	~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ @$ ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''

def menu():
	while True:
		print("==================")
		print("1 - bwscaledMap")
		print("2 - drawMap")
		print("3 - hexProb")
		print("4 - hexPath")
		print("5 - ssgScore")
		print("6 - ssgPath")
		print("7 - annotate")
		print("8,9 - <unassigned>")
		print("0 - EXIT")
		print("==================")
		inp = int(input("Enter Operation : "))								# ~~~ Tested Inputs ~~~
		if (inp == 1):
			print(">> bwscaledMap(fname, trshld)")
			fname = input("\tEnter filename : ")							# map003.jpg		map004.jpg		map008.jpg
			trshld = int(input("\tEnter threshold value : "))				# 246				170				240
			bwscaledMap(fname, trshld)
		elif (inp == 2):
			print(">> drawMap(ang)")
			ang = int(input("\tEnter rotation angle in degrees : "))		#									60, 90
			drawMap(ang)
		elif (inp == 3):
			print(">> hexProb(hxsz,ang)")
			hxsz = int(input("\tEnter hexagon size in pixels : "))			# 20								5
			ang = int(input("\tEnter image angle to process : "))			#									60, 90
			hexProb(hxsz,ang)
		elif (inp == 4):
			print(">> hexPath(hxsz,ang,start,goal)")
			hxsz = int(input("\tEnter hexagon size in pixels : "))			# 20								5
			ang = int(input("\tEnter image angle to process : "))			#									0
			hexPath(hxsz,ang,(15,27),(3,143))								# (12,31)/(8,19)					(15,27),(3,143)
		elif (inp == 5):
			print(">> ssgScore(hxsz,ang,ar)")
			hxsz = int(input("\tEnter hexagon size in pixels : "))			# 20								5
			ang = int(input("\tEnter image angle to process : "))			#									60
			ar = int(input("\tEnter ssg angular step size in degrees : "))	#									30
			ssgScore(hxsz,ang,ar)
		elif (inp == 6):
			print(">> ssgPath(hxsz,ang,ssgang)")
			hxsz = int(input("\tEnter hexagon size in pixels : "))			# 20								5
			ang = int(input("\tEnter image angle to process : "))			#									60
			ssgang = int(input("\tEnter SSG angle to rotate path : "))		#									60
			ssgPath(hxsz,ang,ssgang)
		elif (inp == 7):
			#anot = annotate(1);
			continue
		elif (inp == 8):
			continue
		elif (inp == 9):
			continue
		elif (inp == 0):
			break
		else:
			print("Invalid selection, try again!")

'''	~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ @$ ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''

pno = int(input("Enter Problem ID : "))										# 4									8
menu()

'''	~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ @$ ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''

## Links:
	# https://kevingue.wordpress.com/research/aisle-design-for-warehouses/