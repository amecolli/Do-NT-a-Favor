from kivy.uix.widget import Widget
from kivy.graphics import Ellipse,Color
from kivy.core.window import Window

cwidth,cheight = Window.size
feed = ["a","b","c","d","e","f"]
theme_y = (244/255,227/255,16/255,1) #the yellow scheme used in the program

class Accm(Widget): #elem on board

	global cwidth, cheight, feed

	margin = cwidth/13
	r = cwidth/13
	spacing = cwidth/80
	sr = cwidth/40

	def __init__(self,row,col,i):
		self.row,self.col = row,col
		self.dscp = feed[i]
		self.spec=None
		self.seen=False
		self.used=False

	def __repr__(self): #for debugging
		return "(%d, %d) %s %s %s" % (self.row,self.col,self.spec,
			self.seen,self.used)

	def __eq__(self,other): #check if in a list
		#compare each attribute
		return (isinstance(other,Accm) and self.row==other.row 
			and self.col==other.col)

	def locate(self,row,col):
		#keep board and other lists in sync
		self.row,self.col = row,col

	def draw(self,d):
		#draw the element
		Color(*(1,1,1,1))
		Ellipse(source='./img/%s.png' % self.dscp,pos=(self.margin+self.col*self.r,
			self.margin+(self.row-d)*self.r),size=(self.r-self.spacing,
			self.r-self.spacing))
		#draw the special signs
		if self.spec=="L":
			Color(*theme_y)
			Ellipse(pos=(self.margin+self.col*self.r,self.margin+
				(self.row-d)*self.r),size=(self.sr,self.sr),source='./img/d3.png')
		elif self.spec=="4":
			Color(*theme_y)
			Ellipse(pos=(self.margin+self.col*self.r,self.margin+
				(self.row-d)*self.r),size=(self.sr,self.sr),source='./img/e4.png')
		elif self.spec=="5":
			Color(*theme_y)
			Ellipse(pos=(self.margin+self.col*self.r,self.margin+
				(self.row-d)*self.r),size=(self.sr,self.sr),source='./img/e5.png')