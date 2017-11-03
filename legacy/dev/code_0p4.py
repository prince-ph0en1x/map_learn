from graphics import *
import math
import random
from PIL import Image


def a():
	a = 21;
	for j in range (1,a):
		for i in range (0,j):
			print j,
		print
		
def drawHex():
	return 1
		
def b():
	# walls from image
		# threshold image (free/occupied)
		# hex centre grid image
		# if 2 centres are free, common edge is open, else closed
	# gap between hex
	# rotate hex
	
	xwin = 600
	ywin = 600
	win = GraphWin("Print Map", xwin, ywin)
	gap = 4		# gap between hex boundaries
	r = 6		# centre to vertex distance of hex
	
	jpgfile = Image.open("world001.jpg")
	rgbfile = jpgfile.convert('RGB')
	
	xsamp = int(math.ceil(jpgfile.size[0]/(xwin*2*r)))
	ysamp = int(math.ceil(jpgfile.size[1]/(ywin*2*r)))

	
	ymax = int(math.ceil((ywin-3*r)/(math.sqrt(3)*r+gap)))
	xmax = int(math.ceil((xwin-2*r)/(1.5*r+gap*math.cos(math.pi/6))))
	agtori = 0*2*math.pi/360
	
	edges = [1,0,0,0,0,0]
	pose = [0+r,0+r,0]
	hexcell = [pose,edges]
	print hexcell
	
	hmap = [[[0 for e in range(0,9)] for y in range(0,ymax)] for x in range(0,xmax)]
	for ycell in range (ymax):
		for xcell in range (xmax):
			if (xcell % 2 == 0):
				xc = pose[0]+(1.5*r+gap*math.cos(math.pi/6))*xcell
				yc = pose[1]+(math.sqrt(3)*r+gap)*ycell
			else:
				xc = pose[0]+(1.5*r+gap*math.cos(math.pi/6))*xcell
				yc = pose[1]+(math.sqrt(3)*r+gap)*ycell+(0.5*math.sqrt(3)*r+0.5*gap)
			
			c1, c2, c3 = rgbfile.getpixel((int(xc/xwin*jpgfile.size[0]),int(yc/ywin*jpgfile.size[1])))
			hmap[xcell][ycell][0] = xc
			hmap[xcell][ycell][1] = yc
			if ((c1+c2+c3)/3 < 128):
				hmap[xcell][ycell][2] = 1
			else:
				hmap[xcell][ycell][2] = 0

	# dirn 0
	for ycell in range (1,ymax):
		for xcell in range (0,xmax-1):
			if (hmap[xcell][ycell][2] == 1 or hmap[xcell+1][ycell-1][2] == 1):
				hmap[xcell][ycell][3+0] = 1
	# dirn 1
	for ycell in range (1,ymax):
		for xcell in range (0,xmax):
			if (hmap[xcell][ycell-1][2] == 1 or hmap[xcell][ycell][2] == 1):
				hmap[xcell][ycell][3+1] = 1
	# dirn 2
	for ycell in range (0,ymax):
		for xcell in range (1,xmax):
			if (hmap[xcell-1][ycell][2] == 1 or hmap[xcell][ycell][2] == 1):
				hmap[xcell][ycell][3+2] = 1
	# dirn 3
	for ycell in range (0,ymax-1):
		for xcell in range (1,xmax):
			if (hmap[xcell][ycell][2] == 1 or hmap[xcell-1][ycell+1][2] == 1):
				hmap[xcell][ycell][3+3] = 1
	# dirn 4
	for ycell in range (0,ymax-1):
		for xcell in range (0,xmax):
			if (hmap[xcell][ycell][2] == 1 or hmap[xcell][ycell+1][2] == 1):
				hmap[xcell][ycell][3+4] = 1
	# dirn 5
	for ycell in range (0,ymax):
		for xcell in range (0,xmax-1):
			if (hmap[xcell][ycell][2] == 1 or hmap[xcell+1][ycell][2] == 1):
				hmap[xcell][ycell][3+5] = 1
													
	for ycell in range (0,ymax):
		for xcell in range (0,xmax):
			for ang in range (0,6):
				xc = hmap[xcell][ycell][0]
				yc = hmap[xcell][ycell][1]
				p1 = Point(xc,yc)
				if (hmap[xcell][ycell][2] == 1):
					p1.setOutline("blue")
				else:
					p1.setOutline("red")
				p1.draw(win)
				
				a1 = (math.pi/3+agtori)*ang
				a2 = (math.pi/3+agtori)*(ang+1)
				
				v1 = Point(xc+r*math.cos(a1),yc-r*math.sin(a1))
				v2 = Point(xc+r*math.cos(a2),yc-r*math.sin(a2))
				s1 = Line(v1,v2)
				
				if (hmap[xcell][ycell][3+ang] == 1):
					s1.setOutline("red")
				else:
					s1.setOutline("blue")
					
				s1.draw(win)
					
	win.getMouse() # pause for click in window
	win.close()
b();

