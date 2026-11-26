import os 
os.environ['KIVY_GL_BACKEND'] = 'angle_sdl2'

from kivy.config import Config

Config.set("graphics", "width", "1280")
Config.set("graphics", "height", "720")
Config.set("graphics", "minimum_width", "1024")
Config.set("graphics", "minimum_height", "600")

from ui.app import SupervisorioApp

if __name__ == "__main__":
    SupervisorioApp().run()