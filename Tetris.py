# Tetris Attempt 435

import pygame, random, time, numpy, os

blockSize = 30
FPS = 60

SCREEN_WIDTH = 10 * blockSize + blockSize * 10
SCREEN_HEIGHT = 21 * blockSize + blockSize 

SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Tetris")

from os import listdir

pygame.font.init()
font = pygame.font.Font("SourceCodePro-Regular.ttf", int(blockSize*1.4))

# Assets

def loadImages(directory, dim):
    images = []
    for file in os.listdir(directory):
        image = pygame.image.load(directory+'/'+file)
        image = pygame.transform.scale(image, dim)
        images.append(image)
    return images



Blocks = loadImages("Assets/Blocks", (blockSize, blockSize))
HUD = loadImages("Assets/HUD", (8*blockSize, blockSize*22))

class Board():

    def __init__(self):

        self.Score = 0
        self.Lines = 0
        self.Level = 0

    def displayStats(self):

        if int(self.Score/10) > self.Level:
            self.Level += 1


        score = font.render(str(self.Score), "black", True)
        lines = font.render(str(self.Lines), "black", True)
        level = font.render(str(self.Level), "black", True)
        
        SCREEN.blit(score, (blockSize*17, blockSize * 3.4))
        SCREEN.blit(level, (blockSize*17, blockSize * 8.3))
        SCREEN.blit(lines, (blockSize*17, blockSize * 12.2))

    def clearGrid(self):

        self.Grid = []
        for height in range(0, 21):
            setUpList = []
            for width in range(0, 10):
                setUpList.append(0)
            self.Grid.append(setUpList)
                
    def drawGrid(self):

        #print(self.Grid)
        for width in range(0, 10):
            for height in range(0, 21):
                box = pygame.Rect(width*blockSize+blockSize*5, height*blockSize+blockSize, blockSize, blockSize)
                #pygame.draw.rect(SCREEN, "black", box, 1)


        for i in range(22):
            SCREEN.blit(Blocks[5], (5, i*blockSize))

        for i in range(22):
            SCREEN.blit(Blocks[5], (5+blockSize*11, i*blockSize))


    def drawHUD(self):

        SCREEN.blit(HUD[0], (blockSize+blockSize*11 + 5, 3))
        self.displayStats()
        

    def clearLines(self, Shapes):

        for line in range(0, 21):
            if (self.Grid[line]).count(0) == 0:
                elements = list(set(self.Grid[line]))

                # make sure every shape with the element ID has moving as False then remove them all
                for Shape in Shapes:
                    if Shape.ObjectCollection[0].ObjectID in elements and Shape.Moving == True:
                        elements = []
                    
                for Shape in Shapes:
                    for Object in Shape.ObjectCollection:
                        if Object.ObjectID in elements and Object.gridPos.y == line:
                            Shape.removeObject(Object)
                            self.Score += 1

                if len(elements) > 0:
                    for Shape in Shapes:
                        for Object in Shape.ObjectCollection:
                            if Object.gridPos.y < line:
                                Object.gridPos.y += 1
                    self.Lines +=1


    def updateGrid(self, Shapes):

        for Shape in Shapes:
            for Object in Shape.ObjectCollection:
                if Object.Active:

                    if self.Grid[int(Object.gridPos.y)][int(Object.gridPos.x)] != 0:
                        # Handle overlapping objects (e.g., end the game)
                        print("Game Over - Overlapping Shapes")
                        pygame.quit()
                        quit()
                    else:
                        self.Grid[int(Object.gridPos.y)][int(Object.gridPos.x)] = Object.ObjectID

        self.drawGrid()
        self.drawHUD()

    def drawShapes(self, Shapes):

        for Shape in Shapes:
            Shape.drawObjects()

        self.clearLines(Shapes)

    def updateShapes(self, Shapes):

        for Shape in Shapes:
            Shape.updateShapes(Shapes, self.Grid, self.Level)

class Object():

    def __init__(self, ID, image, posx, posy):

        self.ObjectID = ID
        self.Active = True
        self.image = image
        self.gridPos = pygame.math.Vector2(posx, posy) #X, Y ON GRID

    def drawObject(self):

        if self.Active:
            SCREEN.blit(self.image, (self.gridPos.x*blockSize+blockSize+5, self.gridPos.y*blockSize+blockSize))


