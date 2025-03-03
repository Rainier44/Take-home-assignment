import math

class BrickQueuer:
    """
    Class that handles different brick placement queueing strategies.
    """
    
    def __init__(self, wall):
        """
        Initialize the QueueingFunctions with a wall object.
        
        Args:
            wall: The Wall object to generate queues for
        """
        self.wall = wall
        # State variables for robot optimization
        self.lastLayedBrickLength = 0
        self.hDirection = 'right'
        self.hPos = 0
        self.vPos = 0
        self.lastFullCourse = None
        self.strideWidth = 0
        self.strideHeight = 0
        self.coursesPerStride = 0
        self.courseRanges = []
        self.laidBricks = {}
        self.hStrideEnd = 0
        self.vStrideEnd = 0
        self.currentStride = 0

    def define_per_course_queue(self) -> list:
        """
        Create a simple per-course brick placement queue.
        
        Returns:
            list: Queue of brick placement coordinates (course, brick_id)
        """
        self.wall.brickQueue = []
        for course in range(self.wall.numCourses):
            for i in range(len(self.wall.bricks[course])):
                self.wall.brickQueue.append((course, i, self.currentStride))
        return self.wall.brickQueue

    def define_robot_optimized_queue(self):
        """
        Define a robot-optimized placement sequence
        Places bricks in strides that the robot can reach.
        
        Returns:
            list: Queue of brick placement coordinates
        """
        # Initialize robot parameters and tracking data
        # Get robot capabilities
        self.wall.brickQueue = []
        self.strideWidth = self.wall.usedRobot.strideWidth
        self.strideHeight = self.wall.usedRobot.strideHeight
        self.coursesPerStride = math.floor(self.strideHeight / self.wall.brickTypes[0].courseHeight)
        
        # Track brick placement status
        self.courseRanges = [None] * self.wall.numCourses  # Stores min/max placement range for each course
        self.laidBricks = {course: set() for course in range(self.wall.numCourses)}
        
        # Current robot position
        self.hPos = 0
        self.vPos = 0
        self.hDirection = 'right'
        
        # Process the wall in strides until complete
        while self.vPos < self.wall.numCourses:
            # Calculate the current stride boundaries
            self.hStrideEnd = min(self.hPos + self.strideWidth, self.wall.wallWidth)
            self.vStrideEnd = min(self.vPos + self.coursesPerStride, self.wall.numCourses)
            self.lastFullCourse = None
            
            # Process current stride area
            self._process_current_stride()
            
            # Move to next stride position
            self._move_to_next_stride()
            
        return self.wall.brickQueue

    def _process_current_stride(self):
        """
        Process the current stride area, placing bricks where possible.
        """
        # Process each course in the current vertical stride
        for course in range(int(self.vPos), int(self.vStrideEnd)):
            currentWidth = 0
            
            # Process each brick in the course
            for brickId in range(len(self.wall.bricks[course])):
                # Skip already placed bricks
                if brickId in self.laidBricks[course]:
                    currentWidth += self.wall.bricks[course][brickId]['type'].length + self.wall.headJoint
                    continue
                
                # Get brick information
                brick = self.wall.bricks[course][brickId]
                brickLength = brick['type'].length
                
                # Check if brick is within the current stride
                if not self._check_within_stride(currentWidth, brickLength):
                    currentWidth += brickLength + self.wall.headJoint
                    continue
                
                # Calculate brick position
                brickStart = currentWidth
                brickEnd = currentWidth + brickLength
                
                # Check if brick has proper support
                if self._check_brick_support(course, brickStart, brickEnd):
                    self._brick_in_queue(course, brickId, brickStart, brickEnd)
                    self.lastLayedBrickLength = brickLength
                
                currentWidth += brickLength + self.wall.headJoint
            
            lastCourse = course
            
            # Check if this course is complete
            if len(self.laidBricks[course]) == len(self.wall.bricks[course]):
                self.lastFullCourse = course

    def _check_within_stride(self, currentWidth, brickLength):
        """
        Check if a brick is within the current horizontal stride.
        
        Args:
            currentWidth: Current width position in the course
            brickLength: Length of the brick
            
        Returns:
            bool: True if brick is within stride, False otherwise
        """
        # Skip bricks that are completely before the horizontal position
        if currentWidth + brickLength <= self.hPos:
            return False
        
        # Skip bricks that start after the stride end
        if currentWidth >= self.hStrideEnd:
            return False
        
        return True

    def _check_brick_support(self, course, brickStart, brickEnd):
        """
        Check if a brick has proper support from the course below.
        
        Args:
            course: Current Course number
            brickStart: Start position of the brick
            brickEnd: End position of the brick
            
        Returns:
            bool: True if brick has proper support, False otherwise
        """
        if course == 0:
            return True  # First course always has support
            
        if self.courseRanges[course-1] is None:
            return False
                
        supportMin, supportMax = self.courseRanges[course-1]
        return not (brickStart < supportMin or brickEnd > supportMax)

    def _brick_in_queue(self, course, brickId, brickStart, brickEnd):
        """
        Place a brick and update tracking information.
        
        Args:
            course: Course number
            brickId: Brick ID in the course
            brickStart: Start position of the brick
            brickEnd: End position of the brick
        """
        # Add to queue
        self.wall.brickQueue.append((course, brickId, self.currentStride))
        self.laidBricks[course].add(brickId)
        
        # Update the course range
        if self.courseRanges[course] is None:
            self.courseRanges[course] = [brickStart, brickEnd]
        else:
            self.courseRanges[course][0] = min(self.courseRanges[course][0], brickStart)
            self.courseRanges[course][1] = max(self.courseRanges[course][1], brickEnd)

    def _move_to_next_stride(self):
        """
        Calculate the next position for the robot.
        """

        self.currentStride += 1

        # Determine next position based on direction
        if self.hDirection == 'right':
            if self.hStrideEnd >= self.wall.wallWidth:
                # Reached the right edge, move up to the next complete course
                self.vPos = self.lastFullCourse + 1 if self.lastFullCourse is not None else self.vPos + self.coursesPerStride
                self.hDirection = 'left'
            else:
                self.hPos += self.lastLayedBrickLength + self.wall.headJoint
                self.hPos = min(self.hPos, self.wall.wallWidth - self.strideWidth)
        else:  # hDirection == 'left'
            if self.hPos <= 0:
                # Reached the left edge, move up
                self.vPos = self.lastFullCourse + 1 if self.lastFullCourse is not None else self.vPos + self.coursesPerStride
                self.hDirection = 'right'
                self.hPos = max(0, self.hPos)
                
            else:
                # Continue left
                self.hPos -= self.lastLayedBrickLength + self.wall.headJoint
