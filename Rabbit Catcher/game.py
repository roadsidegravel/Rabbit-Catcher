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
        game_window_name(self,'Rabbit Catcher')
        set_default_input(self)
                        
        #temporary
        self.disableMouse()  # Disable the default camera control
        self.camera.setPos(20*2/2,20*2/2,100)
        self.camera.setHpr(0, -90, 0)
        self.camLens.setFov(90)
        self.camLens.setNear(0.05)
        #nodePath.setTwoSided(True) for two side rendering
        
        #=========================================================================
        # GUI
        #=========================================================================        
        load_game_GUI(self)
        
        #=========================================================================
        # Important variables
        #=========================================================================                
        self.levelNodePath = NodePath(PandaNode('level'))
        self.levelNodePath.reparentTo(self.render)
        self.playerSpawnList = []
        self.placedExitsList = []
        self.playerAvatar = None
        self.paused = False        
        self.toggle_frameOverlay(True)
        self.cTrav = CollisionTraverser()
        self.cTrav.setRespectPrevTransform(True)
        self.collisionHandlerPusher = CollisionHandlerPusher()
        self.collisionHandlerPusher.setHorizontal(True)
        self.collisionHandlerGravity = CollisionHandlerGravity()
        self.collisionHandlerGravity.setGravity(10.0)
        self.collisionHandlerGravity.setMaxVelocity(100)
        self.collisionHandlerEvent = CollisionHandlerEvent()
        self.maskPusher = self.return_bitMask_with_specified_bit(0)
        self.maskGravity = self.maskPusher #self.return_bitMask_with_specified_bit(1)
        self.maskEvent = self.return_bitMask_with_specified_bit(2)
        self.aiWorld = AIWorld(self.render)   
        
        #=========================================================================
        # Generating events with CollisionHandlerEvent
        #=========================================================================
        # https://docs.panda3d.org/1.10/python/programming/collision-detection/collision-handlers#collisionhandlerevent
        self.collisionHandlerEvent.addInPattern('%fn-into-%in')
        
        #=========================================================================
        # attaching the event functions to their events
        #=========================================================================
        # DirectObject, because that class can respond to events
        # https://docs.panda3d.org/1.10/python/_modules/direct/showbase/DirectObject
        # The event functions are below, this still is the __init__ function
        self.eventHandlerDO = DirectObject()
        self.eventHandlerDO.accept('playercolevent-into-exitcnode', self.event_exit_reached)
        self.eventHandlerDO.accept('playercolevent-into-rabbitcolevent', self.event_rabbit_caught)
        self.eventHandlerDO.accept('rabbitcolevent-into-rabbitcolevent', self.event_test)
        
        #=========================================================================
        #add the task to task manager
        #=========================================================================
        #https://docs.panda3d.org/1.10/python/programming/tasks-and-events/tasks#the-task-manager
        taskMgr.add(self.task_input, 'input')
        taskMgr.add(self.task_ai_update, 'ai_update')
        
    def return_bitMask_with_specified_bit(self,bit):
        return BitMask32.bit(bit)
        
    def place_exit(self,parent,positionList = []):
        for newPos in positionList:
            exitNodePath, exitCollider = load_exit(parent,posV3 = newPos, scaleV3 = Vec3(0.5,0.5,0.5))
            self.placedExitsList.append(exitNodePath)            
            
    def place_player(self,parent, positionList = []):
        randomizer = Randomizer()
        #random place if there is no player spawn
        if len(positionList) < 1:
            newPos = Vec3(randomizer.randomInt(20),randomizer.randomInt(20),2.5)
        else:
            index = randomizer.randomInt(len(positionList)-1)
            newPos = Vec3(positionList[index])
        self.playerAvatar = None
        self.playerAvatar, pusherCollider, gravityCollider, eventCollider = load_player(parent, posV3 = newPos)
        pusherCollider.node().setFromCollideMask(self.maskPusher)
        pusherCollider.node().setIntoCollideMask(BitMask32.allOff())
        gravityCollider.node().setFromCollideMask(self.maskGravity)
        gravityCollider.node().setIntoCollideMask(BitMask32.allOff())
        eventCollider.node().setFromCollideMask(self.maskEvent)
        eventCollider.node().setIntoCollideMask(self.maskEvent)
        self.collisionHandlerPusher.addCollider(pusherCollider, self.playerAvatar)
        self.cTrav.addCollider(pusherCollider, self.collisionHandlerPusher)
        self.collisionHandlerGravity.addCollider(gravityCollider, self.playerAvatar)
        self.cTrav.addCollider(gravityCollider,self.collisionHandlerGravity)
        self.cTrav.addCollider(eventCollider,self.collisionHandlerEvent)
        
    def place_rabbit(self,parent, positionList = []):
        for newPos in positionList:
            newRabbit, pusherCollider, gravityCollider, eventCollider= load_rabbit(parent, posV3 = newPos-Vec3(0, 0, 0.25), scaleV3 = Vec3(0.05,0.05,0.05))
            pusherCollider.node().setFromCollideMask(self.maskPusher)
            pusherCollider.node().setIntoCollideMask(BitMask32.allOff())
            pusherCollider.show()
            gravityCollider.node().setFromCollideMask(self.maskGravity)
            gravityCollider.node().setIntoCollideMask(BitMask32.allOff())
            eventCollider.node().setFromCollideMask(self.maskEvent)
            eventCollider.node().setIntoCollideMask(self.maskEvent)
            self.collisionHandlerPusher.addCollider(pusherCollider, newRabbit)
            self.cTrav.addCollider(pusherCollider, self.collisionHandlerPusher)
            self.collisionHandlerGravity.addCollider(gravityCollider, newRabbit)
            self.cTrav.addCollider(gravityCollider,self.collisionHandlerGravity)
            self.cTrav.addCollider(eventCollider,self.collisionHandlerEvent)
            rabbitaiChar = AICharacter('rabbitAI', newRabbit, 100, 0.05, 5)
            rabbitBehaviors = rabbitaiChar.getAiBehaviors()
            rabbitBehaviors.evade(self.playerAvatar, 10, 20, 0.8)
            #rabbitBehaviors.wander(120, 0, 100, 0.2)
            #rabbitBehaviors.obstacleAvoidance(0.5)
            self.aiWorld.addAiChar(rabbitaiChar)
        
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
        self.levelNodePath.setCollideMask(self.maskPusher)
        wallTexture = loader.loadCubeMap('Assets/cubeMapBrickWall/brickWall#.png')
        #wallTexture = loader.loadTexture('Assets/Untitled.png')
        #wallTexture.setWrapU(Texture.WM_clamp)
        #wallTexture.setWrapV(Texture.WM_clamp) 
        #wallTexture.setBorderColor((0.4, 0.5, 1, 1))
        #wallTexture.setAnisotropicDegree(2)
        for wallBlock in self.levelNodePath.findAllMatches('**/wall'):
            wallBlock.setTexture(wallTexture, 1)
            self.aiWorld.addObstacle(wallBlock)
        self.graphicsEngine.renderFrame()
        for blockCollisionNode in self.levelNodePath.findAllMatches('**/blockcnode'):
            #blockCollisionNode.node().setCollideMask(self.maskPusher)
            pass
        self.playerSpawnList = []
        self.exitColliderList = []
        self.playerAvatar = None
        exitPositionList = []
        rabbitPositionList = []
        for startPoint in newLevel.findAllMatches('start'):
            self.playerSpawnList.append(startPoint.getPos()+Vec3(0,0,1))
        for exitPoint in newLevel.findAllMatches('exit'):
            exitPositionList.append(exitPoint.getPos()+Vec3(0,0,1.5))
        for rabbitPoint in newLevel.findAllMatches('rabbit'):
            rabbitPositionList.append(rabbitPoint.getPos()+Vec3(0,0,1.5))            
        self.place_player(self.levelNodePath,self.playerSpawnList)
        self.place_exit(self.levelNodePath,exitPositionList)
        self.place_rabbit(self.levelNodePath,rabbitPositionList)
        self.levelNodePath.reparentTo(self.render)
        self.graphicsEngine.renderFrame()
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

    def event_test(self,entry):
        print("rabbits touching")
        
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
        playerSpeed = 4*dt
        lookSpeed = 18
        if self.playerAvatar and not self.paused:
            newX = 0
            newY = 0
            if self.inputMap["up"]:
                #self.playerAvatar.setY(self.playerAvatar,playerSpeed)
                newY = 1
            if self.inputMap["down"]:
                #self.playerAvatar.setY(self.playerAvatar,-playerSpeed)
                newY = -1
            if self.inputMap["left"]:
                #self.playerAvatar.setX(self.playerAvatar,-playerSpeed)
                newX = -1
            if self.inputMap["right"]:
                #self.playerAvatar.setX(self.playerAvatar,playerSpeed)
                newX = 1
            newXYZ = Vec3(newX,newY,0)
            newXYZ.normalize()
            #self.playerAvatar.setFluidPos(Vec3(self.playerAvatar.getX(),self.playerAvatar.getY()),0.5)
            if self.collisionHandlerGravity.isOnGround():
                self.playerAvatar.setFluidPos(self.playerAvatar,newXYZ*playerSpeed)
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
            self.camera.setPos(self.playerAvatar.getPos()+Vec3(0,0,0.75))
            self.camera.setHpr(self.playerAvatar.getHpr())
        if self.inputMap['spawn']:
            print('spawniewanie')
            self.event_key_change('spawn',False)
        if self.inputMap['jump']:
            #print('jump')
            if self.collisionHandlerGravity.isOnGround():
                #print('on the ground')
                #self.collisionHandlerGravity.addVelocity(20) no good, makes everything jump
                print("jump")
            self.event_key_change('jump',False)
        if self.inputMap['screenshot']:
            print('screenshot')
            base.screenshot()
            self.event_key_change('screenshot',False)
        if self.inputMap['menu']:
            self.toggle_frameOverlay(self.frameOverlay.isHidden())
            self.event_key_change('menu',False)
        return task.cont    
    
    def task_ai_update(self,task):
        self.aiWorld.update()
        dt = globalClock.getDt()   
        self.liveRabbitsList = self.levelNodePath.findAllMatches('rabbitholder')
        if len(self.liveRabbitsList) > 0:
            self.rabbitCounter.setText(f'rabbits remaining:\n {len(self.liveRabbitsList)}')
            for placedExit in self.placedExitsList:
                placedExit.setCollideMask(BitMask32.allOff())
        else:
            self.rabbitCounter.setText(f'all rabbits caught!\n find an exit to win')
            for placedExit in self.placedExitsList:
                placedExit.setCollideMask(self.maskEvent)
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