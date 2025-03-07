import matplotlib.pyplot as plt
import matplotlib.patches as patches

from queueing_functions import BrickQueuer
from colors import colors



class Brick:
    def __init__(self, length: float, height: float, courseHeight: float, width: float):
        # Initialize the brick type
        self.length = length
        self.height = height
        self.courseHeight = courseHeight
        self.width = width

class Robot:
    def __init__(self, strideWidth: float, strideHeight: float, placementSequence: str = 'perCourse'):
        # Initialize the robot
        self.strideWidth = strideWidth
        self.strideHeight = strideHeight

        self.placementSequence = placementSequence
    
class Wall:
    def __init__(self,bondType: str, wallHeight: float, wallWidth: float, headJoint: float, usedRobot: Robot):
        #Initialize the wall
        self.bondType = bondType
        self.wallHeight = wallHeight
        self.wallWidth = wallWidth
        self.headJoint = headJoint
        
        self.usedRobot = usedRobot

    def _getStretcherBondPattern(self, course: int, yPos: float):
        # Define the stretcher bond pattern for the wall
        fullBrick = self.brickTypes[0]
        halfBrick = self.brickTypes[1]
        xPos = 0

        # Start with a full brick if the course is even, otherwise start with a half brick
        if course % 2 == 0:
            startBrickType = fullBrick
        else:
            startBrickType = halfBrick
        self.bricks[course].append({'type': startBrickType, 'ID': 0, 'position': (xPos, yPos)})
        xPos += startBrickType.length + self.headJoint

        brickId = 1
        while xPos < self.wallWidth:

            remainingWidth = self.wallWidth - xPos

            if remainingWidth >= fullBrick.length:
                brickType = fullBrick
            else:
                brickType = halfBrick

            self.bricks[course].append({'type': brickType, 'ID': brickId, 'position': (xPos, yPos)})

            xPos += brickType.length + self.headJoint
            brickId += 1

    def _getFlemishBondPattern(self, course: int, yPos: float):
        fullBrick = self.brickTypes[0]  
        halfBrick = self.brickTypes[1]
        headerBrick = self.brickTypes[2] 
        halfHeaderBrick = self.brickTypes[3]
 
        xPos = 0
        brickId = 1

        if course % 2 == 0:
            startBrickType = halfBrick
        else:
            startBrickType = halfHeaderBrick
        self.bricks[course].append({'type': startBrickType, 'ID': 0, 'position': (xPos, yPos)})
        xPos += startBrickType.length + self.headJoint

        while xPos < self.wallWidth:
            if brickId % 2 == course % 2:
                isHeader = False
            else:
                isHeader = True

            remainingWidth = self.wallWidth - xPos

            currentBrick = headerBrick if isHeader else fullBrick

            if remainingWidth < currentBrick.length:
                if remainingWidth >= halfHeaderBrick.length:
                    currentBrick = halfHeaderBrick
                elif remainingWidth >= halfBrick.length:
                    currentBrick = halfBrick
                else:
                    break

            # Add the brick to the wall
            self.bricks[course].append({'type': currentBrick, 'ID': brickId, 'position': (xPos, yPos)})
            
            # Move to the next position
            xPos += currentBrick.length + self.headJoint
            brickId += 1

        

    def defineBrickGrid2D(self, brickTypes: list[Brick]):
        self.brickTypes = brickTypes

        for i in range(1,len(self.brickTypes)):
            assert self.brickTypes[i-1].height == self.brickTypes[i].height, "Brick heights must be equal"

        self.numCourses = int(self.wallHeight / self.brickTypes[0].courseHeight)

        self.bricks = [[] for _ in range(self.numCourses)]

        self.queuer = BrickQueuer(self)

        for course in range(self.numCourses):
            yPos = course * self.brickTypes[0].courseHeight

            if self.bondType == 'stretcher':
                self._getStretcherBondPattern(course, yPos)
            elif self.bondType == 'flemish':
                self._getFlemishBondPattern(course, yPos)
            else:
                raise ValueError('Invalid bond pattern type')


    def definePlacementSequence(self):
        # Define the placement sequence of the bricks
        self.brickQueue = []
        if self.bondType in ['stretcher','flemish']:

            if self.usedRobot.placementSequence == 'perCourse':
                self.queuer.define_per_course_queue()

            if self.usedRobot.placementSequence == 'robotOptimized':
                self.queuer.define_robot_optimized_queue()


    
