# Pyramid Chart Generator

A Python application for creating organizational pyramid charts with images and names.

## Features
- Create customizable pyramid charts
- Add images and names to positions
- Export to PDF
- Save and load assignments
- Automatic image management
- Responsive design

## Requirements
- Python 3.8 or higher
- Tkinter (usually comes with Python)
- Pillow and ReportLab libraries

## Installation
1. Clone the repository
2. Create a virtual environment: `python -m venv venv`
3. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - Unix/MacOS: `source venv/bin/activate`
4. Install requirements: `pip install -r requirements.txt`

## Usage
1. Run `python src/pyramid_chart.py`
2. Enter the number of positions in your pyramid
3. Click "Manage Names" to add people and their photos
4. Click positions to assign people
5. Use "Save Assignments" to preserve your work
6. Export to PDF when ready

## File Structure
- `src/pyramid_chart.py` - Main application code
- `images/` - Directory for storing photos
- `name_database.json` - Database of names and image paths (auto-generated)

## License
MIT License - see LICENSE file for details

## Author
ItsRene

Copyright © 2025
