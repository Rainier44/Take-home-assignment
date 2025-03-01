import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np



class Brick:
    def __init__(self, id: int, name: str, length: float, height: float, courseHeight: float, width: float):
        # Initialize the brick type
        self.name = name
        self.length = length
        self.height = height
        self.courseHeight = courseHeight
        self.width = width

    
class Wall:
    def __init__(self,bondType: str, wallHeight: float, wallWidth: float, headJoint: float, bedJoint: float):
        #Initialize the wall
        self.bondType = bondType
        self.wallHeight = wallHeight
        self.wallWidth = wallWidth
        self.headJoint = headJoint
        self.bedJoint = bedJoint

    def getStretcherBondPattern(self, brickTypes: list, course: int, yPos: float):
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

        id = 1
        while xPos < self.wallWidth:

            remainingWidth = self.wallWidth - xPos

            if remainingWidth >= fullBrick.length:
                brickType = fullBrick
            else:
                brickType = halfBrick

            self.bricks[course].append({'type': brickType, 'ID': id, 'position': (xPos, yPos)})

            xPos += brickType.length + self.headJoint
            id += 1

    def defineBrickGrid2D(self, brickTypes: list[Brick]):
        self.brickTypes = brickTypes

        assert self.brickTypes[0].height == self.brickTypes[1].height, "Brick heights must be equal"

        self.numCourses = int(self.wallHeight / self.brickTypes[0].courseHeight)

        self.bricks = np.empty((self.numCourses, 0)).tolist()


        for course in range(self.numCourses):
            yPos = course * self.brickTypes[0].courseHeight

            if self.bondType == 'stretcher':
                self.getStretcherBondPattern(self.brickTypes, course, yPos)


    def definePlacementSequence(self) -> list:
        # Define the placement sequence of the bricks
        self.brick_queue = []
        if self.bondType == 'stretcher':
            # Start with a simple per course placement sequence
            for course in range(self.numCourses):
                for i in range(len(self.bricks[course])):
                    self.brick_queue.append((course, i))

        return self.brick_queue
    
    def plotBrickGrid2D(self):
        plt.ion()
        fig, ax = plt.subplots(figsize=(10, 8))
        for course in range(self.numCourses):
            for i in range(len(self.bricks[course])):
                length = self.bricks[course][i]['type'].length
                height = self.bricks[course][i]['type'].height
                x = self.bricks[course][i]['position'][0]
                y = self.bricks[course][i]['position'][1]

                rect = patches.Rectangle((x,y),
                                        length,
                                        height,
                                        linewidth=0, 
                                        facecolor=(0.5,0.5,0.5,0.5))
                ax.add_patch(rect)
        
        # Connect the key press event
        fig.canvas.mpl_connect('key_press_event', lambda event: self.handle_key_press(event, fig, ax))
                
        ax.autoscale_view()
        plt.grid(True)
        plt.xlabel('X Position')
        plt.ylabel('Y Position')
        plt.title('Brick Layout, Press Enter To add Brick')
        fig.canvas.draw()
        plt.show(block=True)

    def placeBrick(self, fig, ax, brick):
        length = brick['type'].length
        height = brick['type'].height
        x = brick['position'][0]
        y = brick['position'][1]

        rect = patches.Rectangle((x,y),
                                length,
                                height,
                                linewidth=1, 
                                edgecolor='black',
                                facecolor=(1,0,0,1))  
        ax.add_patch(rect)
        
        # Update the canvas
        fig.canvas.draw_idle()

    def handle_key_press(self, event, fig, ax):
        if event.key == 'enter' and self.brick_queue:
            course, brick_idx = self.brick_queue.pop(0)
            
            brick = self.bricks[course][brick_idx]
            self.placeBrick(fig, ax, brick)
            
            

def main():
    brickWidth = 100 # mm
    brickHeight = 50 # mm
    courseHeight = 62.5 # mm
    fullBrickLength = 210 # mm
    halfBrickLength = 100 # mm

    brick1 = Brick(1, 'Full', fullBrickLength, brickHeight, courseHeight, brickWidth)
    brick2 = Brick(2, 'Half', halfBrickLength, brickHeight, courseHeight, brickWidth)

    wallHeight = 2000 # mm
    wallWidth = 2300 # mm
    headJoint = 10 # mm
    bedJoint = 12.5 # mm

    wall1 = Wall('stretcher', wallHeight, wallWidth, headJoint, bedJoint)

    wall1.defineBrickGrid2D([brick1, brick2])
    wall1.definePlacementSequence()
    wall1.plotBrickGrid2D()
                
if __name__ == '__main__':
    main()


        
    