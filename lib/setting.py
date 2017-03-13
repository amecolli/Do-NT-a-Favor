from kivy.uix.floatlayout import FloatLayout
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.button import Button
from kivy.core.audio import SoundLoader
from kivy.uix.togglebutton import ToggleButton
from kivy.properties import ObjectProperty,NumericProperty
from kivy.event import EventDispatcher
from kivy.core.window import Window

import lib.home as home

sound = SoundLoader.load('src/MY TURN.mp3') #sound test

class SettingScreen(Screen):

	sound.play()
	sound.loop = True #loops
	#soundOn = "normal"
	stopTime = 0

	def __init__(self,**kwargs):
		super(SettingScreen,self).__init__(**kwargs)
		layout = FloatLayout()
		SoundControl = ToggleButton(state="normal",
			pos_hint={'center_x':.4,'center_y':.5},size_hint=(.15,.2),
			background_normal='img/sound_on.png',
			background_down='img/sound_off.png') #a sound control button (on/off)
		SoundControl.bind(state=self.soundChange)
		NTselect = Button(pos_hint={'center_x':.6,'center_y':.5},
			size_hint=(.15,.2),background_normal='img/NT_normal.png',
			background_down='img/NT_down.png') #a sound control button (on/off)
		NTselect.bind(on_release=self.goToSelect)
		layout.add_widget(SoundControl)
		layout.add_widget(NTselect)
		self.back_button = Button(pos_hint={'right':.9,'top':.2},
			size_hint=(.08,.1067),background_normal='img/back_normal.png',
			background_down='img/back_down.png')
		self.back_button.bind(on_release=self.return_func)
		layout.add_widget(self.back_button)
		self.add_widget(layout)

	def soundChange(self,instance,value):
		if value=="normal":
			sound.play()
			sound.seek(self.stopTime) #resume from where it stopped
		elif value=="down":
			self.stopTime = sound.get_pos() #record the stop position
			sound.stop()

	def goToSelect(self,instance):
		self.manager.transition.direction = 'left'
		self.manager.current = 'story'

	def return_func(self,instance): #back to home screen
		self.manager.transition.direction='right'
		self.manager.current=home.prevScreen[-1]
