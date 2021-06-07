from direct.gui.DirectGui import *
from direct.gui.OnscreenText import OnscreenText
from direct.showbase.DirectObject import DirectObject
from direct.showbase.ShowBase import ShowBase
from panda3d.core import *

from Code.LoadModels import *
from Code.SharedCode import *
from Code.UI import *


class Game(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        game_window_settings(self)
        game_window_name(self,'Level Editor')
        
        #=========================================================================
        # Important variables
        #=========================================================================   
        self.gridWidth = 20
        self.gridLength = 20
        self.colorWall = [1, 1, 1, 1]
        self.colorFloor = [0.8, 0.8, 1.0, 1]
        self.colorScaleSelected = [0.8, 1, 0.8, 1]
        self.currentTarget = None
        self.UIContextOptions = contextOptions()
        self.currentContext = None
        self.levelName = 'newLevel'
        
        #=========================================================================
        # Camera
        #=========================================================================
        self.disableMouse()  # Disable the default camera control
        self.camera.setPos(self.gridWidth*2/2,self.gridLength*2/2,100)
        self.camera.setHpr(0, -90, 0)

        #=========================================================================
        # GUI
        #=========================================================================
        self.messageTop = OnscreenText(text='welcome! The level is currently filled up with walls.',
                                pos = (0.0, 0.8), scale=0.06,
                                fg = (0.85, 0.85, 0.85, 1), align = TextNode.ACenter, mayChange=1)
        frameRightMenu = DirectFrame(frameColor =( 0.75, 0.75, 0.75, 1), frameSize = (-0.25, .2, -1, 1),
                                pos=(1, 0, 0))
        buttonClearMouse = DirectButton(parent = frameRightMenu, text = 'clear mouse',
                                pos = (-0.02, 0, 0.65), scale = 0.05, frameSize = (-4.5, 4.5, -0.5, 1),
                                command = self.command_set_context,
                                extraArgs = [None])
        buttonPlaceWall = DirectButton(parent = frameRightMenu, text = 'place wall',
                                pos = (-0.02, 0, 0.55), scale = 0.05, frameSize = (-4.5, 4.5, -0.5, 1),
                                command = self.command_set_context,
                                extraArgs = [self.UIContextOptions.placeWall])
        buttonPlaceFloor = DirectButton(parent = frameRightMenu, text = 'place empty floor',
                                pos = (-0.02, 0, 0.45), scale = 0.05, frameSize = (-4.5, 4.5, -0.5, 1),
                                command = self.command_set_context,
                                extraArgs = [self.UIContextOptions.placeFloor])
        buttonPlaceStart = DirectButton(parent = frameRightMenu, text = 'place start',
                                pos = (-0.02, 0, 0.35), scale = 0.05, frameSize = (-4.5, 4.5, -0.5, 1),
                                command = self.command_set_context,
                                extraArgs = [self.UIContextOptions.placeStart])
        buttonPlaceExit = DirectButton(parent = frameRightMenu, text = 'place exit',
                                pos = (-0.02, 0, 0.25), scale = 0.05, frameSize = (-4.5, 4.5, -0.5, 1),
                                command = self.command_set_context,
                                extraArgs = [self.UIContextOptions.placeExit])
        buttonPlaceRabbit = DirectButton(parent = frameRightMenu, text = 'place rabbit',
                                pos = (-0.02, 0, 0.15), scale = 0.05, frameSize = (-4.5, 4.5, -0.5, 1),
                                command = self.command_set_context,
                                extraArgs = [self.UIContextOptions.placeRabbit])
        buttonExportBam = DirectButton(parent = frameRightMenu, text = 'export to .bam',
                                pos = (-0.02, 0, -0.25), scale = 0.05, frameSize = (-4.5, 4.5, -0.5, 1),
                                command = self.command_set_context,
                                extraArgs = [self.UIContextOptions.exportBam])
        buttonImportBam = DirectButton(parent = frameRightMenu, text = 'import .bam',
                                pos = (-0.02, 0, -0.35), scale = 0.05, frameSize = (-4.5, 4.5, -0.5, 1),
                                command = self.command_set_context,
                                extraArgs = [self.UIContextOptions.importBam])
        self.entryLevelName = DirectEntry(parent = frameRightMenu, text = '', initialText = self.levelName,
                                frameColor = (0.9, 0.9, 0.9, 1), width = 8, cursorKeys = 1,
                                pos = (-0.2125, 0, -0.15), scale = 0.05, frameSize = (-0.5, 8, -0.5, 1),
                                command = self.command_set_levelname,
                                focusOutCommand = self.command_set_levelname_focus_out)
            
        #=========================================================================
        # Collision Traverser and Collision Handler
        #=========================================================================
        base.cTrav=CollisionTraverser()
        collisionHandler = CollisionHandlerEvent()

        #=========================================================================
        # Load the models and assign collision geometry
        #=========================================================================
        self.terrainNodePath = NodePath(PandaNode('terrain'))
        self.terrainNodePath.reparentTo(self.render)
        for x in range(self.gridWidth):
            for y in range(self.gridLength):
                posV3 = Vec3(x*2,y*2,0)
                blockModel = load_cube(self.terrainNodePath,posV3)
                if x == 0 or x+1 == self.gridWidth or y == 0 or y+1 == self.gridLength:
                    blockModel.setColorScale(1.0,0.6,0.6,1)
                    blockModel.find('blockcnode').removeNode()
                blockModel.name = 'wall'

        #=========================================================================
        # Collision Ray, for object picking
        #=========================================================================
        # Used to know what object the mouse is pointing at
        # A task will be set to update it's position every frame
        pickerNode=CollisionNode('mouseraycnode')
        pickerNP=base.camera.attachNewNode(pickerNode)
        pickerRay=CollisionRay()
        pickerNode.addSolid(pickerRay)
        base.cTrav.addCollider(pickerNP, collisionHandler)

        #=========================================================================
        # Generating events with CollisionHandlerEvent
        #=========================================================================
        # https://docs.panda3d.org/1.10/python/programming/collision-detection/collision-handlers#collisionhandlerevent
        collisionHandler.addInPattern('%fn-into-%in')
        collisionHandler.addOutPattern('%fn-out-%in')

        #=========================================================================
        # Generating mouse events
        #=========================================================================
        # https://docs.panda3d.org/1.10/python/programming/hardware-support/mouse-support
        # The mouse click event is already automatically generated
        # We just have to define a function and attach it to the 'mouse1' event (left mouse button)           
        
        #=========================================================================
        # attaching the functions to their events
        #=========================================================================
        # DirectObject, because that class can respond to events
        # https://docs.panda3d.org/1.10/python/_modules/direct/showbase/DirectObject
        # The event functions are below, this still is the __init__ function
        self.eventHandlerDO = DirectObject()
        self.eventHandlerDO.accept('mouseraycnode-into-blockcnode', self.event_collide_in)
        self.eventHandlerDO.accept('mouseraycnode-out-blockcnode', self.event_collide_out)
        #** This is how we interact with mouse clicks - see the mousePick function above for details
        self.eventHandlerDO.accept('mouse1', self.event_mouse1_down)

        #=========================================================================
        # task to update the ray position
        #=========================================================================
        # https://docs.panda3d.org/1.10/python/programming/tasks-and-events/tasks
        # We want the ray to be in the same place as the mouse is on the screen
        # Ray points straight into the screen
        def rayupdate(task):
            if base.mouseWatcherNode.hasMouse():
                mousePosition = base.mouseWatcherNode.getMouse()
                pickerRay.setFromLens(base.camNode, mousePosition.getX(),mousePosition.getY())        
            return task.cont

        #=========================================================================
        #add the task to task manager
        #=========================================================================
        #https://docs.panda3d.org/1.10/python/programming/tasks-and-events/tasks#the-task-manager
        taskMgr.add(rayupdate, "updatePicker")
    
    #=========================================================================
    # unsorted functions
    #=========================================================================
    def clean_string(self,newString):
        result = ''
        for character in newString:
            if character.isalnum():
                result += character
        return result
    
    def export_to_bam(self):
        path = 'Levels/- new -'
        name = self.clean_string(self.entryLevelName.get())+'.bam'
        filename = Filename(path,name)
        filename.standardize()
        filename.makeDir()
        exportTerrain = NodePath(PandaNode('export'))
        self.terrainNodePath.copyTo(exportTerrain)
        for c in exportTerrain.getChild(0).children:
            c.find('cube text').removeNode()
        exportTerrain.getChild(0).writeBamFile(filename)
        return f'exported to {filename}'
    
    def import_from_bam(self):
        path = 'Levels/- new -'
        name = self.clean_string(self.entryLevelName.get())+'.bam'
        filename = Filename(path,name)
        try:
            newLevel = loader.loadModel(filename)
            self.terrainNodePath.removeNode()
            self.terrainNodePath = NodePath(PandaNode('terrain'))
            for wall in newLevel.findAllMatches('wall'):
                blockModel = load_cube(self.terrainNodePath,wall.getPos())
                x = wall.getX()
                y = wall.getY()
                if x == 0 or x == (self.gridWidth-1)*2 or y == 0 or y == (self.gridLength-1)*2:
                    blockModel.setColorScale(1.0,0.6,0.6,1)
                    blockModel.find('blockcnode').removeNode()
                self.place_wall(blockModel)
            for floor in newLevel.findAllMatches('floor'):
                blockModel = load_cube(self.terrainNodePath,floor.getPos())
                self.place_floor(blockModel)
            for start in newLevel.findAllMatches('start'):
                blockModel = load_cube(self.terrainNodePath,start.getPos())
                self.place_start(blockModel)
            for levelexit in newLevel.findAllMatches('exit'):
                blockModel = load_cube(self.terrainNodePath,levelexit.getPos())
                self.place_exit(blockModel)
            for rabbit in newLevel.findAllMatches('rabbit'):
                blockModel = load_cube(self.terrainNodePath,rabbit.getPos())
                self.place_rabbit(blockModel)
            self.terrainNodePath.reparentTo(self.render)
            return f'imported {filename}'
        except:
            return f'could not import {filename}'        
            
    def place_level_element(self,np):
        if self.currentContext == None:
            return
        elif self.currentContext == str(self.UIContextOptions.placeFloor):
            self.place_floor(self.currentTarget)
        elif self.currentContext == str(self.UIContextOptions.placeWall):
            self.place_wall(self.currentTarget)
        elif self.currentContext == str(self.UIContextOptions.placeRabbit):
            self.place_rabbit(self.currentTarget)
        elif self.currentContext == str(self.UIContextOptions.placeStart):
            self.place_start(self.currentTarget)
        elif self.currentContext == str(self.UIContextOptions.placeExit):
            self.place_exit(self.currentTarget)
        else:
            print(f'place_level_element context {self.currentContext} not implemented')  
        
    def place_floor(self,np):
        np.setColor(*self.colorFloor)
        np.setPos(np.getX(), np.getY(), -1.5)
        np.find('cube text').node().setText('')
        np.name = 'floor'
    
    def place_wall(self,np):
        np.setColor(*self.colorWall)
        np.setPos(np.getX(), np.getY(), 0)
        np.find('cube text').node().setText('')
        np.name = 'wall'
    
    def place_rabbit(self,np):
        np.setColor(*self.colorFloor)
        np.setPos(np.getX(), np.getY(), -1.5)
        np.find('cube text').node().setText('rabbit')
        np.name = 'rabbit'
    
    def place_start(self,np):
        np.setColor(*self.colorFloor)
        np.setPos(np.getX(), np.getY(), -1.5)
        np.find('cube text').node().setText('start')
        np.name = 'start'    
        
    def place_exit(self,np):
        np.setColor(*self.colorFloor)
        np.setPos(np.getX(), np.getY(), -1.5)
        np.find('cube text').node().setText('exit')
        np.name = 'exit'    
        
    def set_top_message_text(self,newText):    
        self.messageTop.setText(newText)
        
    #=========================================================================
    # commands for the GUI elements
    #=========================================================================
    def command_set_context(self,newContext = None):
        if newContext is None:
            self.currentContext = None
        else:
            if hasattr(self.UIContextOptions,newContext):
                self.currentContext = newContext
            else:
                print(f'{newContext} not understood, setting to None')
                self.currentContext = None
        newMessage = 'Currently not placing anything'
        if self.currentContext  == str(self.UIContextOptions.placeWall):
            newMessage = 'Walls are impassable. Click or drag to place.'
        elif self.currentContext  == str(self.UIContextOptions.placeFloor):
            newMessage = 'Floors are walkable areas. Click or drag to place.'
        elif self.currentContext  == str(self.UIContextOptions.placeStart):
            newMessage = 'Player start location. You spawn here.'
        elif self.currentContext  == str(self.UIContextOptions.placeExit):
            newMessage = 'Collect all rabbits and get to an exit to win.'
        elif self.currentContext == str(self.UIContextOptions.placeRabbit):
            newMessage = 'Player must catch all rabbits.'
        elif self.currentContext  == str(self.UIContextOptions.exportBam):
            newMessage = self.export_to_bam()
            self.currentContext = None
        elif self.currentContext == str(self.UIContextOptions.importBam):
            newMessage = self.import_from_bam()
            self.currentContext = None
        self.set_top_message_text(newMessage)
    
    def command_set_levelname(self,entryText):
        cleanName = self.clean_string(entryText)
        self.entryLevelName.set(cleanName)
    
    def command_set_levelname_focus_out(self):
        self.command_set_levelname(self.entryLevelName.get())
                
    #=========================================================================
    # functions to call when events happen
    #=========================================================================
    # FROM ray goes in INTO object
    def event_collide_in(self,entry):
        np_from=entry.getFromNodePath()
        np_into=entry.getIntoNodePath()
        np_into_parent = np_into.getParent()
        np_into_parent.setColorScale(*self.colorScaleSelected)
        self.currentTarget = np_into_parent
        is_down = self.mouseWatcherNode.is_button_down('mouse1')
        if is_down:
            self.place_level_element(np_into_parent)
     
    # FROM ray goes out of INTO object
    def event_collide_out(self,entry):
        np_into=entry.getIntoNodePath()
        np_into_parent = np_into.getParent()
        np_into_parent.setColorScale(1, 1, 1, 1)
        if self.currentTarget == np_into_parent:
            self.currentTarget = None
            
    # Left mouse button clicked
    def event_mouse1_down(self):
        if self.currentTarget:
            self.place_level_element(self.currentTarget)
            

#=========================================================================
# Load the Game() and run it
#=========================================================================
# This code is only executed if this script is run directly
# It will not be executed when the script is imported
if __name__ == '__main__':
    PStatClient.connect()
    game = Game()
    game.run()