class Shape(pygame.sprite.Sprite):

    def __init__(self):
        
        super().__init__()
 
        self.Moving = True
        self.fallTicks = 0
        self.moveCoolDown = 30
        self.moveCoolDownStart = 30
        self.moveTicks = 0
        self.moveHorizontalCoolDown = 5
        self.ObjectCollection = []
        self.rotateTicks = 0
        self.matrix = []


    def removeObject(self, Object):

        Object.Active = False

    def updateShapes(self, Shapes, Grid, Level):

        if self.Moving:

            self.moveShapeVertical(Shapes, Grid, Level)
            self.moveShapeHorizontal(Shapes, Grid)
            self.rotateShape(Shapes, Grid)

        if self.moveCoolDown > 5:
            self.moveCoolDown = self.moveCoolDownStart * 1-(Level+1/10)
        #print(self.moveCoolDown)
        
    def drawObjects(self):

        for Object in self.ObjectCollection:
            Object.drawObject()

    def getMatrix(self, Shapes, Grid):

        Positions = []
        for Object in self.ObjectCollection:
            Positions.append([int(Object.gridPos.x), int(Object.gridPos.y)])
    
        smallestY = Positions[0][1]
        smallestX = Positions[0][0]
        for i in range(len(Positions)):
            if Positions[i][1] < smallestY:
                smallestY = Positions[i][1]
            if Positions[i][0] < smallestX:
                smallestX = Positions[i][0]
            
        for i in range(len(Positions)):
            Positions[i][1] -= smallestY
            Positions[i][0] -= smallestX

        largestY = Positions[0][1]
        largestX = Positions[0][0]

        for i in range(len(Positions)):
            if Positions[i][1] > largestY:
                largestY = Positions[i][1]
            if Positions[i][0] > largestX:
                largestX = Positions[i][0]

        matrix = []
        for i in range(largestY+1):
            line = []
            for j in range(largestX+1):
                line.append(0)
            matrix.append(line)

        for pos in Positions:
                matrix[pos[1]][pos[0]] = 1

        self.smallestX = smallestX
        self.smallestY =smallestY
        self.matrix = matrix
            
    def rotateShape(self, Shapes, Grid):

        # Fix this Up so it can rotate either way and the long line has a roation AXIS

        self.getMatrix(Shapes, Grid)
        keys = pygame.key.get_pressed()

        if keys[pygame.K_r] and self.rotateTicks > 10:
            self.rotateTicks = 0

            new = numpy.rot90(self.matrix)
            #======================================================
            newPositions = []
            for i in range(len(new[0])):
                for j in range(len(new)):
                    if new[j][i] == 1:
                        newPositions.append([i+self.smallestX, j+self.smallestY])

            Collision = False

            for Position in newPositions:
                try:
                    if Grid[Position[1]][Position[0]] != 0 and Grid[Position[1]][Position[0]] != self.ObjectCollection[0].ObjectID:
                        Collision = True
                except:
                    Collision = True
            
            if Collision == False:

                i = 0
                for Object in self.ObjectCollection:
                    Object.gridPos.x = newPositions[i][0]
                    Object.gridPos.y = newPositions[i][1]
                    i+=1
        else:
            self.rotateTicks += 1

            

    def moveShapeVertical(self, Shapes, Grid, Level):

        keys = pygame.key.get_pressed()
        if keys[pygame.K_s]:
            self.moveCoolDown = 1
        else:
            self.moveCoolDown = self.moveCoolDownStart * 1-(Level+1/10)

        if self.fallTicks > self.moveCoolDown:
            self.fallTicks = 0
            if self.shapeCollisionsVertical(Shapes, Grid):
                for Object in self.ObjectCollection:
                    Object.gridPos.y += 1
            else:
                self.Moving = False
        else:
            self.fallTicks += 1

    def moveShapeHorizontal(self, Shapes, Grid):
        
        if self.moveTicks > self.moveHorizontalCoolDown:
            self.moveTicks = 0
            keys = pygame.key.get_pressed()
            if keys[pygame.K_a]:
                if self.shapeCollisionsHorizontal(Shapes, "Left", Grid):
                    for Object in self.ObjectCollection:
                        Object.gridPos.x -= 1
            if keys[pygame.K_d]:
                if self.shapeCollisionsHorizontal(Shapes, "Right", Grid):
                    for Object in self.ObjectCollection:
                        Object.gridPos.x += 1
        else:
            self.moveTicks += 1
                    
    def shapeCollisionsHorizontal(self, Shapes, Direction, Grid):

        # Width boundries and make it stop moving when it hits floor or other object
        # Use Future Prediction
        Outcome = True
        if Direction == "Right":
            for Object in self.ObjectCollection:
                if Object.gridPos.x > 8:
                    Outcome = False
                elif Grid[int(Object.gridPos.y)][int(Object.gridPos.x)+1] != 0 and Grid[int(Object.gridPos.y)][int(Object.gridPos.x)+1] != Object.ObjectID:
                    Outcome = False
        if Direction == "Left":
            for Object in self.ObjectCollection:
                if Object.gridPos.x < 1:
                    Outcome = False
                elif Grid[int(Object.gridPos.y)][int(Object.gridPos.x)-1] != 0 and Grid[int(Object.gridPos.y)][int(Object.gridPos.x)-1] != Object.ObjectID:
                    Outcome = False 
        return Outcome

    def shapeCollisionsVertical(self, Shapes, Grid):

        # Only going DOWN, check each object in Collection and test if adding 1 to each y value causes overlap, True if can Move
        Outcome = True
        for Object in self.ObjectCollection:
            if Outcome == True:
                if Object.gridPos.y > 19:
                    Outcome = False
                elif Grid[int(Object.gridPos.y)+1][int(Object.gridPos.x)] != Object.ObjectID and Grid[int(Object.gridPos.y)+1][int(Object.gridPos.x)] != 0:
                    Outcome = False

        print(Outcome)
        return Outcome


    def displayInBox(self, Shapes, Grid):

        self.getMatrix(Shapes, Grid)
        positions = []
        for i in range(len(self.matrix[0])):
            for j in range(len(self.matrix)):
                if self.matrix[j][i] == 1:
                    if len(self.matrix) == 1:
                        positions.append([i*blockSize+ blockSize * 14.4, j*blockSize+SCREEN_HEIGHT - blockSize*4.5])
                    else:
                        positions.append([i*blockSize+ blockSize * 15.7, j*blockSize+SCREEN_HEIGHT - blockSize*4.5])

        i = 0
        for Object in self.ObjectCollection:
            SCREEN.blit(Object.image, (positions[i][0], positions[i][1]))
            i+=1

