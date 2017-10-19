## Code to generate hex tile probability

## \date: 19-10-2017
## \author: Aritra Sarkar (prince-ph0en1x)

from graphics import *
import math
import random
from PIL import Image

sz = 600

def hexprob():
	
	# take world002_0.png and generate hex probability map
	
	win = GraphWin("Print Map", sz, sz)
	
	gap = 0	# gap between hex boundaries
	d = 20	# vertex to vertex distance of hex
	
	imgfile = Image.open("images/world002_90.png")
	rgbfile = imgfile.convert('RGB')
	
	rad = d/2 	#	d/(2*math.cos(30*2*math.pi/360))
	
	c1, c2, c3 = rgbfile.getpixel((300,300))
	print(c1,c2,c3)
	
	xmax =  int(math.ceil(imgfile.size[0]/d))+1
	ymax = int(math.ceil(imgfile.size[1]/(d*math.sqrt(3)/2)))+1
	print(math.sqrt(3)/2)
	for ys in range (0,ymax):
		for xs in range (-xmax,xmax):
			xc = (xs + float(ys)/2)*d
			yc = (ys*math.sqrt(3)/2)*d
			#print(xs,ys)
			
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
				
				cc = Circle(Point(xc,yc), rad)
				cc.setOutline(color_rgb(int(float(pblu)/ptot*255),int(float(pblu)/ptot*255),255))
				cc.setFill(color_rgb(int(float(pblu)/ptot*255),int(float(pblu)/ptot*255),255))
				cc.draw(win)		
				
	print(imgfile.size[0],xmax,ymax)
	
	win.postscript(file = "temp.eps", pageheight = sz-1, pagewidth = sz-1)
	epsimg = Image.open("temp.eps")
	epsimg.save("images/test6.png","png")
	win.getMouse() # pause for click in window
	win.close()
	return
	
	
	
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
	
hexprob();

