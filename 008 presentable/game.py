import os

from direct.gui.DirectGui import *
from direct.gui.OnscreenText import OnscreenText
from direct.showbase.DirectObject import DirectObject
from direct.showbase.ShowBase import ShowBase
from panda3d.ai import *
from panda3d.core import *

from Code.KeyBindings import *
from Code.LoadModels import *
from Code.SharedCode import *
from Code.UI import *

class Game(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        game_window_settings(self)
        game_window_name(self,'Level Editor')
        set_default_input(self)
                        
        #temporary
        #self.disableMouse()  # Disable the default camera control
        self.camera.setPos(20*2/2,20*2/2,100)
        self.camera.setHpr(0, -90, 0)
        
        #=========================================================================
        # GUI
        #=========================================================================
        self.frameOverlay = DirectFrame(frameColor =(1, 1, 1, 0.25), frameSize = (-1.2, 1.2, -1, 1),
                                pos=(0, 0, 0))
        frameLevels = DirectFrame(parent = self.frameOverlay, frameColor =(1, 1, 1, 0.0),
                                frameSize = (-1.2, .8, -1, 1), pos=(0, 0, 0))
        path = 'Levels'
        campaignDict = {}
        for dirPath, dirNames, fileNames in os.walk(path):
            for file in fileNames:
                if (file.endswith('.bam')):
                    levelDirPath = dirPath.replace('\\','/')  
                    if not levelDirPath in campaignDict:
                        campaignDict[levelDirPath] = [file]
                    else:                      
                        levels = campaignDict[levelDirPath]
                        levels.append(file)
                        campaignDict[levelDirPath] = levels
        row = 0
        col = 0
        standardSize = (-4.5, 4.5, -0.5, 1)
        for folder in campaignDict.keys():
            col = 0
            folderLabel = DirectLabel(parent = frameLevels, text = str(folder), frameColor =(1, 1, 1, 0.0),
                                pos = (-0.95+(col*0.5), 0, 0.95-(row*0.1)), scale = 0.05, frameSize = standardSize)
            row +=1
            for level in campaignDict[folder]:
                levelPath = Filename(folder,level)
                levelPath.standardize()  
                buttonLevel = DirectButton(parent = frameLevels, text = str(level),
                                pos = (-0.95+(col*0.5), 0, 0.95-(row*0.1)), scale = 0.05,
                                frameSize = standardSize, command = self.command_load_level,
                                extraArgs = [levelPath])
                col += 1
                if col > 3:
                    row += 1
                    col = 0
            row += 1
            
        self.winMessage = OnscreenText(text='you win!!!  (press esc to play again)', pos = (0, 0), scale = 0.1)
        self.winMessage.hide()
        
        self.rabbitCounter = OnscreenText(text='rabbits remaining', pos=(0.96,0.9), scale = 0.05, mayChange = 1)
        
        keyboardMap = self.win.get_keyboard_map()
        upMap = keyboardMap.get_mapped_button('w')
        downMap = keyboardMap.get_mapped_button('s')
        leftMap = keyboardMap.get_mapped_button('a')
        rightMap = keyboardMap.get_mapped_button('d')
        pMap = keyboardMap.get_mapped_button('p')
        escMap = keyboardMap.get_mapped_button('escape')
        infostring = f'{upMap}: forward\n{downMap}: backwards\n{leftMap}: left\n{rightMap}: right\nMouse to look\n{pMap}: screenshot\n{escMap}: menu'
        self.infoMessage = OnscreenText(text=infostring, pos=(0.98,-0.65), scale = 0.05)
        #=========================================================================
        # Important variables
        #=========================================================================                
        self.levelNodePath = NodePath(PandaNode('level'))
        self.levelNodePath.reparentTo(self.render)
        self.playerSpawnList = []
        self.playerAvatar = None
        self.maskValues = BitMask32(0x01)
        self.paused = False        
        self.toggle_frameOverlay(True)
        self.cTrav = CollisionTraverser()
        self.collisionHandler = CollisionHandlerPusher()
        """
        self.aiWorld = AIWorld(self.render)   
        """
        
        #=========================================================================
        # Generating events with CollisionHandlerEvent
        #=========================================================================
        # https://docs.panda3d.org/1.10/python/programming/collision-detection/collision-handlers#collisionhandlerevent
        self.collisionHandler.addInPattern('%fn-into-%in')
        
        #=========================================================================
        # attaching the event functions to their events
        #=========================================================================
        # DirectObject, because that class can respond to events
        # https://docs.panda3d.org/1.10/python/_modules/direct/showbase/DirectObject
        # The event functions are below, this still is the __init__ function
        self.eventHandlerDO = DirectObject()
        self.eventHandlerDO.accept('playercnode-into-exitcnode', self.event_exit_reached)
        self.eventHandlerDO.accept('playercnode-into-rabbitcnode', self.event_rabbit_caught)
        self.eventHandlerDO.accept('rabbitcnode-into-blockcnode', self.event_rabbit_collide)
        self.eventHandlerDO.accept('rabbitcnode-into-rabbitcnode', self.event_rabbit_collide)
        self.eventHandlerDO.accept('rabbitcnode-into-exitcnode', self.event_rabbit_collide)
        self.eventHandlerDO.accept('rabbitcnode-again-blockcnode', self.event_rabbit_collide)
        
        #=========================================================================
        #add the task to task manager
        #=========================================================================
        #https://docs.panda3d.org/1.10/python/programming/tasks-and-events/tasks#the-task-manager
        taskMgr.add(self.task_input, 'input')
        taskMgr.add(self.task_ai_update, 'ai_update')
        
    def place_exit(self,parent,positionList = []):
        for newPos in positionList:
            load_exit(parent,posV3 = newPos, scaleV3 = Vec3(0.5,0.5,0.5))
            
    def place_player(self,parent, positionList = []):
        randomizer = Randomizer()
        if len(positionList) < 1:
            newPos = Vec3(randomizer.randomInt(20),randomizer.randomInt(20),2.5)
        else:
            index = randomizer.randomInt(len(positionList)-1)
            newPos = Vec3(positionList[index])
        self.playerAvatar = None
        self.playerAvatar, playerCollider = load_player(parent, posV3 = newPos, scaleV3 = Vec3(0.5,0.5,0.5))
        playerCollider.node().setFromCollideMask(self.maskValues)
        self.collisionHandler.addCollider(playerCollider,self.playerAvatar)
        self.cTrav.addCollider(playerCollider, self.collisionHandler)
        
    def place_rabbit(self,parent, positionList = []):
        for newPos in positionList:
            newRabbit,newRabbitCollider = load_rabbit(parent, posV3 = newPos-Vec3(0, 0, 0.25), scaleV3 = Vec3(0.05,0.05,0.05))
            """
            rabbitaiChar = AICharacter('rabbitAI', newRabbit, 100, 0.05, 5)
            rabbitBehaviors = rabbitaiChar.getAiBehaviors()
            #rabbitBehaviors.evade(self.playerAvatar, 10, 20, 0.8)
            rabbitBehaviors.wander(120, 0, 100, 0.2)
            rabbitBehaviors.obstacleAvoidance(0.5)
            """
            newRabbitCollider.node().setFromCollideMask(self.maskValues)
            self.collisionHandler.addCollider(newRabbitCollider,newRabbit)
            self.cTrav.addCollider(newRabbitCollider,self.collisionHandler)            
            """
            self.aiWorld.addAiChar(rabbitaiChar)
            """

        
    def center_mouse(self):
        props = base.win.getProperties()
        self.win.movePointer(0,props.getXSize() // 2,props.getYSize() // 2)
        
    def toggle_confine_mouse_and_hide(self,trueFalse):
        props = WindowProperties()
        props.setCursorHidden(trueFalse)
        if trueFalse:
            props.setMouseMode(WindowProperties.M_confined)
        else:
            props.setMouseMode(WindowProperties.M_absolute)
        self.win.requestProperties(props)
        
    def toggle_frameOverlay(self,trueFalse):
        self.center_mouse()
        self.toggle_confine_mouse_and_hide(not trueFalse)
        self.paused = trueFalse
        if trueFalse:
            self.frameOverlay.show()
            self.rabbitCounter.hide()
        else:
            self.frameOverlay.hide()
            self.rabbitCounter.show()
            
    #=========================================================================
    # commands for the GUI elements
    #=========================================================================
    def command_load_level(self,levelPath):        
        try:
            newLevel = loader.loadModel(levelPath)
        except:
            print('level load failed')
        self.winMessage.hide()
        self.levelNodePath.removeNode()
        self.levelNodePath = newLevel
        self.levelNodePath.setCollideMask(self.maskValues)
        """
        for x in self.levelNodePath.findAllMatches('*'):
            self.aiWorld.addObstacle(x)
        """
        self.playerSpawnList = []
        exitList = []
        rabbitList = []
        offset = Vec3(0,0,1.5)
        for startPoint in newLevel.findAllMatches('start'):
            self.playerSpawnList.append(startPoint.getPos()+offset)
        for exitPoint in newLevel.findAllMatches('exit'):
            exitList.append(exitPoint.getPos()+offset)
        for rabbitPoint in newLevel.findAllMatches('rabbit'):
            rabbitList.append(rabbitPoint.getPos()+offset)            
        self.place_player(self.levelNodePath,self.playerSpawnList)
        self.place_exit(self.levelNodePath,exitList)
        self.place_rabbit(self.levelNodePath,rabbitList)
        self.levelNodePath.reparentTo(self.render)
        self.toggle_frameOverlay(False)
        

    #=========================================================================
    # events
    #=========================================================================
    def event_exit_reached(self,entry):
        if len(self.liveRabbitsList) < 1:
            self.paused = True
            self.winMessage.show()
        
    def event_rabbit_caught(self,entry):
        rabbit = entry.getIntoNodePath().getParent()
        rabbit.removeNode()
        
    def event_rabbit_collide(self,entry):
        rabbit = entry.getFromNodePath().getParent()
        rando = Randomizer()
        rabbit.setH(rabbit,rando.randomInt(45))
        
    def event_key_change(self, controlName, controlState):
        self.inputMap[controlName] = controlState
            
    #=========================================================================
    # tasks for the TaskMgr
    #=========================================================================
    def task_input(self, task):
        #https://docs.panda3d.org/1.10/python/programming/tasks-and-events/tasks
        #return Task.cont    call again next frame
        #return Task.done    dont call again
        #return None         default behavior is to stop in this case
        #return Task.again   call again, after the same delay
        dt = globalClock.getDt()    
        # player controls
        # first person camera based on
        # https://discourse.panda3d.org/t/first-person-camera/12904
        # https://discourse.panda3d.org/t/simple-first-person-game-base/25520
        playerSpeed = 6*dt
        lookSpeed = 18
        if self.playerAvatar and not self.paused: 
            if self.inputMap["up"]:
                self.playerAvatar.setY(self.playerAvatar,playerSpeed)
            if self.inputMap["down"]:
                self.playerAvatar.setY(self.playerAvatar,-playerSpeed)
            if self.inputMap["left"]:
                self.playerAvatar.setX(self.playerAvatar,-playerSpeed)
            if self.inputMap["right"]:
                self.playerAvatar.setX(self.playerAvatar,playerSpeed)
            self.playerAvatar.setPos(Vec3(self.playerAvatar.getX(),self.playerAvatar.getY(),0.5))
            #print(self.playerAvatar.getPos())
            if self.mouseWatcherNode.hasMouse():
                mouseX = self.mouseWatcherNode.getMouseX()
                mouseY = self.mouseWatcherNode.getMouseY()
                if not mouseX == 0:
                    self.playerAvatar.setH(self.playerAvatar.getH()+(-mouseX)*lookSpeed)                
                if self.playerAvatar.getP() < 90 and self.playerAvatar.getP() > -90:
                    self.playerAvatar.setP(self.playerAvatar.getP() + mouseY * lookSpeed)
                # If the camera is at a -90 or 90 degree angle, this code helps it not get stuck.
                else:
                    if self.playerAvatar.getP() > 90:
                        self.playerAvatar.setP(self.playerAvatar.getP() - 1)
                    elif self.playerAvatar.getP() < -90:
                        self.playerAvatar.setP(self.playerAvatar.getP() + 1)                        
            self.center_mouse()
            self.camera.setPos(self.playerAvatar.getPos())
            self.camera.setHpr(self.playerAvatar.getHpr())
        if self.inputMap['spawn']:
            print('spawniewanie')
            self.event_key_change('spawn',False)
        if self.inputMap['screenshot']:
            print('screenshot')
            base.screenshot()
            self.event_key_change('screenshot',False)
        if self.inputMap['menu']:
            self.toggle_frameOverlay(self.frameOverlay.isHidden())
            self.event_key_change('menu',False)
        return task.cont    
    
    def task_ai_update(self,task):
        """
        self.aiWorld.update()
        """
        dt = globalClock.getDt()   
        rabbitSpeed = 4*dt
        self.liveRabbitsList = self.levelNodePath.findAllMatches('pokemon')
        if len(self.liveRabbitsList) > 0:
            self.rabbitCounter.setText(f'rabbits remaining:\n {len(self.liveRabbitsList)}')
        else:
            self.rabbitCounter.setText(f'all rabbits caught!\n find an exit to win')
        for rabbit in self.liveRabbitsList:
            rabbit.setPos(rabbit, Vec3(0,rabbitSpeed,0))
            rabbit.setZ(-0.45)
        return task.cont    

#=========================================================================
# Load the Game() and run it
#=========================================================================
# This code is only executed if this script is run directly
# It will not be executed when the script is imported
if __name__ == '__main__':
    PStatClient.connect()
    game = Game()
    game.run()