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
        
    def define_per_course_queue(self):
        """
        Create a simple per-course brick placement queue.
        
        Returns:
            list: Queue of brick placement coordinates (course, brick_id, stride number)
        """
        self.wall.brickQueue = []
        for course in range(self.wall.numCourses):
            for i in range(len(self.wall.bricks[course])):
                self.wall.brickQueue.append((course, i, 0))

    def define_robot_optimized_queue(self):
        """
        Define a robot-optimized placement sequence
        Places bricks in strides that the robot can reach.
        
        """
        # Initialize robot parameters and tracking data

        # State variables for robot optimization
        self.hDirection = 'right'       # Horizontal direction of the robot
        self.hPos = 0                   # Horizontal position of the robot
        self.vPos = 0                   # Vertical position of the robot in courses
        self.lastFullCourse = None      # Last course that was fully laid
        self.coursesPerStride = 0       # Number of courses per stride
        self.hStrideEnd = 0             # Horizontal stride end
        self.vStrideEnd = 0             # Vertical stride end
        self.currentStride = 0          # Stride number for coloring bricks per stride
        self.lastLayedBrickLength = 0


        self.supportSegments = [[] for _ in range(self.wall.numCourses)]    # Tracking which segments of a course are layed and therefore offer support


        # Get robot capabilities
        self.wall.brickQueue = []
        self.strideWidth = self.wall.usedRobot.strideWidth
        self.strideHeight = self.wall.usedRobot.strideHeight
        self.coursesPerStride = math.floor(self.strideHeight / self.wall.brickTypes[0].courseHeight)
        
        # Track brick placement status
        self.laidBricks = {course: set() for course in range(self.wall.numCourses)}
        
        # Process the wall in strides until complete
        while self.vPos < self.wall.numCourses:
            # Calculate the current stride boundaries
            self.hStrideEnd = min(self.hPos + self.strideWidth, self.wall.wallWidth)
            self.vStrideEnd = min(self.vPos + self.coursesPerStride, self.wall.numCourses)
            
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

                # Get brick information
                brick = self.wall.bricks[course][brickId]
                brickLength = brick['type'].length
                
                # Check if brick is within the current stride
                if not self._check_within_stride(currentWidth, brickLength, course, brickId):
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
                        
            # Check if this course is complete
            if len(self.laidBricks[course]) == len(self.wall.bricks[course]):
                self.lastFullCourse = course

    def _check_within_stride(self, currentWidth, brickLength, course, brickId):
        """
        Check if a brick is within the current horizontal stride.
        
        Args:
            currentWidth: Current width position in the course
            brickLength: Length of the brick
            course: Current course number
            brickId: Brick ID in the course
            
        Returns:
            bool: True if brick is within stride, False otherwise
        """

        # Skip bricks that are already laid
        if brickId in self.laidBricks[course]:
            return False
        
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
        # If this is the first course, the brick is supported
        if course == 0:
            return True

        # Check if the brick is fully supported by segments in the course below
        for segment_start, segment_end in self.supportSegments[course - 1]:
            if segment_start <= brickStart and segment_end >= brickEnd:
                return True
            
        return False

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
        
        # Calculate the end of the support segment
        support_end = min(brickEnd + self.wall.headJoint, self.wall.wallWidth)
        
        # Add new support segment
        self._add_support_segment(course, brickStart, support_end)

    def _add_support_segment(self, course, start, end):
        """
        Add a new support segment and merge overlapping segments.
        Handles all cases of overlapping and adjacent segments.
        
        Args:
            course: Course number
            start: Start position of new segment
            end: End position of new segment
        """
        # If no existing segments, add the new one
        if not self.supportSegments[course]:
            self.supportSegments[course] = [(start, end)]
            return

        # Find all segments that overlap with or are next to the new segment
        overlapping_indices = []
        min_start = start
        max_end = end
        
        for i, (seg_start, seg_end) in enumerate(self.supportSegments[course]):
            # Check for overlap or being next to the new segment
            if min(end, seg_end) >= max(start, seg_start):
                overlapping_indices.append(i)
                min_start = min(min_start, seg_start)
                max_end = max(max_end, seg_end)

        # If no overlaps found, insert the new segment in the correct position
        if not overlapping_indices:
            # Find insertion point to maintain order
            insert_pos = 0
            for i, (seg_start, _) in enumerate(self.supportSegments[course]):
                if start > seg_start:
                    insert_pos = i + 1
            
            self.supportSegments[course].insert(insert_pos, (start, end))
            return

        # Create new segment list with merged segment
        new_segments = []
        for i, segment in enumerate(self.supportSegments[course]):
            if i < min(overlapping_indices):
                # Add segments before the merged one
                new_segments.append(segment)
            elif i == min(overlapping_indices):
                # Add the merged segment
                new_segments.append((min_start, max_end))
            elif i > max(overlapping_indices):
                # Add segments after the merged one
                new_segments.append(segment)
        
        self.supportSegments[course] = new_segments

    def _move_to_next_stride(self):
        """
        Calculate the next position for the robot.
        """
        # Increment stride counter
        self.currentStride += 1

        # Determine next position based on direction and proximity to edges
        if self.hDirection == 'right':
            if self.hStrideEnd >= self.wall.wallWidth:
                # Reached the right edge, move up to the next complete course
                self.vPos = self.lastFullCourse + 1 
                self.hDirection = 'left'
            else:
                # Continue right
                self.hPos += (self.lastLayedBrickLength + self.wall.headJoint)
                self.hPos = min(self.hPos, self.wall.wallWidth - self.strideWidth)
        else:  # hDirection == 'left'
            if self.hPos <= 0:
                # Reached the left edge, move up
                self.vPos = self.lastFullCourse + 1 
                self.hDirection = 'right'
                self.hPos = max(0, self.hPos)
            else:
                # Continue left
                self.hPos -= (self.lastLayedBrickLength + self.wall.headJoint)
