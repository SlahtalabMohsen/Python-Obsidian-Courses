🎓 Python Obsidian Courses Dashboard
This project helps you organize, track, and visualize your progress through video-based courses using Markdown dashboards compatible with Obsidian.

Features
Automatic Course Dashboards: Generates a checklist for each course folder containing video files.
Progress Tracking: Calculates session and time progress based on watched videos.
Smart Tags: Adds tags based on video names (e.g., #beginner, #project).
Video Duration: Extracts and displays video durations using ffprobe.
Main Index: Creates a summary dashboard linking to all course dashboards.
Obsidian-Friendly: All dashboards are Markdown files with clickable links to open videos.
How It Works
Scan Folders: The script scans your main courses folder for subfolders containing video files.
Generate Dashboards: For each course, it creates a Markdown checklist in a Dashboards folder.
Track Progress: Mark videos as watched by checking the boxes in the Markdown file.
View Summary: The main Index.md shows progress for all courses.
Requirements
Python 3.7 or higher
ffmpeg/ffprobe installed and available in your system PATH
Usage
Clone or download this repository.
Prepare Your Courses Folder: Organize your courses so each course is in its own folder containing video files.
Run the Script: python app4.py
Enter the Path: When prompted, enter the path to your main courses folder.
Open Dashboards: Find generated Markdown files in the Dashboards folder and open them in Obsidian.
Supported Video Formats
.mp4, .mkv, .avi, .mov, .flv, .webm, .wmv, .mpeg, .mpg
Example Output
Dashboards/checklist\_<course_name>.md — Checklist for each course
Index.md — Main dashboard with progress bars
Customization
Emojis and Tags: Edit the emojis, tags_default, and smart_tags lists in app4.py to personalize your dashboards.
License
MIT License
