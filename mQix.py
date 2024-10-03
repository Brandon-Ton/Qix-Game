import pygame, sys, os
import math, random

#pyinstaller mQix.py --onefile --noconsole

# Define colors
WHITE = (155, 155, 155)
BLACK = (0, 0, 0)

directions = ['L', 'U', 'R', 'D']
dirToVector = {'L': (-1, 0), 'U': (0, -1), 'R': (1, 0), 'D': (0, 1)}
EPSILON = 0.001


def loopList(L, i, j):
    if i >= len(L):
        i = i%len(L)
    if i >= j:
        return L[i:] + L[:j]
    return L[i:j]

def getDir(v1, v2):
    #print(v1, v2)
    dx = v2[0]-v1[0]
    dy = v2[1]-v1[1]
    if dy == 0:
        if dx > 0:
            return 'R'
        else:
            return 'L'
    elif dx == 0:
        if dy > 0:
            return 'D'
        else:
            return 'U'
    #print("value error: ", v1, v2)
    raise ValueError

def calcArea(vertices):
    n = len(vertices)
    area = 0.0
    for i in range(n):
        x1, y1 = vertices[i]
        x2, y2 = vertices[(i + 1) % n]
        area += (x1 * y2 - x2 * y1)
    return abs(area) / 2.0

def distance(a,b):
    return math.sqrt((a[0] - b[0])**2 + (a[1] - b[1])**2)

class Qix:
    def __init__(self, pos, radius, speed):
        self.pos = pos
        self.prevPos = pos
        self.jiggleSpeed = math.sqrt(0.5*speed**2)
        self.radius = radius

    def move(self):
        self.prevPos = self.pos
        self.pos = (self.pos[0] + random.randint(-1, 1)*self.jiggleSpeed, self.pos[1] + random.randint(-1, 1)*self.jiggleSpeed)
        # for i in range(len(f.vertices)):
        #     v1 = f.vertices[i]
        #     v2 = f.vertices[(i+1) % len(f.vertices)]
        #     if line_intersection((v1, v2), (self.prevPos, self.pos)) is not None:
        #         self.pos = self.prevPos
        if not isInsidePolygon(self.pos, f.vertices):
            self.pos = self.prevPos

class Field:
    def __init__(self, vertices, goal):
        self.goal = goal
        
        self.vertices = vertices
        self.startArea = calcArea(self.vertices)
        self.currentArea = self.startArea
        self.percentArea = self.currentArea / self.startArea * 100        

    def updateArea(self):
        global areaText, gameState
        self.currentArea = calcArea(self.vertices)
        self.percentArea = self.currentArea / self.startArea * 100
        font = pygame.font.Font(None, 30)   
        areaText = small_font.render("Remaining Area: " + str(round(f.percentArea, 2)) + "%", True, WHITE)
        if (self.currentArea / self.startArea) < self.goal:
            gameState = "winScreen"


