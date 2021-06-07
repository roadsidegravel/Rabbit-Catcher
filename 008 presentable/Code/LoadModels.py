from panda3d.core import *

"""
def load_square(self):
    positionVec3 = Vec3(-self.fieldWidth/2,-5,-10)
    #load the square model
    self.square = loader.loadModel('Assets/square')
    #load the texture
    #squareTexture = loader.loadTexture('Assets/Terrain/textureMap.png')
    #put the texture on the model, the 1 tells Panda3D that we want to replace the texture
    #self.square.setTexture(squareTexture,1)
    #set x scale
    self.square.setSx(self.fieldWidth)
    #set y scale
    self.square.setSy(self.fieldWidth)
    #set position, x, y, z
    centerVec3 = Vec3(self.fieldWidth/2,self.fieldWidth/2,0)
    actualPos = positionVec3+centerVec3
    self.square.setPos(actualPos)
    #we reparent to render so it is added to the scene and rendered
    self.square.reparentTo(self.render)
"""
"""
def load_square(parent, posV3 = Vec3(0,0,0),scaleV3 = Vec3(1,1,1)):
    newSquare = loader.loadModel('Assets/square')
    #load the texture
    newSquare.reparentTo(parent)
    newSquare.setPos(posV3)
    newSquare.setScale(scaleV3)
    return newSquare
"""
    
def load_cube(parent, posV3 = Vec3(0,0,0),scaleV3 = Vec3(1,1,1)):
    newCube = loader.loadModel('Assets/cube.bam')
    #load the texture (cube map texture)
    newCube.reparentTo(parent)
    newCube.setPos(posV3)
    newCube.setScale(scaleV3)
    newCubeText = TextNode('cube text')
    newCubeText.setText('')
    newCubeTextNodePath = NodePath(newCubeText)
    newCubeTextNodePath.reparentTo(newCube)
    newCubeText.setTextColor(0,0,0,1)
    newCubeText.setAlign(TextNode.ACenter)
    newCubeTextNodePath.setScale(0.7)
    newCubeTextNodePath.setHpr(0,-90,0)
    newCubeTextNodePath.setPos(0,-0.25,1.1)
    newCubeCollider = newCube.attachNewNode(CollisionNode('blockcnode'))
    newCubeCollider.node().addSolid(CollisionSphere(0, 0, 0, 1))
    return newCube

def load_player(parent, posV3 = Vec3(0,0,0), scaleV3 = Vec3(1,1,1)):
    playerNodePath = NodePath(PandaNode('player'))
    playerNodePath.reparentTo(parent)
    playerCollider = playerNodePath.attachNewNode(CollisionNode('playercnode'))
    playerCollider.node().addSolid(CollisionSphere(0, 0, 0, 1))
    playerNodePath.setPos(posV3)
    playerNodePath.setScale(scaleV3)    
    return playerNodePath, playerCollider

def load_exit(parent, posV3 = Vec3(0,0,0), scaleV3 = Vec3(1,1,1)):
    exitNodePath = NodePath(PandaNode('exit'))
    exitNodePath.reparentTo(parent)
    exitCollider = exitNodePath.attachNewNode(CollisionNode('exitcnode'))
    exitCollider.node().addSolid(CollisionSphere(0, 0, 0, 1.5))
    exitNodePath.setPos(posV3)
    exitNodePath.setScale(scaleV3)
    exitModel = loader.loadModel('Assets/icosphere.bam')
    exitModel.reparentTo(exitNodePath)
    exitModel.setTransparency(TransparencyAttrib.MAlpha)
    exitModel.setColor(0.4,0.6,0.3,0.25)
    return exitNodePath, exitCollider

def load_rabbit(parent, posV3 = Vec3(0,0,0), scaleV3 = Vec3(1,1,1)):
    rabbitNodePath = NodePath(PandaNode('pokemon'))
    rabbitNodePath.reparentTo(parent)
    rabbitCollider = rabbitNodePath.attachNewNode(CollisionNode('rabbitcnode'))
    rabbitCollider.node().addSolid(CollisionSphere(0, 0, 0, 0.25))
    rabbitCollider.setPos(0,0,0.5)
    #rabbitCollider.show()
    rabbitNodePath.setPos(posV3)
    rabbitModel = loader.loadModel('Assets/pill.bam')
    rabbitModel.reparentTo(rabbitNodePath)
    rabbitModel.setColor(0.2,0.5,0.7,1)
    rabbitModel.setHpr(90,0,0)
    rabbitModel.setScale(scaleV3)
    return rabbitNodePath, rabbitCollider