class Box(Shape):

    def __init__(self, ID):
        super().__init__()
        self.ID = ID
        self.createShape()
         
    def createShape(self):

        num = random.randint(0, 4)
        self.ObjectCollection.append(Object(self.ID, Blocks[num], 3, 0))
        self.ObjectCollection.append(Object(self.ID, Blocks[num], 3, 1))
        self.ObjectCollection.append(Object(self.ID, Blocks[num], 4, 1))
        self.ObjectCollection.append(Object(self.ID, Blocks[num], 4, 0))


class Line(Shape):

    def __init__(self, ID):
        super().__init__()
        self.ID = ID
        self.createShape()
         
    def createShape(self):
        num = random.randint(0, 4)
        self.ObjectCollection.append(Object(self.ID, Blocks[num], 1, 0))
        self.ObjectCollection.append(Object(self.ID, Blocks[num], 2, 0))
        self.ObjectCollection.append(Object(self.ID, Blocks[num], 3, 0))
        self.ObjectCollection.append(Object(self.ID, Blocks[num], 4, 0))


class Z(Shape):

    def __init__(self, ID):
        super().__init__()
        self.ID = ID
        self.createShape()
         
    def createShape(self):
        num = random.randint(0, 4)
        self.ObjectCollection.append(Object(self.ID, Blocks[num], 4, 0))
        self.ObjectCollection.append(Object(self.ID, Blocks[num], 4, 1))
        self.ObjectCollection.append(Object(self.ID, Blocks[num], 3, 2))
        self.ObjectCollection.append(Object(self.ID, Blocks[num], 3, 1))
 
class L(Shape):
    
    def __init__(self, ID):
        super().__init__()
        self.ID = ID
        self.createShape()
         
    def createShape(self):
        num = random.randint(0, 4)
        self.ObjectCollection.append(Object(self.ID, Blocks[num], 4, 0))
        self.ObjectCollection.append(Object(self.ID, Blocks[num], 4, 1))
        self.ObjectCollection.append(Object(self.ID, Blocks[num], 4, 2))
        self.ObjectCollection.append(Object(self.ID, Blocks[num], 5, 2))

class T(Shape):
    
    def __init__(self, ID):
        super().__init__()
        self.ID = ID
        self.createShape()
         
    def createShape(self):
        num = random.randint(0, 4)
        self.ObjectCollection.append(Object(self.ID, Blocks[num], 3, 0))
        self.ObjectCollection.append(Object(self.ID, Blocks[num], 4, 0))
        self.ObjectCollection.append(Object(self.ID, Blocks[num], 5, 0))
        self.ObjectCollection.append(Object(self.ID, Blocks[num], 4, 1))
        
    

class ShapeQueue():

    def __init__(self):

        self.Queue = []
        self.ShapesNum = 1

    def addRandomToQueue(self, Shapes):

        shapeRandomNum = random.randint(0, 4)
        if shapeRandomNum == 0:
            new = Box(self.ShapesNum)
        elif shapeRandomNum == 1:
            new = Line(self.ShapesNum)
        elif shapeRandomNum == 2:
            new = Z(self.ShapesNum)
        elif shapeRandomNum == 3:
            new = L(self.ShapesNum)
        else:
            new = T(self.ShapesNum)

        self.Queue.append(new)


    def checkMovingObject(self, Shapes):


        if self.Queue[self.ShapesNum-1].Moving == False or self.ShapesNum == 1:
            Shapes.add(self.Queue[self.ShapesNum])
            self.ShapesNum += 1
            self.addRandomToQueue(Shapes)

        self.DisplayNextShape()

    def getMovingObject(self):

        return self.Queue[self.ShapesNum]


    def DisplayNextShape(self):

        self.Queue[self.ShapesNum].displayInBox(Shapes, newBoard.Grid)
        
    

gameStart = True

Shapes = pygame.sprite.Group()

newBoard = Board()
newQueue = ShapeQueue()
newQueue.addRandomToQueue(Shapes)
newQueue.addRandomToQueue(Shapes)


Clock = pygame.time.Clock()

while gameStart:

    SCREEN.fill((202,210,169))
    
    newBoard.clearGrid()
    newBoard.updateGrid(Shapes)
    newBoard.drawShapes(Shapes)
    newBoard.updateShapes(Shapes)
    newQueue.checkMovingObject(Shapes)

    pygame.display.update()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            gameStart = False

    Clock.tick(FPS)
