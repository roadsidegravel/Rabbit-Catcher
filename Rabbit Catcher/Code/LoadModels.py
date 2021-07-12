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
    newCubeCollider.node().addSolid(CollisionBox(LPoint3f(0,0,0), 1, 1, 1))
    # newCube.hide()
    # newCubeCollider.show()
    return newCube

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

def load_player(parent, posV3 = Vec3(0,0,0)):
    # Dont rescale CollisionNodes!!
    # pusher handler
    # gravity handler
    # event handler
    holderNode = NodePath(PandaNode('playerholder')) #is the characters feet! for the gravity handler
    holderNode.reparentTo(parent)
    holderNode.setPos(posV3)
    #no playerModel
    pusherCollider = holderNode.attachNewNode(CollisionNode('playercolpusher'))
    pusherCollider.node().addSolid(CollisionSphere(0, 0, .5, 0.25))
    gravityCollider =  holderNode.attachNewNode(CollisionNode('playercolgravity'))
    gravityCollider.node().addSolid(CollisionRay(0,0,0.5, 0,0,-1))
    eventCollider = holderNode.attachNewNode(CollisionNode('playercolevent'))
    eventCollider.node().addSolid(CollisionSphere(0, 0, 0.5, 0.6))
    return holderNode, pusherCollider, gravityCollider, eventCollider

def load_rabbit(parent, posV3 = Vec3(0,0,0),scaleV3 = Vec3(0,0,0)):
    # Dont rescale CollisionNodes!!
    # Each object can only have one collision handler associated with it
    # pusher handler
    # gravity handler
    # event handler
    holderNode = NodePath(PandaNode('rabbitholder'))
    holderNode.reparentTo(parent)
    holderNode.setPos(posV3)
    rabbitModel = loader.loadModel('Assets/pill.bam')
    rabbitModel.reparentTo(holderNode)
    rabbitModel.setColor(0.2,0.5,0.7,1)
    rabbitModel.setHpr(90,0,0)
    rabbitModel.setPos(0,0,0.05)
    rabbitModel.setScale(scaleV3)
    pusherCollider = holderNode.attachNewNode(CollisionNode('rabbitcolpusher'))
    pusherCollider.node().addSolid(CollisionSphere(0, 0, 0.3, 0.25))
    gravityCollider =  holderNode.attachNewNode(CollisionNode('rabbitcolgravity'))
    gravityCollider.node().addSolid(CollisionRay(0,0,0.25, 0,0,-1))
    eventCollider = holderNode.attachNewNode(CollisionNode('rabbitcolevent'))
    eventCollider.node().addSolid(CollisionSphere(0, 0, 0.5, 0.6))  
    return holderNode, pusherCollider, gravityCollider, eventCollider
