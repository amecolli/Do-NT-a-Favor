from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.widget import Widget
from kivy.graphics import Ellipse,Color,Rectangle
from random import randint
from kivy.clock import Clock
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.event import EventDispatcher
from kivy.core.window import Window
import copy

feed = ["a","b","c","d","e","f"]
selected_NT = 1
cwidth,cheight = Window.size
theme_y = (244/255,227/255,16/255,1) #the yellow scheme used in the program

record = {'survival':[0,None],'endless':[0,None]}

import lib.accm as a
import lib.nt as nt

class Board(Widget):

	global feed, cwidth, cheight, theme_y, record, selected_NT

	cr = cwidth/16

	# def __init__(self,snum,**kwargs):
	# 	super(Board,self).__init__(**kwargs)
	# 	self.init(snum)

	def __init__(self,snum,**kwargs):
		global selected_NT
		super(Board,self).__init__(**kwargs)
		self.init(snum)
		selected_NT = snum

	def init(self,snum):
		self.margin = cwidth/13
		self.cellHeight,self.cellWidth = cwidth/13,cwidth/13
		self.col,self.row = 6,8
		self.selectedNT = snum
		#all the partial lists for further operation
		self.switch,self.cancel,self.NT,self.special,self.accmed =[],[],[],[],[]
		self.eliminating,self.pause,self.gameover = False, False, False
		self.timerCount,self.limit,self.target = 0,360,3
		self.board = [[None]*self.col for row in range(self.row)]
		self.scroll = 0
		self.startToEliminate = False
		for row in range(self.row):
			for col in range(self.col):
				i = randint(0,len(feed)-1)
				self.board[row][col] = a.Accm(row,col,i)
		self.initPlayer()
		self.tempboard = copy.deepcopy(self.board) #for elimination animation
		self.initDraw()
		Clock.schedule_interval(self.timerFired,.5)

	def initDraw(self):
		t_x,t_y = 500,150 #position of the time bar (left bottom)
		t_w,t_h = 50,300 #size of the time bar
		N_x,N_y = 570,150 #position of the NT counter
		N_r = 80 #size of the NT counter
		selected_NT = self.selectedNT
		with self.canvas:
			for row in range(self.row):
				for col in range(self.col):
					self.board[row][col].draw(0) #no offset
			#draw the background of the time bar
			Color(*(0,0,0,.5))
			Rectangle(pos=(t_x,t_y),size=(t_w,t_h))
			#draw the time bar itself (full when initiated)
			Color(*theme_y)
			Rectangle(pos=(t_x,t_y),size=(t_w,t_h))
			#draw the image that counts the number of NT went across the board
			Color(*(0,0,0,.5))
			Rectangle(source='img/NT%d-1.png'% selected_NT,pos=(N_x,N_y),
				size=(N_r,N_r))

	def initPlayer(self):
		if len(self.NT) == self.col: return
		while True: #so the new NT doesn't crash on existing ones...
			NTrow, NTcol = self.scroll,randint(0,self.col-1)#0th row is @ bottom
			if self.board[NTrow][NTcol].dscp!="NT":
				break
		newNT = nt.NT(NTrow,NTcol,self.selectedNT)
		self.board[NTrow][NTcol] = newNT
		self.NT.append(newNT)

	def on_touch_down(self,touch):
		if self.eliminating: return
		row = int((touch.y-self.margin)//self.cellHeight)+self.scroll #offset
		col = int((touch.x-self.margin)//self.cellWidth)
		if (row<self.scroll or col<0 or row>=self.row+self.scroll
			or col>=self.col): return #out of bound
		self.switch.append((row,col))

	def on_touch_up(self,touch):
		if self.switch != []: #only when there's one legal start point
			x0,y0 = self.switch[0]
			y1= int((touch.x-self.margin)//self.cellHeight)
			x1= int((touch.y-self.margin)//self.cellWidth)+self.scroll
			if (x1<self.scroll or y1<0 or x1>=self.row+self.scroll 
				or y1>=self.col): return
			#only neighbors can switch
			if x1>x0: self.switch.append((x0+1,y0))
			elif x1<x0: self.switch.append((x0-1,y0))
			elif y1>y0: self.switch.append((x0,y0+1))
			elif y1<y0: self.switch.append((x0,y0-1))
			if len(self.switch)%2==0:
				self.trySwitch() #actually do the switch
			self.update() #refresh the board immediately
			self.switch = []

	def trySwitch(self): 
		r0,c0 = self.switch[0]
		r1,c1 = self.switch[1]
		a1,a2 = self.board[r0][c0],self.board[r1][c1]
		if a1.dscp!="NT" and a2.dscp!="NT" and a1.spec!=None and a2.spec!=None:
			self.specialSwitch(a1,a2) #handle it differently
			return
		#try to switch
		self.board[r0][c0],self.board[r1][c1] = self.board[r1][c1], \
			self.board[r0][c0]
		self.board[r0][c0].locate(r0,c0)
		self.board[r1][c1].locate(r1,c1)
		#and if the switch is illegal i.e. nothing changes
		if self.search() == None: #undo
			self.board[r0][c0],self.board[r1][c1] = self.board[r1][c1], \
				self.board[r0][c0]
			self.board[r0][c0].locate(r0,c0)
			self.board[r1][c1].locate(r1,c1)
		self.tempboard=copy.deepcopy(self.board) #the tempboard is updated

	def specialSwitch(self,c1,c2): #aka really sad switch
		i = randint(0,len(self.NT)-1) #randomly choose an NT to process
		row,col = self.NT[i].row,self.NT[i].col
		j = feed.index(c1.dscp)
		if c1.spec==c2.spec: #replace a random player with the element
			self.board[row][col] = a.Accm(row,col,j)
			self.NT.pop(i)
			if len(self.NT)==0: self.gameover = True
		else: #boost the player to the top
			self.board[self.row-1+self.scroll][col]=self.board[row][col]
			self.board[row][col].locate(self.row-1+self.scroll,col)
			self.board[row][col]=a.Accm(row,col,j)
		self.tempboard=copy.deepcopy(self.board)
		self.eliminateFill(c1.row,c1.col,c2.row-c1.row,c2.col-c1.col,2)

	def searchInDir(self,s,row,col,dirc):
		d = [( 0,+1),(+1, 0),(0,-1),(-1,0)]
		drow,dcol = d[dirc]
		count = 0
		while True: #try to search as far as possible
			r,c = row+drow*count,col+dcol*count
			if r<self.scroll or c<0 or r>=self.row+self.scroll or c>=self.col:
				break
			elif self.board[r][c].dscp!=s:
				break
			else: #found one
				count+=1
		if count>=3: #has 3 or more grouped elements
			return (row,col,drow,dcol,count)
		return None

	def searchFromCell(self,row,col):
		for dirc in range(4): #only in 4 directions (up,down,left,right)
			result = self.searchInDir(self.board[row][col].dscp,row,col,dirc)
			if result!=None:
				return result
		return None

	def search(self): #go over each element on board
		#search from the top so it doesn't miss any possible elimination
		#prioritize special elements
		for row in range(self.row+self.scroll-1,self.scroll-1,-1):
			for col in range(self.col):
				if self.board[row][col].dscp=="NT": continue
				if self.board[row][col].spec!=None:
					result = self.searchFromCell(row,col)
					if result!=None:
						return result
		for row in range(self.row+self.scroll-1,self.scroll-1,-1):
			for col in range(self.col):
				if self.board[row][col].dscp=="NT": continue
				result = self.searchFromCell(row,col)
				if result!=None:
					return result		
		return None

	def check3s(self):
		if self.search() == None: self.eliminating=False #allow other actions
		else:
			self.eliminating = True
			x0,y0,drow,dcol,l = self.search()
			for i in range(l):
				row,col = x0+i*drow,y0+i*dcol
				#record the position of ones just eliminated(for graphic effect)
				self.cancel.append(self.board[x0+i*drow][y0+i*dcol])
			if l == 3: #check if it's a double 3
				result = self.isDouble3(x0,y0,drow,dcol,l)
				if result!=None: 
					#will set the special one and leave it on board
					self.eliminateWing(result)
			elif l == 4:
				midr,midc = (x0+x0+(l-1)*drow)//2,(y0+y0+(l-1)*dcol)//2
				self.board[midr][midc].spec = "4" #set up a special elem
			elif l>=5:
				midr,midc = (x0+x0+(l-1)*drow)//2,(y0+y0+(l-1)*dcol)//2
				self.board[midr][midc].spec = "5"
			#self.debugPrint(x0,y0,drow,dcol,l)
			self.eliminateFill(x0,y0,drow,dcol,l)
		return self.eliminating


	def update(self): #draw the game after the set time interval
		self.canvas.clear()
		with self.canvas:
			if self.cancel == []: #no elimination effect to display
				for row in range(self.row):
					for col in range(self.col):
						elem = self.board[row][col] #use the original board
						elem.draw(0)
			else: #display elimination effect
				for row in range(self.row):
					for col in range(self.col):
						elem = self.tempboard[row][col] #use the unchanged board
						if elem in self.cancel:
							Color(*(1,1,1,1))
							Ellipse(pos=(self.margin+col*self.cellWidth,
								self.margin+row*self.cellHeight),size=(
								self.cr,self.cr),source='img/cancel.png')
						else: elem.draw(0)
				self.cancel = [] #prepare another round of cancelling
				self.tempboard = copy.deepcopy(self.board) #update the tempboard
		self.draw_peripheral()		

	def draw_peripheral(self):
		t_x,t_y = 500,150 #position of the time bar (left bottom)
		t_w,t_h = 50,300 #size of the time bar
		N_x,N_y = 570,150 #position of the NT counter
		N_r = 80 #size of the NT counter
		l_x,l_y = 595,155 #position of the label (NT counter)
		l_r = 30 #size of the label
		selected_NT = self.selectedNT
		with self.canvas:
			#draw the time bar
			Color(*(0,0,0,.2))
			Rectangle(pos=(t_x,t_y),size=(t_w,t_h))
			Color(*theme_y)
			Rectangle(pos=(t_x,t_y),size=(t_w,
				(t_h/self.limit*(self.limit-self.timerCount))))
			#draw the NT counter
			Color(*(0,0,0,.5))
			Rectangle(source='img/NT%d-1.png'% selected_NT,pos=(N_x,N_y),
				size=(N_r,N_r))
			Color(*(1,1,1,1))
			Label(text=str(len(self.accmed)),pos=(l_x,l_y),size=(l_r,l_r))

	def isDouble3(self,x0,y0,drow,dcol,l):
		x1,y1 = x0+(l-1)*drow,y0+(l-1)*dcol
		r0,c0,r1,c1=x0,y0,x1,y1
		if r1>r0 or c1<c0:
			x0,y0,x1,y1,drow,dcol = r1,c1,r0,c0,-drow,-dcol#search from top&left
		#only search in direction that's perpenticular to the existing 3
		d = [(1-abs(drow),1-abs(dcol)),(abs(drow)-1,abs(dcol)-1)]
		dcount = [0,0] #check in both opposite directions
		for i in range(l): #start row/col
			row,col = x0+i*drow,y0+i*dcol
			if (row<self.scroll or col<0 or row>=self.row+self.scroll 
				or col>=self.col): continue
			rDscp = self.board[row][col].dscp #reference description
			for dirc in range(len(d)): #direction
				dx,dy = d[dirc]
				while True: #bascially doing the same as search()
					r,c = row+dx*dcount[dirc],col+dy*dcount[dirc]
					if (r<self.scroll or c<0 or r>=self.row+self.scroll 
						or c>=self.col): break
					elif self.board[r][c].dscp!=rDscp: break
					else: dcount[dirc]+=1
			if dcount[0]>=3: return (row,col,d[0],dcount[0])
			elif dcount[1]>=3: return (row,col,d[1],dcount[1])
			elif dcount[0]+dcount[1]>=4: #a cross/T
				sR,sC = row+(dcount[0]-1)*d[0][0],col+(dcount[0]-1)*d[0][1]
				return (sR,sC,d[1],dcount[0]+dcount[1]-1)
		return None					

	def setCross(self,startR,startC,dr,dc,l):
		#find the (row,col) of the intersection of double 3
		#the elem @ this position will have special effect
		for i in range(l):
			row,col = startR+dr*i,startC+dc*i
			if self.board[row][col] in self.cancel: #intersection
				return (row,col)

	def eliminateWing(self,result): #eliminate part of the double 3
		(row,col,(dr,dc),l2) = result
		endr,endc = row+(l2-1)*dr,col+(l2-1)*dc
		if endr>row or endc<col:
			row,col,endr,endc = endr,endc,row,col #search from top&left
			dr,dc = -dr,-dc
		midr,midc = self.setCross(row,col,dr,dc,l2)
		self.board[midr][midc].spec = "L"
		for i in range(l2):
			self.cancel.append(self.board[row+i*dr][col+i*dc])
		if dr == 0: #horizontal,eliminate left & right
			self.eliminateFill(midr+dr,midc+dc,dr,dc,endc-midc) 
			self.eliminateFill(midr-dr,midc-dc,-dr,-dc,midc-col)
		elif dc == 0: #vertical,eliminate up & down
			self.board[midr][midc].seen = True
			self.eliminateFill(midr+dr,midc+dc,dr,dc,midr-endr) 
			self.eliminateFill(midr-dr,midc-dc,-dr,-dc,row-midr)

	def partialDrop(self,x0,y0,drow,dcol,l): #for vertical lines
		#if there's a special element that's not used, drop it as far as it can
		x1,y1 = x0+(l-1)*drow,y0
		if x1<x0:
			x0,y0,x1,y1 = x1,y1,x0,y0
			drow,dcol = -drow,-dcol #search from bottom
		j = 0 #count the num of special element
		for i in range(l): #search from bottom to top
			row,col = x0+i*drow,y0
			elem = self.board[row][col]
			if elem.dscp=="NT":
				self.board[x0+j][y0]=elem
				elem.locate(x0+j,y0)
				j+=1
			elif elem.spec!=None: #special
				if not elem.used:#drop the special
					if not elem.seen:
						self.board[x0+j][y0] = elem
						elem.locate(x0+j,y0)
						elem.seen = True #activated, ready to use
						j+=1
					else: #should be eliminated
						elem.used = True
						self.special.append(elem)
		return j

	def double3Eliminate(self,row,col):
		for c in [col-1,col,col+1]:#eliminate three columns of length 3
			if c<0 or c>=self.col: continue #check bound
			l = min(self.row-1+self.scroll,row+1)-max(0,row-1)+1
			self.eliminateFill(max(0,row-1),c,1,0,l)

	def Eliminate4(self,row,col): #changes the outer border completely
		self.eliminateFill(self.scroll,0,1,0,self.row)
		self.eliminateFill(self.scroll,self.col-1,1,0,self.row)
		self.eliminateFill(self.scroll,0,0,1,self.col)
		self.eliminateFill(self.row+self.scroll-1,0,0,1,self.col)
		#eliminate the special element as well (unlike the other 2 special)
		self.eliminateFill(row+self.scroll,col,0,1,1)

	def Eliminate5(self,row,col):
		#eliminate the whole row(lenth=col)
		self.eliminateFill(row,0,0,1,self.col)

	def specialEliminate(self,cell):
		if cell.spec == "L": #double 3
			self.double3Eliminate(cell.row,cell.col)
		elif cell.spec == "4": #4 combo
			self.Eliminate4(cell.row,cell.col)
		elif cell.spec == "5": #5 combo
			self.Eliminate5(cell.row,cell.col)

	def verticalEliminateFill(self,x0,y0,drow,dcol,l):
		x1,y1 = x0+(l-1)*drow,y0+(l-1)*dcol #the other end
		d = self.partialDrop(x0,y0,drow,dcol,l)	#drop NT & special
		for j in range(min(x0,x1)+d,self.row-(l-d)+self.scroll):
			#deal with non-NT and non-special elems
			self.board[j][y0] = self.board[j+(l-d)][y0]
			self.board[j][y0].locate(j,y0)
			if (self.board[j+(l-d)][y0].dscp!="NT" 
				and self.board[j+(l-d)][y0].spec!=None):
				self.relocateSpecial(j+(l-d),y0,j,y0)
		for row in range(self.row-(l-d)+self.scroll,self.row+self.scroll):
			#generate new ones at the top
			self.board[row][y0] = a.Accm(row,y0,randint(0,len(feed)-1))

	def horizontalEliminateFill(self,x0,y0,drow,dcol,l):
		x1,y1 = x0+(l-1)*drow,y0+(l-1)*dcol #the other end
		ref = self.board[x0][y0].dscp
		for i in range(l): #loop over each elem in the row
			col = y0+i*dcol
			if self.board[x0][col].dscp=="NT" or  self.board[x0][col].dscp!=ref:
				continue
			elif self.board[x0][col].spec!=None:#keep unused special
				special = self.board[x0][col]
				if not special.used: #activiated/just created, not used
					if not special.seen: #just created
						special.seen = True
						continue
					else: #activated, this is the time to use
						special.used = True
						self.special.append(special) 
			for row in range(x0,self.row-1+self.scroll):
				self.board[row][col] = self.board[row+1][col]
				self.board[row][col].locate(row,col)
				if (self.board[row+1][col].dscp!="NT"
					and self.board[row+1][col].spec!=None):
					self.relocateSpecial(row+1,col,row,col)
			self.board[self.row+self.scroll-1][col]=a.Accm(self.row-1+self.scroll,
													col,randint(0,len(feed)-1))

	def eliminateFill(self,x0,y0,drow,dcol,l):
		if not self.startToEliminate: #record the original board
			self.tempboard = copy.deepcopy(self.board)
			self.startToEliminate = True
		for i in range(l):
			#record the position of ones just eliminated(for graphic effect)
			self.cancel.append(self.board[x0+i*drow][y0+i*dcol])
		x1,y1 = x0+(l-1)*drow,y0+(l-1)*dcol #the other end
		if dcol == 0: #a vertical line
			self.verticalEliminateFill(x0,y0,drow,dcol,l)
		elif drow == 0: #a horizontal line
			self.horizontalEliminateFill(x0,y0,drow,dcol,l)
		#recursively eliminate all available special elements (ugh)
		if len(self.special)==0:
			return
		else:
			row,col = self.special[0].row,self.special[0].col
			cell = self.special.pop(0) #remove used special
			self.specialEliminate(cell) #deal with special elimination

	def debugPrint(self,x0,y0,x1,y1,dx,dy,l):
		for i in range(l):
			print(self.board[x0+dx*i][y0+dy*i],end=" ")
	
	def relocateSpecial(self,prevrow,prevcol,currow,curcol):
		#update the position of special elements
		for accm in reversed(self.special):
			if accm.row == prevrow and accm.col == prevcol:
				accm.locate(currow,curcol)
				break

	def scrollBoard(self): #for endless mode to override
		pass

	def canSwitch(self): #check if there's a possible move by switching elems
		moved = False
		for row in range(self.row+self.scroll):
			for col in range(self.col):
				for (drow,dcol) in [( 0,+1),(+1, 0),(0,-1),(-1,0)]:
					row1,col1 = row+drow,col+dcol
					if (row1<self.scroll or col1<0 or row1>=self.row+self.scroll 
						or col1>=self.col): #out of bound
						continue 
					temp = self.board[row][col] #switch
					self.board[row][col] = self.board[row1][col1]
					self.board[row1][col1] = temp
					self.board[row][col].locate(row,col) #update the position
					self.board[row1][col1].locate(row1,col1)
					if self.search()!=None: #try to move elements around
						moved = True
					temp = self.board[row][col] #undo
					self.board[row][col] = self.board[row1][col1]
					self.board[row1][col1] = temp
					self.board[row][col].locate(row,col)
					self.board[row1][col1].locate(row1,col1)
		return moved

	def playerCanMove(self): #check if there's a move can be made by the NT
		moved = False
		for NT in reversed(self.NT): #see if the user can move
			x,y = NT.row, NT.col
			for (drow, dcol) in [(-1,0),(-1,-1),(-1,+1),
								 (0,-1),         (0,+1),
								 (+1,0),(+1,-1),(+1,+1)]:
				if (x+drow<self.scroll or y+dcol<0 
					or x+drow>=self.row+self.scroll or y+dcol>=self.col):
					continue
				if self.board[x+drow][y+dcol].dscp=="NT": continue
				if self.board[x+drow][y+dcol].dscp == NT.feedtype:
					moved = True	
		return moved	

	def hasMove(self): #check if the player can move; if not, game over
		if self.canSwitch() or self.playerCanMove():
			return True

	def timerFired(self,dt):
		init_interval = 120 #how often a new NT is generated
		if self.gameover:
			self.finish("lost")
			return
		elif len(self.accmed) == self.target:
			self.finish("win")
			self.recordUpdate() #just recording... doesn't show it at last
			return
		if not self.hasMove(): #no move, refresh the board
			self.refreshBoard()
			return
		self.timerCount += 1
		if self.timerCount == self.limit: self.gameover = True
		if self.timerCount!=0 and self.timerCount%init_interval==0: 
			self.initPlayer()
		self.check3s()
		if not self.eliminating: #NT can't move until all 3s are cleared
			self.startToEliminate = False #prepare for another round
			self.movePlayer()
		self.update()

	def refreshBoard(self):
		#Note: the popup won't last long,but so the player know it's refreshing
		msg = Label(text='Refreshing...')
		popup = Popup(title='No More Moves',content=msg,
			size_hint=(.8,.5),auto_dismiss=False,background='img/2.jpg')
		popup.open()
		#since it's only used in the survival mode, self.scroll can be ignored
		for row in range(self.row):
			for col in range(self.col):
				#keep the NT and the specials
				if (self.board[row][col].dscp=="NT" 
					or self.board[row][col].spec!=None): continue
				self.board[row][col] = a.Accm(row,col,randint(0,len(feed)-1))
		self.tempboard = copy.deepcopy(self.board) #reset the tempboard
		self.update() #graphically show it
		popup.dismiss() #close the popup

	def movePlayer(self):
		for NT in reversed(self.NT):
			NT.feed(self.board,self.special,self.scroll)
			if NT.row == self.row-1: #reaches the end
				self.accmed.append(NT) #achievement+1
				self.board[NT.row][NT.col]=a.Accm(NT.row,NT.col,
														randint(0,len(feed)-1))
				self.NT.remove(NT)
				self.initPlayer()

	def recordUpdate(self): #record the best score
		#but it's not shown in the program
		if len(self.accmed)> record["survival"][0]:
			record["survival"] = [len(self.accmed),self.timerCount]
		elif (len(self.accmed)==record["survival"][0] 
			and self.timerCount<record["survival"][1]):
			record["survival"] = [len(self.accmed),self.timerCount]	

	def finish(self,result):
		Clock.unschedule(self.timerFired)
		for key in temp: #can't play a game that's over...
			temp[key] = None
		layout = BoxLayout(orientation="vertical")
		if result == "lost": #game over
			msg = Label(text="You accomodated %d/%d NT, too bad!" 
				% (len(self.accmed),self.target))
			title='Game over'
		elif result == "win": #player wins
			msg = Label(text="You accomodated %d/%d NT; great job!" 
				% (len(self.accmed),self.target))
			title='You won'
		back = Button(text="Back",background_down='img/bt_bk.png')
		restart = Button(text="Restart",background_down='img/bt_bk.png')
		layout.add_widget(msg)
		layout.add_widget(back)
		layout.add_widget(restart)
		popup = Popup(title=title,content=layout,size_hint=(.5,.5),
			auto_dismiss=False,background='img/2.jpg')
		back.bind(on_release=popup.dismiss) #close the popup
		back.bind(on_release=self.return_f) #load board & resume game
		restart.bind(on_release=popup.dismiss)
		restart.bind(on_release=self.reset_func) #start with a new one
		popup.open()

	def return_f(self,instance):
		#pause the game
		Clock.unschedule(self.timerFired)
		self.gameover = False
		#tell the screen(root) to pause
		self.root.return_func(instance)
		return

	def reset_func(self,instance): #restart the game
		self.init()