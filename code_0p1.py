# Run: python code_0p1.py graphics.py

from graphics import *
import math
import random

def a():
	a = 21;
	for j in range (1,a):
		for i in range (0,j):
			print j,
		print
		
def b():
	
	r = 20;
	ymax = 15;
	xmax = 12;
	
	edges = [1,0,0,0,0,0]
	pose = [0+2*r,0+2*r,0]
	hexcell = [pose,edges]
	print hexcell
	
	win = GraphWin("Print Map", 600, 600)
	
	for ycell in range (0,ymax):
		for xcell in range (0,xmax):
			for ang in range (0,6):
				v1 = Point(pose[0]+3*r*xcell+r*math.cos((math.pi/3)*ang),		pose[1]+math.sqrt(3)*r*ycell-r*math.sin((math.pi/3)*ang))
				v2 = Point(pose[0]+3*r*xcell+r*math.cos((math.pi/3)*(ang+1)),	pose[1]+math.sqrt(3)*r*ycell-r*math.sin((math.pi/3)*(ang+1)))
				s1 = Line(v1,v2)
				if (random.random() > 0.5):
					s1.setOutline("red")
				else:
					s1.setOutline("blue")
				s1.draw(win)
			v1 = Point(pose[0]+r+3*r*xcell,		pose[1]+math.sqrt(3)*r*ycell)
			v2 = Point(pose[0]+2*r+3*r*xcell,		pose[1]+math.sqrt(3)*r*ycell)
			s1 = Line(v1,v2)
			if (random.random() > 0.5):
				s1.setOutline("red")
			else:
				s1.setOutline("blue")
			s1.draw(win)
	
	#for ycell in range (0,12):
	#	for xcell in range (0,6):
	
	win.getMouse() # pause for click in window
	win.close()
b();

