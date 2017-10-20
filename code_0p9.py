## Code to generate hex tile probability

## \date: 19-10-2017
## \author: Aritra Sarkar (prince-ph0en1x)

from graphics import *
import math
import random
from PIL import Image
import re

sz = 600

'''	~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ @$ ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''

def drawMap():
	
	## Plan:
		
	## draw a red circle on a black square of 600x600
	## add wb image at the centre and save image
	## rotate wb image by 90 deg and make semantic similar image
	
	win = GraphWin("Print Map", sz, sz)

	imgfile = Image.open("images/wb.png")
	rgbfile = imgfile.convert('RGB')
	
	rr = Rectangle(Point(0,0), Point(sz,sz))	#	https://stackoverflow.com/questions/13537483/when-saving-turtle-graphics-to-an-eps-file-the-background-color-shows-on-the-s
	rr.setOutline("white")
	rr.setFill("white")
	rr.draw(win)
	
	cc = Circle(Point(sz/2,sz/2), sz/2)
	cc.setOutline("red")
	cc.setFill("red")
	cc.draw(win)
	
	win.getMouse() # pause for click in window
	
	scale = 2
	imgcx = imgfile.size[0]/2
	imgcy = imgfile.size[1]/2
	for ypix in range (0,imgfile.size[1],scale):
		for xpix in range (0,imgfile.size[0],scale):
			c1, c2, c3 = rgbfile.getpixel((xpix,ypix))
			if not(c1 > 250 and c2 > 250  and c3 > 250):
				pt = Point((xpix+sz-imgcx)/scale,(ypix+sz-imgcy)/scale)
				pt.setOutline("blue")
				pt.draw(win)
	
	win.getMouse() # pause for click in window
	
	win.postscript(file = "temp.eps", pageheight = sz-1, pagewidth = sz-1)
	epsimg = Image.open("temp.eps")
	epsimg.save("images/world002_0.png","png")
	win.close()

'''	~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ @$ ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''

def turnMap(arot):		# rotation of global map
	
	win = GraphWin("Print Map", sz, sz)

	imgfile = Image.open("images/world002_0.png")
	rgbfile = imgfile.convert('RGB')
	
	xrotc = sz/2
	yrotc = sz/2
	
	scale = 2
	for ypix in range (0,imgfile.size[1],scale):
		for xpix in range (0,imgfile.size[0],scale):
			c1, c2, c3 = rgbfile.getpixel((xpix,ypix))
			
			xxx = xpix - xrotc
			yyy = ypix - yrotc
			
			xnew = +yyy * math.sin(arot) + xxx * math.cos(arot) 
			ynew = -yyy * math.cos(arot) - xxx * math.sin(arot) 
			
			p1 = Point(xnew + xrotc, ynew + yrotc)
			p1.setOutline(color_rgb(c1,c2,c3))
			p1.draw(win)
			
	win.getMouse() # pause for click in window
	
	win.postscript(file = "temp.eps", pageheight = sz-1, pagewidth = sz-1)
	epsimg = Image.open("temp.eps")
	epsimg.save("images/world002_90.png","png")
	win.close()

'''	~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ @$ ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''
	
def hexprob(d,fname):
	
	# d = vertex to vertex distance of hex
	
	# take world002_0.png and generate hex probability map
	
	win = GraphWin("Print Map", sz, sz)
	
	gap = 0	# gap between hex boundaries
	
	imgfile = Image.open("images/world002_"+str(fname)+".png")
	rgbfile = imgfile.convert('RGB')
	
	file = open("world002_"+str(fname)+".txt","w")
	
	rad = d/2 	#	d/(2*math.cos(30*2*math.pi/360))
	xmax =  int(math.ceil(imgfile.size[0]/d))+1
	ymax = int(math.ceil(imgfile.size[1]/(d*math.sqrt(3)/2)))+1
	print(math.sqrt(3)/2)
	for ys in range (0,ymax):
		for xs in range (-xmax,xmax):
			xc = (xs + float(ys)/2)*d
			yc = (ys*math.sqrt(3)/2)*d
			
			if (xc >= 0 and xc <= sz and yc >= 0 and yc <= sz): 
				
				ptot = 0
				pblu = 0
				for ypix in range (int(yc-rad),int(yc+rad)):
					for xpix in range (int(xc-rad),int(xc+rad)):
						if (xpix >= 0 and xpix < sz and ypix >= 0 and ypix < sz):
							ptot = ptot + 1
							c1, c2, c3 = rgbfile.getpixel((xpix,ypix))
							if (c1 == 255):
								pblu = pblu + 1
				prob = float(pblu)/ptot
				file.write(str(xs)+","+str(ys)+","+str(prob)+"\n")
				#print(xs,ys,prob)
				cc = Circle(Point(xc,yc), rad)
				cc.setOutline(color_rgb(int(prob*255),int(prob*255),255))
				cc.setFill(color_rgb(int(prob*255),int(prob*255),255))
				cc.draw(win)		
	
	file.close()			
	win.postscript(file = "temp.eps", pageheight = sz-1, pagewidth = sz-1)
	epsimg = Image.open("temp.eps")
	epsimg.save("images/world002_"+str(fname)+"h.png","png")
	win.getMouse() # pause for click in window
	win.close()
	return

'''	~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ @$ ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''	
	
