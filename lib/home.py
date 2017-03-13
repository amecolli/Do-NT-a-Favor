from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.label import Label
from kivy.uix.popup import Popup

prevScreen = ["home"] #record visited screens for back functionality

class HomeScreen(Screen):
	def on_pre_enter(self): #show about page(a popup)
		about = Button(pos_hint={'right':.2,'top':.9},size_hint=(.08,.1067),
			background_normal='img/about_normal.png',
			background_down='img/about_normal.png')
		aboutcontent = BoxLayout(orientation='vertical')
		about_text = self.readFile('src/about.txt')
		info = Label(text=about_text,halign='center')
		close = Button(text="x",background_down='img/bt_bk.png',size_hint=(.1,.1),
			pos_hint={'x':.9,'y':1})
		aboutcontent.add_widget(info)
		aboutcontent.add_widget(close)
		popup = Popup(title='About',content=aboutcontent,size_hint=(.6,.6),
			background='img/2.jpg')
		about.bind(on_release=popup.open) #click "about" to open
		close.bind(on_release=popup.dismiss) #click "close" to close
		#Note: this popup can also be dismissed by clicking outside of it
		self.add_widget(about)
		prevScreen.append('home')

	def readFile(self,path):
	    with open(path, "rt") as f:
	        return f.read()