import os

from direct.gui.DirectGui import *
from direct.gui.OnscreenText import OnscreenText
from panda3d.core import *

class contextOptions:
    def __init__(self):
        self.exportBam = 'exportBam'
        self.importBam = 'importBam'
        self.placeExit = 'placeExit'
        self.placeFloor = 'placeFloor'
        self.placeRabbit = 'placeRabbit'
        self.placeStart = 'placeStart'
        self.placeWall = 'placeWall'

def load_game_GUI(gameSelf):
    gameSelf.frameOverlay = DirectFrame(frameColor =(1, 1, 1, 0.25), frameSize = (-1.2, 1.2, -1, 1),
                            pos=(0, 0, 0))
    frameLevels = DirectFrame(parent = gameSelf.frameOverlay, frameColor =(1, 1, 1, 0.0),
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
                            frameSize = standardSize, command = gameSelf.command_load_level,
                            extraArgs = [levelPath])
            col += 1
            if col > 3:
                row += 1
                col = 0
        row += 1
        
    gameSelf.winMessage = OnscreenText(text='you win!!!  (press esc to play again)', pos = (0, 0), scale = 0.1)
    gameSelf.winMessage.hide()
    
    gameSelf.rabbitCounter = OnscreenText(text='rabbits remaining', pos=(0.96,0.9), scale = 0.05, mayChange = 1)
    
    keyboardMap = gameSelf.win.get_keyboard_map()
    upMap = keyboardMap.get_mapped_button('w')
    downMap = keyboardMap.get_mapped_button('s')
    leftMap = keyboardMap.get_mapped_button('a')
    rightMap = keyboardMap.get_mapped_button('d')
    pMap = keyboardMap.get_mapped_button('p')
    escMap = keyboardMap.get_mapped_button('escape')
    infostring = f'{upMap}: forward\n{downMap}: backwards\n{leftMap}: left\n{rightMap}: right\nMouse to look\n{pMap}: screenshot\n{escMap}: menu'
    gameSelf.infoMessage = OnscreenText(text=infostring, pos=(0.98,-0.65), scale = 0.05)
