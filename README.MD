# Monumental Take Home Assignment for Forward Deployed Robotics Engineer

## Project Overview
This project simulates a masonry robot that places bricks to build walls using different bonding patterns (stretcher or flemish). The visualization allows you to see the brick placement sequence.

## Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)

### Setup Instructions
1. Clone the repository:
   ```
   git clone https://github.com/Rainier44/Take-Home-Assignment.git
   cd Take-Home-Assignment
   ```

2. Create a virtual environment:
   ```
   python -m venv venv
   ```

3. Activate the virtual environment:
   - On Windows:
     ```
     venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```
     source venv/bin/activate
     ```

4. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

## Running the Application

To run the masonry robot simulation:

```
python masonry-robot.py
```

When the application starts:
1. You'll be prompted to choose a bond type (1 for stretcher, 2 for flemish)
2. The visualization window will open showing the brick layout
3. Press Enter key to add bricks according to the placement sequence, hold Enter to quickly lay the bricks

## Project Structure

- `masonry-robot.py`: Main application file that handles the robot simulation and visualization
- `queueing_functions.py`: Contains functions for determining the brick placement sequence
- `colors.py`: Defines color schemes used in the visualization
- `requirements.txt`: Lists all Python dependencies

## Features

- Two bond pattern options: stretcher and flemish
- Interactive visualization with step-by-step brick placement
- Optimization of brick placement sequence based on robot parameters
- 2D visualization of the wall construction process

## Controls

- Press the Enter key to place the next brick in the sequence
- Close the visualization window to exit the application