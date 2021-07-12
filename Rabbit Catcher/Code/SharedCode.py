from panda3d.core import *

def game_window_settings(self):
    properties = WindowProperties()
    windowWidth = 1200
    windowHeight = 1000
    properties.setSize(windowWidth,windowHeight)
    properties.fixed_size =True
    self.win.requestProperties(properties)        
    #https://docs.panda3d.org/1.10/python/optimization/basic-performance-diagnostics
    self.setFrameRateMeter(True)
    self.render.setShaderAuto()        
    #so stuff doesnt fall through the floor and such while loading
    self.graphicsEngine.renderFrame()
    
def game_window_name(self,newName):
    properties = WindowProperties()
    properties.title = newName
    self.win.requestProperties(properties)
    