class Sparx:
    def __init__(self, currentVertexIndex):
        self.radius = 5
        self.color = (51, 51, 255)
        self.velocity = 0.02
        self.direction = random.randint(1,2)

        self.prevVertexIndex = currentVertexIndex
        self.prevVertexPreMerge = f.vertices[self.prevVertexIndex]
        self.pos = list(f.vertices[currentVertexIndex])
        self.prevPos = self.pos
        self.prevPos = self.pos[:]
        self.moving_clockwise = False
        self.moving_counterclockwise = False
        self.pushDirection = ""
        self.newPushDirection = ""
        self.tail = []


    def getNextVertex(self):
        return f.vertices[(self.prevVertexIndex + 1) % len(f.vertices)]


    def draw(self, screen):
        if self.pushDirection != "":
            for i in range(len(self.tail)-1):
                pygame.draw.line(screen, (0, 0, 255), self.tail[i], self.tail[i+1])
            pygame.draw.line(screen, (0, 0, 255), self.tail[-1], (round(self.pos[0]), round(self.pos[1])))        
        pygame.draw.circle(screen, self.color, (int(self.pos[0]), int(self.pos[1])), self.radius)


    def move(self):
        self.prevPos = self.pos
        if self.direction == 1:
            self.move_clockwise()
        else:
            self.move_counterclockwise()


    def move_clockwise(self):
        target_x, target_y = self.getNextVertex()
        dx, dy = target_x - self.pos[0], target_y - self.pos[1]
        distance_to_target = math.sqrt(dx ** 2 + dy ** 2)
        if distance_to_target > self.velocity:
            angle = math.atan2(dy, dx)
            self.pos[0] += self.velocity * math.cos(angle)
            self.pos[1] += self.velocity * math.sin(angle)
        else:
            self.pos[0], self.pos[1] = target_x, target_y
            self.prevVertexIndex = (self.prevVertexIndex + 1) % len(f.vertices)


    def move_counterclockwise(self):
        target_x, target_y = f.vertices[self.prevVertexIndex]
        dx, dy = target_x - self.pos[0], target_y - self.pos[1]
        distance_to_target = math.sqrt(dx ** 2 + dy ** 2)
        if distance_to_target > self.velocity:
            #unnecessary math
            angle = math.atan2(dy, dx)
            self.pos[0] += self.velocity * math.cos(angle)
            self.pos[1] += self.velocity * math.sin(angle)
        else:
            self.pos[0], self.pos[1] = target_x, target_y
            self.prevVertexIndex = (self.prevVertexIndex - 1) % len(f.vertices)