def plotBrickGrid2D(wall: Wall):
    plt.ion()
    fig, ax = plt.subplots(figsize=(10, 8))
    for course in range(wall.numCourses):
        for i in range(len(wall.bricks[course])):
            length = wall.bricks[course][i]['type'].length
            height = wall.bricks[course][i]['type'].height
            x = wall.bricks[course][i]['position'][0]
            y = wall.bricks[course][i]['position'][1]

            rect = patches.Rectangle((x,y),
                                    length,
                                    height,
                                    linewidth=0, 
                                    facecolor=(0.5,0.5,0.5,0.5))
            ax.add_patch(rect)
    
    # Connect the key press event
    fig.canvas.mpl_connect('key_press_event', lambda event: _handle_key_press(wall, event, fig, ax))
            
    ax.autoscale_view()
    plt.grid(True)
    plt.xlabel('X Position')
    plt.ylabel('Y Position')
    plt.title(f'Wall with {wall.bondType} bond, Press Enter To add Brick')
    fig.canvas.draw()
    plt.show(block=True)

def _placeBrickInVisual(fig, ax, brick,stride):
    length = brick['type'].length
    height = brick['type'].height
    x = brick['position'][0]
    y = brick['position'][1]

    rect = patches.Rectangle((x,y),
                            length,
                            height,
                            linewidth=1, 
                            edgecolor='black',
                            facecolor=colors[stride])  
    ax.add_patch(rect)
    
    # Update the canvas
    fig.canvas.draw_idle()

def _handle_key_press(wall: Wall, event, fig, ax):
    if event.key == 'enter' and wall.brickQueue:
        course, brick_idx, stride = wall.brickQueue.pop(0)
        
        brick = wall.bricks[course][brick_idx]
        _placeBrickInVisual(fig, ax, brick, stride)
            
            

def main():
    brickWidth = 100 # mm
    brickHeight = 50 # mm
    courseHeight = 62.5 # mm
    fullBrickLength = 210 # mm
    halfBrickLength = 100 # mm

    fullBrick = Brick(fullBrickLength, brickHeight, courseHeight, brickWidth)
    halfBrick = Brick(halfBrickLength, brickHeight, courseHeight, brickWidth)
    headerBrick = Brick(brickWidth, brickHeight, courseHeight, brickWidth)
    halfHeaderBrick = Brick(brickWidth/2, brickHeight, courseHeight, brickWidth)

    wallHeight = 2000 # mm
    wallWidth = 2300 # mm
    headJoint = 10 # mm
    bedJoint = 12.5 # mm

    strideWidth = 800 # mm
    strideHeight = 1300 # mm

    placementSequence = 'robotOptimized'

    robot1 = Robot(strideWidth, strideHeight, placementSequence)

    while True:
            bond_choice = input("Choose bond type (1 for stretcher, 2 for flemish) [default: 1]: ").strip()
            
            # Default to stretcher if empty input
            if bond_choice == "":
                bondType = 'stretcher'
                break
                
            # Process valid choices
            if bond_choice == "1":
                bondType = 'stretcher'
                break
            elif bond_choice == "2":
                bondType = 'flemish'
                break
            else:
                print("Invalid choice. Please enter 1 for stretcher or 2 for flemish.")

    wall1 = Wall(bondType, wallHeight, wallWidth, headJoint, robot1)

    wall1.defineBrickGrid2D([fullBrick, halfBrick, headerBrick, halfHeaderBrick])
    wall1.definePlacementSequence()
    plotBrickGrid2D(wall1)
                
if __name__ == '__main__':
    main()


        
    