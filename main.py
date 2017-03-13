from kivy.app import App
from kivy.lang import Builder
from kivy.config import Config
from kivy.core.window import Window

import lib.accm as a
import lib.nt as nt
import lib.board as b
import lib.endless as eb
import lib.setting as setting
import lib.home as home
import lib.survival as survival
import lib.endlesss as endless
import lib.story as story

#call on_pause when the window's minimized
Config.set('kivy','pause_on_minimize',1)
#the window is not resizable
Config.set('graphics','resizable',0)

cwidth,cheight = Window.size

presentation = Builder.load_file('main.kv')

class MainApp(App):

	icon = 'img/icon.png'

	def build(self):
		Window.bind(on_resize=self._update_rect)
		return presentation

	def on_pause(self):
		if setting.sound.state=="play":
			self.stopTime = setting.sound.get_pos()
			setting.sound.stop()
			self.soundOn = True
		else:
			self.soundOn = False
		return True

	def on_resume(self):
		if self.soundOn:
			setting.sound.play()
			setting.sound.seek(self.stopTime)

	def _update_rect(self,window,width,height):
		self.root.width = width
		global cwidth
		cwidth = width
		self.root.height = height
		global cheight
		cheight = height

if __name__ == '__main__':
	MainApp().run()