class Player:
    def __init__(self, currentVertexIndex, hp):
         # Adjust as needed
        self.radius = 5
        self.color = (255, 0, 0)
        self.velocity = 0.05
        self.hp = hp

        self.prevVertexIndex = currentVertexIndex
        self.pos = list(((f.vertices[0][0] + f.vertices[2][0])/2, (f.vertices[0][1])))
        self.prevPos = self.pos[:]
        self.moving_clockwise = False
        self.moving_counterclockwise = False
        self.pushDirection = ""
        self.newPushDirection = ""
        self.tail = []

    def getNextVertex(self):
        return f.vertices[(self.prevVertexIndex + 1) % len(f.vertices)]

    def draw(self, screen):
        if self.pushDirection != "":
            for i in range(len(self.tail)-1):
                pygame.draw.line(screen, (0, 0, 255), self.tail[i], self.tail[i+1])
            pygame.draw.line(screen, (0, 0, 255), self.tail[-1], (round(self.pos[0]), round(self.pos[1])))        
        pygame.draw.circle(screen, self.color, (int(self.pos[0]), int(self.pos[1])), self.radius)

    def move(self):
        if self.pushDirection != "":
            if self.newPushDirection != "":
                self.continuePush(self.newPushDirection)
        elif self.moving_clockwise:
            self.move_clockwise()
        elif self.moving_counterclockwise:
            self.move_counterclockwise()

    def move_clockwise(self):
        target_x, target_y = self.getNextVertex()
        dx, dy = target_x - self.pos[0], target_y - self.pos[1]
        distance_to_target = math.sqrt(dx ** 2 + dy ** 2)
        if distance_to_target > self.velocity:
            angle = math.atan2(dy, dx)
            self.pos[0] += self.velocity * math.cos(angle)
            self.pos[1] += self.velocity * math.sin(angle)
        else:
            self.pos[0], self.pos[1] = target_x, target_y
            self.prevVertexIndex = (self.prevVertexIndex + 1) % len(f.vertices)

    def move_counterclockwise(self):
        target_x, target_y = f.vertices[self.prevVertexIndex]
        dx, dy = target_x - self.pos[0], target_y - self.pos[1]
        distance_to_target = math.sqrt(dx ** 2 + dy ** 2)
        if distance_to_target > self.velocity:
            #unnecessary math
            angle = math.atan2(dy, dx)
            self.pos[0] += self.velocity * math.cos(angle)
            self.pos[1] += self.velocity * math.sin(angle)
        else:
            self.pos[0], self.pos[1] = target_x, target_y
            self.prevVertexIndex = (self.prevVertexIndex - 1) % len(f.vertices)

    def isItValidPushDirection(self, direction):
        #return false if on a vertex
        self.pos = [round(self.pos[0]), round(self.pos[1])]
        if self.pos[0] == f.vertices[self.prevVertexIndex][0] and self.pos[1] == f.vertices[self.prevVertexIndex][1]:
            hurtSound.play()
            return ""
       
        x, y = f.vertices[(self.prevVertexIndex + 1) % len(f.vertices)]
        #check if the direction is the direction yielded from turning right when facing next vertex
        if direction == 'U' and self.pos[0] > x:
            self.tail.append((round(self.pos[0]), round(self.pos[1])))
            return 'U'
        elif direction == 'D' and self.pos[0] < x:
            self.tail.append((round(self.pos[0]), round(self.pos[1])))
            return 'D'
        elif direction == 'L' and self.pos[1] < y:
            self.tail.append((round(self.pos[0]), round(self.pos[1])))
            return 'L'
        elif direction == 'R' and self.pos[1] > y:
            self.tail.append((round(self.pos[0]), round(self.pos[1])))
            return 'R'
        hurtSound.play()
        return ""
    
    def continuePush(self, direction):
        if self.pushDirection == direction:
            # Get the vector corresponding to the direction
            vector = dirToVector[direction]
            self.pos[0] += self.velocity * vector[0]
            self.pos[1] += self.velocity * vector[1]
        else:
            self.tail.append((round(self.pos[0]), round(self.pos[1])))
            self.pushDirection = direction
            self.continuePush(direction)

        if len(self.tail) > 0:
            for i in range(len(f.vertices)):
                v1 = f.vertices[i]
                v2 = f.vertices[(i+1) % len(f.vertices)]
                if line_intersection((v1, v2), (self.tail[-1], self.pos)) != None:
                    #print("Intersection detected!")
                    if v1[0] == v2[0]:self.pos[0] = v1[0]
                    elif v1[1] == v2[1]:self.pos[1] = v1[1]
                    else: raise ValueError 
                    hurtSound.play()
                    self.tail.append((round(self.pos[0]), round(self.pos[1])))
                    
                    # print("acc: ", self.tail)

                    for sparx in sparxs:
                        if sparx.direction == 1:
                            sparx.prevVertexPreMerge = f.vertices[sparx.prevVertexIndex]
                        else: sparx.prevVertexPreMerge = f.vertices[(sparx.prevVertexIndex + 1) % len(f.vertices)]
                    merge(self.prevVertexIndex, i, self.tail)
                    self.prevVertexIndex = f.vertices.index(self.tail[-1])
                    for sparx in sparxs:
                        try:
                            getDir(self.tail[0], sparx.prevVertexPreMerge)
                            tVertex = self.tail[0]
                            #print("efefe")
                        except:
                            tVertex = self.tail[-1]
                        if sparx.prevVertexPreMerge in f.vertices:
                            if sparx.direction == 1:
                                sparx.prevVertexIndex = f.vertices.index(sparx.prevVertexPreMerge)
                            else: sparx.prevVertexIndex = f.vertices.index(sparx.prevVertexPreMerge) - 1
                        else: sparx.prevVertexIndex = f.vertices.index(tVertex)
                        
                    self.pushDirection = ""
                    self.newPushDirection = ""
                    self.tail = []
                    break
            
            for i in range(len(self.tail)-1):
                v1 = self.tail[i-1]
                v2 = self.tail[i]
                if line_intersection((v1, v2), (self.tail[-1], self.pos)) != None:
                    self.cancelPush()
                    break

    def cancelPush(self):
        self.pushDirection = ""
        self.newPushDirection = ""
        self.pos = list(self.tail[0])
        self.tail = []
        self.getHurt()

    def getHurt(self):
        global gameState, lifeText
        hurtSound.play()
        self.hp -= 1
        lifeText = small_font.render("Remaining Life Force: " + str(player.hp), True, WHITE)
        if self.hp <= 0:
            gameState = "loseScreen"