def ssgScore(fname):
	hxvl1 = []
	file = open("world002_0.txt","r")
	lno = 0
	for line in file:
		hxvl1.append([])
		hxvl1[lno].extend(list(map(float,re.findall('-?[0-9|\'.\']+', line))))	# Lambda expression on Regex
		lno = lno + 1
	
	hxvl2 = []
	file = open("world002_"+str(fname)+".txt","r")
	lno = 0
	for line in file:
		hxvl2.append([])
		hxvl2[lno].extend(list(map(float,re.findall('-?[0-9|\'.\']+', line))))	# Lambda expression on Regex
		lno = lno + 1
	
	ar = 10	# 30 deg angular resolution
	
	#for i in range(len(hxvl1)):
	#	print hxvl2[i]

	for ang in range(360/ar+1):
		# Rotate hxvl2 by ang
		'''
			(a,b) rotate by ang gives (a',b'), thus assign p with p' of (round(a'),round(b'))
			Improve: take average of 7 cells around (a',b')
		'''
		
		hxvl3 = [0 for x in range(0,len(hxvl1))]	
		#if (ang == 0):
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
			#print (i,jmin,dmin,hxvl2[i][0],hxvl2[i][1],hxvl2[jmin][0],hxvl2[jmin][1])
			hxvl3[i] = hxvl2[jmin][2]
				
		# Find SSG score
		ssg = 0
		for i in range(len(hxvl1)):
			ssg = ssg + pow(hxvl1[i][2]-hxvl3[i],2)	# Decide on correlation score. Now, sum of square deviations
		print "SSG for Rotation of \t"+str(ang*ar)+" degrees \t= "+str(round(ssg,2))
	 	
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


def hexdist(a1,b1,a2,b2):
	'''
	dist{(a1,b1)--(a2,b2)}
	sqrt((x2-x1)^2 + (y2-y1)^2)
	x = a + b/2
	y = sqrt(3)*b/2
	'''
	d =	pow(a1 + b1/2 - a2 - b2/2,2) + 3*pow(0.5*(b2-b1),2) 
	return d
'''	~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ @$ ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''
'''
 X	S R	 C
AOC	 Q	XOZ
 Z	P T	 A
'''
#drawMap();
#hexprob(20,0);
ssgScore(90);

'''	~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ @$ ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''

def useless():
	
	ymax = int(math.ceil((ywin-3*r)/(math.sqrt(3)*r+gap)))
	xmax = int(math.ceil((xwin-2*r)/(1.5*r+gap*math.cos(math.pi/6))))
	agtori = 0*2*math.pi/360
	
	hmap = [[[0 for e in range(0,9)] for y in range(0,ymax)] for x in range(0,xmax)]
	for ycell in range (ymax):
		for xcell in range (xmax):
			if (xcell % 2 == 0):
				xc = r+(1.5*r+gap*math.cos(math.pi/6))*xcell
				yc = r+(math.sqrt(3)*r+gap)*ycell
			else:
				xc = r+(1.5*r+gap*math.cos(math.pi/6))*xcell
				yc = r+(math.sqrt(3)*r+gap)*ycell+(0.5*math.sqrt(3)*r+0.5*gap)
			
			c1, c2, c3 = rgbfile.getpixel((int(xc/xwin*jpgfile.size[0]),int(yc/ywin*jpgfile.size[1])))
			hmap[xcell][ycell][0] = xc
			hmap[xcell][ycell][1] = yc
			if ((c1+c2+c3)/3 < 128):
				hmap[xcell][ycell][2] = 1
			else:
				hmap[xcell][ycell][2] = 0

	# IMPROVE: Optimize multiple loops below
	
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
	
	markers = (5,5)
	
	# rotation of global map
	
	xrotc = hmap[int(xcell/2)][int(ycell/2)][0]
	yrotc = hmap[int(xcell/2)][int(ycell/2)][1]
	arot = -math.pi/10	#18 deg
	
	for ycell in range (0,ymax):
		for xcell in range (0,xmax):
			xxx = hmap[xcell][ycell][0] - xrotc;
			yyy = hmap[xcell][ycell][1] - yrotc;
			
			xnew = xxx * math.cos(arot) - yyy * math.sin(arot);
			ynew = xxx * math.sin(arot) + yyy * math.cos(arot);
			
			hmap[xcell][ycell][0] = xnew + xrotc;
			hmap[xcell][ycell][1] = ynew + yrotc;
  	
	# draw map
													
	for ycell in range (0,ymax):
		for xcell in range (0,xmax):
			for ang in range (0,6):
				xc = hmap[xcell][ycell][0]
				yc = hmap[xcell][ycell][1]
				p1 = Point(xc,yc)
				if (hmap[xcell][ycell][2] == 1):
					p1.setOutline("yellow")
				else:
					p1.setOutline("cyan")
				p1.draw(win)
				
				a1 = (math.pi/3+agtori)*ang
				a2 = (math.pi/3+agtori)*(ang+1)
				
				v1 = Point(xc+r*math.cos(a1-arot),yc-r*math.sin(a1-arot))
				v2 = Point(xc+r*math.cos(a2-arot),yc-r*math.sin(a2-arot))
				s1 = Line(v1,v2)
				
				if (hmap[xcell][ycell][3+ang] == 1):
					s1.setOutline("red")
				else:
					s1.setOutline("blue")
					
				s1.draw(win)
				
	pm = Point(hmap[markers[0]][markers[1]][0],hmap[markers[0]][markers[1]][1])
	pm.draw(win)
					
	win.getMouse() # pause for click in window
	win.close()

'''	~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ @$ ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''
