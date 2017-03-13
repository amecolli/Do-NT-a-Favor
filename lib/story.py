from kivy.uix.pagelayout import PageLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.event import EventDispatcher
from kivy.properties import ObjectProperty,NumericProperty
from kivy.core.window import Window

import lib.home as home

selected_NT = 1
cwidth,cheight = Window.size

class NT_selection(EventDispatcher):

	SelectNT=NumericProperty(selected_NT)

def NT_callback(instance,value):
	global selected_NT
	selected_NT = value

selected = NT_selection()
selected.bind(SelectNT=NT_callback)

class StoryScreen(Screen): #where the tutoral is

	def __init__(self,**kwargs):
		super(StoryScreen,self).__init__(**kwargs)
		self.layout = PageLayout() #a nice layout to display instructions
		self.setPages() #set all pages in the pagelayout
		self.back_button = Button(pos_hint={'right':.9,'top':.2},
			size_hint=(.08,.1067),background_normal='img/back_t.png',
			background_down='img/back_down.png')
		self.back_button.bind(on_release=self.return_func)
		self.add_widget(self.back_button)

	def loadPlayerPage(self): #initiate the images&buttons for NT selection
		self.player_1_img = Image(source='img/pair1.png',
			pos_hint={"center_x":.3,"center_y":.7})
		self.player_1 = ToggleButton(state="down",group='NT',
			background_normal='img/select_normal.png',
			background_down='img/select_down.png',allow_no_selection=False,
			pos_hint={"center_x":.7,"center_y":.7},
			size_hint=(218/cwidth,77/cheight))
		self.player_2_img = Image(source='img/pair2.png',
			pos_hint={"center_x":.3,"center_y":.5})
		self.player_2 = ToggleButton(state="normal",group='NT',
			background_normal='img/select_normal.png',
			background_down='img/select_down.png',allow_no_selection=False
			,pos_hint={"center_x":.7,"center_y":.5},
			size_hint=(218/cwidth,77/cheight))
		self.player_3_img = Image(source='img/pair3.png',
			pos_hint={"center_x":.3,"center_y":.3})
		self.player_3 = ToggleButton(state="normal",group='NT',
			background_normal='img/select_normal.png',
			background_down='img/select_down.png',allow_no_selection=False,
			pos_hint={"center_x":.7,"center_y":.3},
			size_hint=(218/cwidth,77/cheight))

	def PlayerPage(self): #create the first page
		self.loadPlayerPage()
		NT_select = FloatLayout()
		self.player_1.bind(state=self.callback_1) #change the NT for the game
		self.player_2.bind(state=self.callback_2)
		self.player_3.bind(state=self.callback_3)
		NT_select.add_widget(self.player_1_img)
		NT_select.add_widget(self.player_1)
		NT_select.add_widget(self.player_2_img)
		NT_select.add_widget(self.player_2)
		NT_select.add_widget(self.player_3_img)
		NT_select.add_widget(self.player_3)
		self.layout.add_widget(NT_select)

	def setPages(self): #set all other pages (simple image)
		self.PlayerPage()
		#three pages - basic, special, and mode
		#only one widget allowed on a page
		basic = Button(background_normal='img/basic_t.png',
			background_down='img/basic_t.png')
		special = Button(background_normal='img/special_t.png',
			background_down='img/special_t.png')
		mode = Button(background_normal='img/mode_t.png',
			background_down='img/mode_t.png')
		self.layout.add_widget(basic)
		self.layout.add_widget(special)
		self.layout.add_widget(mode)
		self.add_widget(self.layout)

	#the following methods uses the NumericProperty of Kivy
	#which would call a defined function every time the value changes

	def callback_1(self,instance,value):
		global SelectNT
		if value=="down":
			selected.SelectNT = 1

	def callback_2(self,instance,value):
		global SelectNT
		if value=="down":
			selected.SelectNT = 2

	def callback_3(self,instance,value):
		global SelectNT
		if value=="down":
			selected.SelectNT = 3

	def on_pre_enter(self): #record current screen for back func
		home.prevScreen.append("story")

	def return_func(self,instance):
		self.manager.transition.direction='right'
		self.manager.current="home"