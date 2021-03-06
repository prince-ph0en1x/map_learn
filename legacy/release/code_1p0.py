## Code to generate hex tile probability

## \date: 21-10-2017
## \author: Aritra Sarkar (prince-ph0en1x)

from graphics import *
import math
import random
from PIL import Image
import re
import timeit

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

def turnMap(fname):		# rotation of global map

	win = GraphWin("Print Map", sz, sz)

	imgfile = Image.open("images/world002_0.png")
	rgbfile = imgfile.convert('RGB')
	
	rr = Rectangle(Point(0,0), Point(sz,sz))
	rr.setOutline("white")
	rr.setFill("white")
	rr.draw(win)

	xrotc = sz/2
	yrotc = sz/2
	arot = fname*math.pi/180
	
	# start = timeit.timeit()
	for ypix in range (0,imgfile.size[1]):
		for xpix in range (0,imgfile.size[0]):
			c1, c2, c3 = rgbfile.getpixel((xpix,ypix))
			
			xxx = xpix - xrotc
			yyy = ypix - yrotc			
			'''
			ynew = yyy + math.tan(-arot/2) * xxx		# 3 shear rotation - problem with 180 deg - tan(90)
			xnew = math.sin(arot) * ynew + xxx
			ynew = ynew + math.tan(-arot/2) * xnew
			'''
			xnew = +yyy * math.sin(arot) + xxx * math.cos(arot)
			ynew = +yyy * math.cos(arot) - xxx * math.sin(arot)
			
			p1 = Point(xnew + xrotc,ynew + yrotc)
			p1.setOutline(color_rgb(c1,c2,c3))
			p1.draw(win)
	# end = timeit.timeit()
	# print end - start
			
	# win.getMouse() # pause for click in window
	win.postscript(file = "temp.eps", pageheight = sz-1, pagewidth = sz-1)
	epsimg = Image.open("temp.eps")
	epsimg.save("images/world002_"+str(fname)+".png","png")
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
		print "SSG for Rotation of \t"+str(ang*ar)+" degrees \t= "+str(round(ssg,2))

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
	# d = sqrt((x2-x1)^2 + (y2-y1)^2)
	# where, { x = a + b / 2 } and { y = sqrt(3) * b / 2 }
	d =	pow(a1 + b1/2 - a2 - b2/2,2) + 3*pow(0.5*(b2-b1),2) 
	return d

'''	~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ @$ ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''

#drawMap();
#for i in range(0,360,30):
turnMap(180);
#hexprob(20,0);
#ssgScore(90);

'''	~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ @$ ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''