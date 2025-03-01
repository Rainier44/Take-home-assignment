import matplotlib.pyplot as plt
import matplotlib.patches as patches



class Brick:
    def __init__(self, id: int, name: str, length: float, height: float, courseHeight: float, width: float):
        self.name = name
        self.length = length
        self.height = height
        self.courseHeight = courseHeight
        self.width = width

    
class Wall:
    def __init__(self,bondType: str, wallHeight: float, wallWidth: float, headJoint: float, bedJoint: float):
        self.bondType = bondType
        self.wallHeight = wallHeight
        self.wallWidth = wallWidth
        self.headJoint = headJoint
        self.bedJoint = bedJoint

    def defineBrickGrid2D(self, brickTypes: list[Brick]):
        self.brickTypes = brickTypes
        self.bricks = []

        assert self.brickTypes[0].height == self.brickTypes[1].height, "Brick heights must be equal"

        numCourses = int(self.wallHeight / self.brickTypes[0].courseHeight)

        fullBrick = self.brickTypes[0]
        halfBrick = self.brickTypes[1]

        for course in range(numCourses):
            yPos = course * self.brickTypes[0].courseHeight
            xPos = 0

            if self.bondType == 'stretcher':
                if course % 2 == 0:
                    startBrickType = fullBrick
                else:
                    startBrickType = halfBrick
                self.bricks.append({'type': startBrickType, 'position': (xPos, yPos)})
                xPos += startBrickType.length + self.headJoint

                while xPos < self.wallWidth:
                    remainingWidth = self.wallWidth - xPos

                    if remainingWidth >= fullBrick.length:
                        brickType = fullBrick
                    else:
                        brickType = halfBrick

                    self.bricks.append({'type': brickType, 'position': (xPos, yPos)})

                    xPos += brickType.length + self.headJoint

                    
    
    def plotBrickGrid2D(self):
        fig, ax = plt.subplots(figsize=(10, 8))
        for i in range(len(self.bricks)):
            length = self.bricks[i]['type'].length
            height = self.bricks[i]['type'].height
            x = self.bricks[i]['position'][0]
            y = self.bricks[i]['position'][1]

            rect = patches.Rectangle((x,y),
                                     length,
                                     height,
                                     linewidth=0, 
                                     facecolor=(0.5,0.5,0.5,0.5))
            ax.add_patch(rect)
            
        ax.autoscale_view()
        plt.grid(True)
        plt.xlabel('X Position')
        plt.ylabel('Y Position')
        plt.title('Brick Layout')
        fig.canvas.draw()
        plt.show()

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
    wall1.plotBrickGrid2D()
                
if __name__ == '__main__':
    main()


        
    