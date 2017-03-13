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

import lib.accm as a
import lib.board as b

class EndlessBoard(b.Board): #board for endless mode

	global feed, cwidth, cheight, theme_y, selected_NT

	def __init__(self,snum,**kwargs):
		super(EndlessBoard,self).__init__(snum,**kwargs)
		self.scrollRow = self.row-4+self.scroll #when player@a row above,scroll

	def scrollBoard(self):
		for newR in range(self.scroll+self.row-len(self.board)):
			self.board.append([None]*self.col)
		for row in range(self.row,self.row+self.scroll):
			for col in range(self.col):
				i = randint(0,len(feed)-1)
				self.board[row][col] = a.Accm(row,col,i)
		#self.tempboard = copy.deepcopy(self.board)
		self.update()

	def timerFired(self,dt):
		if not self.hasMove(): self.gameover = True
		if self.gameover:
			self.finish()
			self.recordUpdate()
			return
		self.timerCount += 1
		self.check3s()
		if not self.eliminating: #NT can't move until all 3s are cleared
			canScroll=False
			dscroll=0
			for NT in reversed(self.NT):
				NT.feed(self.board,self.special,self.scroll)
				if NT.row>self.scrollRow+self.scroll:#check if should scroll
					canScroll = True
					if NT.row-self.scrollRow>dscroll:
						dscroll = NT.row-self.scrollRow
				elif NT.row<dscroll:#all NT should be still in view after scroll
				#this will not be the case because there's only 1 player
					canScroll = False
			if canScroll: 
				self.scroll = dscroll
				self.scrollBoard()
		self.update()

	def recordUpdate(self): #record the best try
		#like the survival mode, it's not shown
		if self.NT==[]: return
		if self.NT[0].row > b.record["survival"][0]:
			b.record["endless"] = [self.NT[0],self.timerCount]
		elif (self.NT[0].row==b.record["survival"][0] 
			and self.timerCount<b.record["survival"][1]):
			b.record["endless"] = [self.NT[0].row,self.timerCount]

	def finish(self):
		Clock.unschedule(self.timerFired)
		for key in temp: #can't play a game that's over...
			temp[key] = None
		layout = BoxLayout(orientation="vertical")
		if self.NT==[]: 
			msg=Label(text="Out of moves after 0 steps forward!")
		else:
			msg = Label(text="Out of moves after %d steps forward!"
				%self.NT[0].row)
		back = Button(text="Back",background_down='img/bt_bk.png')
		restart = Button(text="Restart",background_down='img/bt_bk.png')
		layout.add_widget(msg)
		layout.add_widget(back)
		layout.add_widget(restart)
		popup = Popup(title="Game over",content=layout,size_hint=(.5,.5),
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

	def reset_func(self,instance):
		self.init()

	def update(self):#similar to the update func of Board
		#with fewer peripherals, but with scroll
		self.canvas.clear()
		with self.canvas:
			if self.cancel == []:
				for row in range(self.scroll,self.row+self.scroll):
					for col in range(self.col):
						elem = self.board[row][col]
						elem.draw(self.scroll)
			else:
				for row in range(self.scroll,self.row+self.scroll):
					for col in range(self.col):
						elem = self.tempboard[row][col] #use the unchanged board
						if elem in self.cancel:
							Color(*(1,1,1,1))
							Ellipse(pos=(self.margin+col*self.cellWidth,
								self.margin+(row-self.scroll)*self.cellHeight),
								size=(self.cr,self.cr),source='img/cancel.png')
						else: elem.draw(self.scroll)
				self.cancel = []
		self.tempboard = copy.deepcopy(self.board)
	def update(self):#similar to the update func of Board
		#with fewer peripherals, but with scroll
		self.canvas.clear()
		with self.canvas:
			if self.cancel == []:
				for row in range(self.scroll,self.row+self.scroll):
					for col in range(self.col):
						elem = self.board[row][col]
						elem.draw(self.scroll)
			else:
				for row in range(self.scroll,self.row+self.scroll):
					for col in range(self.col):
						elem = self.tempboard[row][col] #use the unchanged board
						if elem in self.cancel:
							Color(*(1,1,1,1))
							Ellipse(pos=(self.margin+col*self.cellWidth,
								self.margin+(row-self.scroll)*self.cellHeight),
								size=(self.cr,self.cr),source='img/cancel.png')
						else: elem.draw(self.scroll)
				self.cancel = []
		self.tempboard = copy.deepcopy(self.board)