from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.clock import Clock
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.button import Button

import lib.home as home
import lib.board as b
import lib.survival as s
import lib.endless as e
import lib.story as story

feeddic = {1:'c',2:'d',3:'e'}

class EndlessScreen(Screen):

	def on_pre_enter(self): #prepare the board before entering
		self.clear_widgets()
		self.back_button = Button(pos_hint={'right':.8,'top':.2},
			size_hint=(.08,.1067),background_normal='img/back_normal.png',
			background_down='img/back_down.png')
		self.back_button.bind(on_release=self.try_return)
		self.setting_button = Button(pos_hint={'right':.8,'top':.9},
			size_hint=(.08,.1067),background_normal='img/setting_normal.png',
			background_down='img/setting_down.png')
		self.setting_button.bind(on_release=self.setting_func)
		self.board = e.EndlessBoard(story.selected_NT)
		if s.temp['board']!= None and s.temp['mode'] == "endless":
			self.askForResume()
		self.board.root = self
		self.add_widget(self.board)
		self.add_widget(self.back_button)
		self.add_widget(self.setting_button)
		home.prevScreen.append("endless")

	def askForResume(self):
		Clock.unschedule(self.board.timerFired)
		layout = BoxLayout(orientation="vertical")
		msg = Label(text="Do you wish to resume the previous game?")
		resume = Button(text="Yes",background_down='img/bt_bk.png')
		restart = Button(text="Restart",background_down='img/bt_bk.png')
		layout.add_widget(msg)
		layout.add_widget(resume)
		layout.add_widget(restart)
		popup = Popup(title="Resume?",content=layout,size_hint=(.5,.5),
			auto_dismiss=False,background='img/2.jpg')
		resume.bind(on_release=popup.dismiss)
		resume.bind(on_release=self.resume)
		restart.bind(on_release=popup.dismiss)
		popup.bind(on_dismiss=self.timeCont)
		popup.open()

	def loadBoard(self):
		self.board.board = s.temp['board']
		self.board.NT = s.temp['NT']
		self.board.switch = s.temp['switch']
		self.board.cancel = s.temp['cancel']
		self.board.accmed = s.temp['accmed']
		self.board.special = s.temp['special']
		self.board.scroll = s.temp['scroll']
		self.board.eliminating = s.temp['eliminating']
		self.board.pause = s.temp['pause']
		self.board.gameover = s.temp['gameover']
		self.board.timerCount = s.temp['time']
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
		if self.manager.current=='home':
			for key in s.temp:
				s.temp[key] = None
		else:
			s.temp['board'] = self.board.board
			s.temp['scroll'] = self.board.scroll
			s.temp['NT'] = self.board.NT
			s.temp['switch'] = self.board.switch
			s.temp['cancel'] = self.board.cancel
			s.temp['accmed'] = self.board.accmed
			s.temp['special'] = self.board.special
			s.temp['eliminating'] = self.board.eliminating
			s.temp['pause'] = self.board.pause
			s.temp['gameover'] = self.board.gameover
			s.temp['time'] = self.board.timerCount
			s.temp['mode'] = "endless"
		self.clear_widgets()	

	def try_return(self,instance):
		Clock.unschedule(self.board.timerFired) #stop game
		layout = BoxLayout(orientation="vertical")
		msg = Label(text="Are you sure to leave the current game?")
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

	def timeCont(self,instance):
		Clock.schedule_interval(self.board.timerFired,.5)

	def resume(self,instance):
		self.loadBoard()

	def return_func(self,instance): #back to home screen
		self.manager.transition.direction='right'
		self.manager.current="home"

	def setting_func(self,instance): #go to settings
		self.manager.transition.direction='left'
		self.manager.current='setting'