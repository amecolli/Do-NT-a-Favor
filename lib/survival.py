from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.clock import Clock
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.button import Button

import lib.board as b
import lib.home as home
import lib.story as story

feeddic = {1:'c',2:'d',3:'e'}

temp = {'board':None, #store the game to resume in future
		'NT':None,
		'switch':None,
		'cancel':None,
		'special':None,
		'accmed':None,
		'scroll':None,
		'eliminating':None,
		'pause':None,
		'gameover':None,
		'time':None,
		'mode':None}

class SurvivalScreen(Screen):
	
	def on_pre_enter(self): #prepare the board before entering
		self.clear_widgets()
		layout = FloatLayout()
		self.back_button = Button(pos_hint={'right':.8,'top':.2},
			size_hint=(.08,.1067),background_normal='img/back_normal.png',
			background_down='img/back_down.png')
		self.back_button.bind(on_release=self.try_return)
		self.setting_button = Button(pos_hint={'right':.8,'top':.9},
			size_hint=(.08,.1067),background_normal='img/setting_normal.png',
			background_down='img/setting_down.png')
		self.setting_button.bind(on_release=self.setting_func)
		self.board = b.Board(story.selected_NT)

		if temp['board']!= None and temp['mode']=="survival": #game unfinished
			self.askForResume() #ask the player whether to resume or not

		self.board.root = self
		self.add_widget(self.board)
		layout.add_widget(self.back_button)
		layout.add_widget(self.setting_button)
		self.add_widget(layout)
		home.prevScreen.append("survival") #record visited screen

	def askForResume(self): #a popup window
		Clock.unschedule(self.board.timerFired) #stop game
		layout = BoxLayout(orientation="vertical")
		msg = Label(text="Do you wish to resume the previous game?")
		resume = Button(text="Yes",background_down='img/bt_bk.png')
		restart = Button(text="Restart",background_down='img/bt_bk.png')
		layout.add_widget(msg)
		layout.add_widget(resume)
		layout.add_widget(restart)
		popup = Popup(title="Resume?",content=layout,size_hint=(.5,.5),
			auto_dismiss=False,background='img/2.jpg')
		resume.bind(on_release=popup.dismiss) #close the popup
		resume.bind(on_release=self.resume) #load board & resume game
		restart.bind(on_release=popup.dismiss)
		popup.bind(on_dismiss=self.timeCont) #start with a new one
		popup.open()

	def loadBoard(self): #restore unfinished game from memory
		self.board.board = temp['board']
		self.board.NT = temp['NT']
		self.board.switch = temp['switch']
		self.board.cancel = temp['cancel']
		self.board.accmed = temp['accmed']
		self.board.special = temp['special']
		self.board.scroll = temp['scroll']
		self.board.eliminating = temp['eliminating']
		self.board.pause = temp['pause']
		self.board.gameover = temp['gameover']
		self.board.timerCount = temp['time']
		for row in range(len(self.board.board)):
			for col in range(len(self.board.board[0])):
				elem = self.board.board[row][col]
				if elem.dscp=="NT":
					elem.selected=story.selected_NT
					elem.feedtype=feeddic[story.selected_NT]
		for NT in self.board.NT:
			NT.selected=story.selected_NT
			NT.feedtype=feeddic[story.selected_NT]

	def on_leave(self): #stop updates & clear records
		Clock.unschedule(self.board.timerFired)
		if self.manager.current=='home': #erase any game if the player returns
			for key in temp:
				temp[key] = None
		else: #goes to the setting screen.etc
			temp['board'] = self.board.board
			temp['scroll'] = self.board.scroll
			temp['NT'] = self.board.NT
			temp['switch'] = self.board.switch
			temp['cancel'] = self.board.cancel
			temp['accmed'] = self.board.accmed
			temp['special'] = self.board.special
			temp['eliminating'] = self.board.eliminating
			temp['pause'] = self.board.pause
			temp['gameover'] = self.board.gameover
			temp['time'] = self.board.timerCount
			temp['mode'] = "survival"
		self.clear_widgets()

	def timeCont(self,instance):
		Clock.schedule_interval(self.board.timerFired,.5)

	def resume(self,instance):
		self.loadBoard()

	def pause_callback(self):
		layout = BoxLayout(orientation="vertical")
		msg = Label(text="Do you wish to resume the previous game?")
		resume = Button(text="Yes",background_down='img/bt_bk.png')
		restart = Button(text="Restart",background_down='img/bt_bk.png')
		layout.add_widget(msg)
		layout.add_widget(resume)
		layout.add_widget(restart)
		popup = Popup(title="Resume?",content=layout,size_hint=(.5,.5),
			auto_dismiss=False,background='img/2.jpg')
		resume.bind(on_release=popup.dismiss) #close the popup
		resume.bind(on_release=self.resume) #load board & resume game
		restart.bind(on_release=popup.dismiss)
		restart.bind(on_release=self.reset_func) #start with a new one
		popup.open()

	def try_return(self,instance):
		Clock.unschedule(self.board.timerFired) #stop game
		layout = BoxLayout(orientation="vertical")
		msg = Label(text="Are you sure to leave the curret game?")
		leave = Button(text="Yes",background_down='img/bt_bk.png')
		stay = Button(text="No",background_down='img/bt_bk.png')
		layout.add_widget(msg)
		layout.add_widget(leave)
		layout.add_widget(stay)
		popup = Popup(title="Resume?",content=layout,size_hint=(.5,.5),
			auto_dismiss=False,background='img/2.jpg')
		leave.bind(on_release=popup.dismiss) #close the popup
		leave.bind(on_release=self.return_func) #return to the home screen
		stay.bind(on_release=popup.dismiss)
		stay.bind(on_release=self.timeCont) #continue the current game
		popup.open()

	def return_func(self,instance): #back to home screen
		self.manager.transition.direction='right'
		self.manager.current="home"

	def setting_func(self,instance): #go to settings
		self.manager.transition.direction='left'
		self.manager.current='setting'