def checkQixCollide(qix, player):
    for i in range(len(player.tail) - 1):
        if line_intersection((player.tail[i], player.tail[i+1]), (qix.pos, qix.prevPos)):
            player.cancelPush()
            return
    if player.tail:
        if distance(player.pos, qix.pos) < (player.radius + qix.radius):
            player.cancelPush()
            return
        elif line_intersection((player.tail[-1], player.pos), (qix.pos, qix.prevPos)):
            player.cancelPush()
            return

def checkSparcCollide(sparc, player):
    if not player.tail:
        if distance(player.pos, sparc.pos) < (sparc.radius + sparc.radius) and player.prevVertexIndex == sparc.prevVertexIndex:
            if sparc.direction == 1:
                sparc.direction = 2
            else:
                sparc.direction = 1
            while distance(player.pos, sparc.pos) < (sparc.radius + sparc.radius):
                sparc.move()
            player.getHurt()
            return
    if player.tail:
        if distance(player.tail[0], sparc.pos) < sparc.radius and player.prevVertexIndex == sparc.prevVertexIndex:
            player.cancelPush()
            return

def line_intersection(line1, line2):
    x1, y1 = line1[0]
    x2, y2 = line1[1]
    x3, y3 = line2[0]
    x4, y4 = line2[1]

    # Calculate the slopes of the lines
    denom = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
    
    # If the lines are parallel or coincident, return None (no intersection)
    if denom == 0:
        return None
    
    # Calculate the intersection point coordinates
    px = ((x1 * y2 - y1 * x2) * (x3 - x4) - (x1 - x2) * (x3 * y4 - y3 * x4)) / denom
    py = ((x1 * y2 - y1 * x2) * (y3 - y4) - (y1 - y2) * (x3 * y4 - y3 * x4)) / denom
    
    if (round(px), round(py)) == (x3, y3):
        return None

    # Check if the intersection point lies within both line segments
    if (min(x1, x2) <= px <= max(x1, x2) and min(y1, y2) <= py <= max(y1, y2) and
        min(x3, x4) <= px <= max(x3, x4) and min(y3, y4) <= py <= max(y3, y4)):
        
        return px, py
    else:
        return None


def isClockwise(vertices):
    n = len(vertices)
    if n < 3:
        # A polygon with less than 3 vertices is not valid
        return False

    area = 0
    for i in range(n):
        x1, y1 = vertices[i]
        x2, y2 = vertices[(i + 1) % n]
        area += (x2 - x1) * (y2 + y1)

    return area < 0

def merge(edge1, edge2, tail):
    op1 = []
    op2 = []
    vert1 = []
    vert2 = []
    if edge1 == edge2:
        op1 = tail[:]
        if isClockwise(tail):
            tail = tail[::-1]
        op2 = loopList(f.vertices, edge1+1, edge2+1) + tail
    else:
        vert1 = loopList(f.vertices, edge1+1, edge2+1)
        vert2 = loopList(f.vertices, edge2+1, edge1+1)
        op1 = tail[:] + vert2
        op2 = tail[::-1] + vert1
    
    if not isClockwise(op1):
        op1 = op1[::-1]
    if not isClockwise(op2):
        op2 = op2[::-1]
    
    if isInsidePolygon(qix.pos, op1):
        f.vertices = op1[:]
    else:
        f.vertices = op2[:]

    
    # print("L: ", f.vertices)
    f.updateArea()

