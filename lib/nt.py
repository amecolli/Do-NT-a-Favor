from kivy.uix.widget import Widget
from kivy.graphics import Rectangle
from kivy.core.window import Window
from random import randint

import lib.accm as a

cwidth,cheight = Window.size
selected_NT = 1
feed = ["a","b","c","d","e","f"]
feeddic = {1:'c',2:'d',3:'e'}
theme_y = (244/255,227/255,16/255,1) #the yellow scheme used in the program

class NT(Widget): #player

	global cwidth, cheight, feedic, feeddic

	margin = cwidth/13
	r = cwidth/13
	spacing = cwidth/80

	def __init__(self,row,col,snum):
		self.row,self.col = row,col
		self.color = (.8,0,0,1)
		self.dscp = "NT"
		self.selected = snum
		self.feedtype = feeddic[snum]
		self.count = 1

	def __eq__(self,other): #check if in a list
		return (isinstance(other,NT) and 
			self.row==other.row and self.col==other.col)

	def feed(self,board,special,scroll): #NT takes place of a certain element
		dirc = [(+1,-1),(+1,0),(+1,+1),
				( 0,-1),       ( 0,+1),
				(-1,-1),(-1,0),(-1,+1)]
		for i in range(8):
			dx,dy = dirc[i]
			r=self.row+dx
			c=self.col+dy
			if r<scroll or c<0 or r>=len(board) or c>=len(board[0]): continue
			if board[r][c].dscp == self.feedtype: #search for its "food"
				if board[r][c].spec!=None:
					for accm in reversed(special):
						if accm.row == r and accm.col == c:
							special.remove(accm) #no special effect;assimilated
							break
				board[r][c] = self
				row,col=self.row,self.col
				self.locate(r,c)
				self.drop(board,row,col,special)
				break #go one step at a time

	def drop(self,board,prevrow,prevcol,special):
		for r in range(prevrow,len(board)-1): #drop the element in the prevcol
			board[r][prevcol] = board[r+1][prevcol] #become the elem right above
			board[r][prevcol].locate(r,prevcol)
			if board[r][prevcol].dscp!="NT" and board[r][prevcol].spec!=None:
				for accm in reversed(special):
					if accm.row == r+1 and accm.col == prevcol:
						accm.locate(r,prevcol)
						break #each one at a time
		#generate a new one at the top after dropping elems
		board[len(board)-1][prevcol] = a.Accm(len(board)-1,prevcol,randint(
																0,len(feed)-1))

	def locate(self,row,col):
		self.row,self.col = row,col

	def draw(self,d):
		#there's a bug in kivy's animation, which caused flashing between frames
		#and the objectproperty cannot be used to update when NT changes
		#so this is the roundabout way of doing it
		#the program manually changes the frame every time the board updates
		self.count=2 if self.count==1 else 1
		Rectangle(source='./img/NT%d-%d.png' % (self.selected,self.count),
			pos=(self.margin+self.col*self.r,self.margin+(self.row-d)*self.r),
			size=(self.r-self.spacing,self.r-self.spacing),keep_data=True)