def isInsidePolygon(pos, L):
    # Ray casting algorithm to check if a point is inside a polygon
    count = 0
    x = pos[0]
    y = pos[1]
    for i in range(len(L)):
        v1 = L[i]
        v2 = L[(i + 1) % len(L)]
        if ((v1[1] <= y) != (v2[1] <= y)) and (x < (v2[0] - v1[0]) * (y - v1[1]) / (v2[1] - v1[1]) + v1[0]):
            count += 1
    return count % 2 == 1


def displayTexts(texts, sizes):
    """
    . This helper function assists in displaying text on the menus.
    . It renders each text with its respective font size and displays them vertically centered.
    .
    . @author GEN
    . @param texts: list of desired strings to display (ie. ['hello','world'])
    . @param sizes: list of strings respresenting the respective sizes of the strings to be displayed (ie.['small','medium'])
    .
    . Note: the lists have to be of the same size
    """
    global screenDimensions, font_sizes

    screen.fill(BLACK)
    text_surfaces = []

    # Render each text with its corresponding font size
    for text, size in zip(texts, sizes):
        font = font_sizes.get(size, small_font)
        text_surfaces.append(font.render(text, True, WHITE))

    # Calculate the vertical position of the first text
    total_height = sum(text.get_height() for text in text_surfaces)
    initial_y = (screenDimensions[1] - total_height) // 2

    # Blit each text surface onto the screen
    y_offset = initial_y
    for text_surface in text_surfaces:
        screen.blit(text_surface, (screenDimensions[0] // 2 - text_surface.get_width() // 2, y_offset))
        y_offset += text_surface.get_height()

def drawStartMenu():
    global gameState

    texts = ['MQix', '', ' Start [SPACE] ', 'Difficulty Settings [-] ', 'Instructions [=]', 'Quit [Q]']
    sizes = ['big','small'] + ['medium']*4
    displayTexts(texts, sizes)

    keys = pygame.key.get_pressed()
    if keys[pygame.K_SPACE]:
        gameState = "game"
        newGame(diffHP, diffGoal, diffNumSparx, diffQixSpeed)
    elif keys[pygame.K_MINUS]:
        gameState = "adjustmentsMenu"
    elif keys[pygame.K_EQUALS]:
        gameState = "instructionsMenu"

def drawInstructionsMenu():
    global gameState

    texts = ['> Capture enough of the field to win', 
             '> Use [A] and [D] to move Clockwise and CCW around the edge',
             '> Use the arrow keys to enter the field and capture more of it', 
             '> Avoid the Qix when you enter the field',
             '> Avoid the several Sparx that patrol the edges',
             '> Be careful of confused Sparx when you capture territory',
             '', '[BACKSPACE]']
    sizes = ['small']*8
    displayTexts(texts, sizes)

    keys = pygame.key.get_pressed()
    if keys[pygame.K_BACKSPACE]: gameState = "startMenu"

def drawAdjustmentsMenu():
    global gameState
    diffSelect = ['', '', '' ,'']
    diffSelect[diffSelectIndex] = '>>>>>>>>>'

    texts = ['Use UP and DOWN to Change Selection',
             'Use RIGHT and LEFT to Increase / Decrease',
             '',
             diffSelect[0]+'Life Force: '+str(diffHP), 
             diffSelect[1]+'Area Remaining to Win: '+str(round(diffGoal*100, 1))+'%', 
             diffSelect[2]+'# of Sparx: '+str(diffNumSparx), 
             diffSelect[3]+'Speed of Qix: '+str(round(diffQixSpeed, 1)), 
             '', '[BACKSPACE]']
    
    sizes = ['small']*9
    displayTexts(texts, sizes)

    keys = pygame.key.get_pressed()
    if keys[pygame.K_BACKSPACE]: gameState = "startMenu"
    
def diffChange(dir):
    global diffHP, diffGoal, diffNumSparx, diffQixSpeed
    if diffSelectIndex == 0:
        if dir == 'R': diffHP += 1
        elif dir == 'L' and diffHP > 1: diffHP -= 1
    elif diffSelectIndex == 1:
        if dir == 'R' and diffGoal < 0.9: diffGoal += 0.05
        elif dir == 'L' and diffGoal >0.1: diffGoal -= 0.05
    elif diffSelectIndex == 2:
        if dir == 'R' and diffNumSparx < 4: diffNumSparx += 1
        elif dir == 'L' and diffNumSparx > 0: diffNumSparx -= 1
    elif diffSelectIndex == 3:
        if dir == 'R' and diffQixSpeed < 9.9: diffQixSpeed += 0.5
        elif dir == 'L' and diffQixSpeed > 0.7: diffQixSpeed -= 0.5

def drawWinScreen():
    global gameState

    texts = ['You Win!',
             'You can increase the difficulty in the Difficulty Settings',
             '', 'Menu [BACKSPACE]']
    sizes = ['medium'] + ["small"]*3
    displayTexts(texts, sizes)

    keys = pygame.key.get_pressed()
    if keys[pygame.K_BACKSPACE]: gameState = "startMenu"

def drawLoseScreen():
    global gameState

    texts = ['You Lose!',
             'You can change the difficulty in the Difficulty Settings',
             '', 'Menu [BACKSPACE]']
    sizes = ['medium'] + ["small"]*3
    displayTexts(texts, sizes)

    keys = pygame.key.get_pressed()
    if keys[pygame.K_BACKSPACE]: gameState = "startMenu"

# Create instances
def newGame(hp=1, goal=0.3, numSparx=1, QixSpeed=2):
    global f, player, qix, sparxs, areaText, lifeText, goalText, toMenuText
    f = Field([(100, 100), (400, 100), (400, 400), (100, 400)], goal)
    player = Player(0, hp)
    qix = Qix(((f.vertices[0][0] + f.vertices[2][0])/2, (f.vertices[0][1] + f.vertices[2][1])/2), 6, QixSpeed)
    sparxs = []
    for i in range(min(4, numSparx)):
        sparxs.append(Sparx(i))
    font = pygame.font.Font(None, 30)   
    areaText = small_font.render("Remaining Area: " + str(round(f.percentArea, 2)) + "%", True, WHITE)
    lifeText = small_font.render("Remaining Life Force: " + str(player.hp), True, WHITE)
    goalText = small_font.render("Target Area: " + str(round(f.goal * 100, 2)) + "%", True, WHITE)
    toMenuText = small_font.render("Go To Menu [M]", True, WHITE)

def handleEvents():
    global gameState
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            # will break main loop
            return False
        if pygame.key.get_pressed()[pygame.K_q] and gameState == "startMenu":
            # will break main loop
            return False
        if event.type == pygame.KEYDOWN:
            if gameState == "game":
                if event.key == pygame.K_m:
                    gameState = "startMenu"
                elif player.pushDirection == "":
                    if event.key == pygame.K_d:
                        player.moving_clockwise = True
                    elif event.key == pygame.K_a:
                        player.moving_counterclockwise = True
                    elif event.key == pygame.K_UP:
                        player.pushDirection = player.isItValidPushDirection('U')
                        player.newPushDirection = 'U'
                    elif event.key == pygame.K_DOWN:
                        player.pushDirection = player.isItValidPushDirection('D')
                        player.newPushDirection = 'D'
                    elif event.key == pygame.K_LEFT:
                        player.pushDirection = player.isItValidPushDirection('L')
                        player.newPushDirection = 'L'
                    elif event.key == pygame.K_RIGHT:
                        player.pushDirection = player.isItValidPushDirection('R')
                        player.newPushDirection = 'R'
                else:
                    if event.key == pygame.K_UP and player.pushDirection != 'D':
                        player.newPushDirection = 'U'
                    elif event.key == pygame.K_DOWN and player.pushDirection != 'U':
                        player.newPushDirection = 'D'
                    elif event.key == pygame.K_LEFT and player.pushDirection != 'R':
                        player.newPushDirection = 'L'
                    elif event.key == pygame.K_RIGHT and player.pushDirection != 'L':
                        player.newPushDirection = 'R'
        elif event.type == pygame.KEYUP:
            if gameState == "adjustmentsMenu":
                global diffSelectIndex
                if event.key == pygame.K_DOWN and diffSelectIndex <3 : diffSelectIndex += 1
                elif event.key == pygame.K_UP and diffSelectIndex >0 : diffSelectIndex -= 1
                elif event.key == pygame.K_RIGHT: diffChange('R')
                elif event.key == pygame.K_LEFT: diffChange('L')
            if gameState == "game":
                if event.key == pygame.K_d:
                    player.moving_clockwise = False
                elif event.key == pygame.K_a:
                    player.moving_counterclockwise = False
                if event.key == pygame.K_UP and player.newPushDirection == 'U':
                    player.newPushDirection = ""
                elif event.key == pygame.K_DOWN and player.newPushDirection == 'D':
                    player.newPushDirection = ""
                elif event.key == pygame.K_LEFT and player.newPushDirection == 'L':
                    player.newPushDirection = ""
                elif event.key == pygame.K_RIGHT and player.newPushDirection == 'R':
                    player.newPushDirection = ""
    return True

# Initialize Pygame and set up display
os.environ['SDL_VIDEO_CENTERED'] = '1'
pygame.init()
info = pygame.display.Info() 
screen_width,screen_height = info.current_w,info.current_h
window_width,window_height = screen_width,screen_height
screenDimensions = (window_width, window_height)
screen = pygame.display.set_mode(screenDimensions, pygame.FULLSCREEN)

# Set up font and sound
pygame.font.init()
hurtSound = pygame.mixer.Sound("ding.mp3")

# Start state
gameState = "startMenu"
diffSelectIndex = 0
diffHP, diffGoal, diffNumSparx, diffQixSpeed = 5, 0.5, 1, 4
#(hp=1, goal=0.3, numSparx=1, QixSpeed=2)

#[ GEN'S CODE BELOW !!!!!! ] 
big_font_size = 90
big_font = pygame.font.Font('charybdis.regular.ttf', big_font_size) # change path depending on the location of the ttf file
medium_font_size = 50
medium_font = pygame.font.Font('charybdis.regular.ttf', medium_font_size)
small_font_size = 30
small_font = pygame.font.Font('charybdis.regular.ttf', small_font_size)
font_sizes = {
    'big': big_font,
    'medium': medium_font,
    'small': small_font
}


# Main loop
while True:
    if not(handleEvents()): break

    if gameState == "startMenu": drawStartMenu() #GEN
    elif gameState == "instructionsMenu": drawInstructionsMenu() #GEN
    elif gameState == "adjustmentsMenu": drawAdjustmentsMenu() #GEN
    elif gameState == "loseScreen": drawLoseScreen()
    elif gameState == "winScreen": drawWinScreen()

    elif gameState == "game": 
        # Fill the screen with white
        screen.fill(BLACK)

        # Draw the filled polygon
        pygame.draw.polygon(screen, WHITE, f.vertices)

        # Move the player along the edge
        player.move()
        qix.move()
        for sparc in sparxs:
            sparc.move()
            checkSparcCollide(sparc, player)
        checkQixCollide(qix, player)

        # Draw the player
        player.draw(screen)
        # Draw the Qix
        pygame.draw.circle(screen, BLACK, (qix.pos[0], qix.pos[1]), qix.radius)
        #Draw the sparx
        for sparx in sparxs:
            sparx.draw(screen)
        
        screen.blit(areaText, (500, 200))
        screen.blit(goalText, (500, 230))
        screen.blit(lifeText, (500, 270))
        screen.blit(toMenuText, (500, 320))


    # Update the display
    pygame.display.flip()

# Quit Pygame
pygame.quit()
sys.exit()