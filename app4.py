import os
import random
import re
import subprocess
from datetime import datetime
from urllib.parse import quote

# Emojis and default tags
emojis = ["🎬", "📺", "🎥", "📚", "📝", "🔥", "🚀", "⭐", "💡", "🎧"]
tags_default = ["#lesson", "#chapter", "#study", "#watching", "#learning"]

# Smart tags for specific keywords
smart_tags = {
    "intro": "#beginner",
    "project": "#project",
    "advanced": "#advanced",
    "bonus": "#bonus",
    "exercise": "#exercise"
}

def calculate_progress(text):
    """Calculate the progress percentage based on checked items."""
    total = len(re.findall(r"- \[[x ]\] ", text, re.IGNORECASE))
    checked = len(re.findall(r"- \[x\] ", text, re.IGNORECASE))
    percent = int((checked / total) * 100) if total > 0 else 0
    print(f"Progress calculation: {checked}/{total} items checked ({percent}%)")
    return percent

def progress_bar(percent):
    """Generate a progress bar with green and white squares."""
    blocks = int(percent / 10)
    empty = 10 - blocks
    return "🟩" * blocks + "⬜" * empty

def get_video_duration(file_path):
    """Extract video duration using ffprobe."""
    try:
        result = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", file_path],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
        if result.returncode != 0:
            print(f"Error running ffprobe on {file_path}: {result.stderr}")
            return 0.0
        seconds = float(result.stdout.strip())
        print(f"Duration for {file_path}: {seconds} seconds")
        return seconds
    except Exception as e:
        print(f"Exception in get_video_duration for {file_path}: {str(e)}")
        return 0.0

def format_time(seconds):
    """Format seconds into hours and minutes."""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    return f"{hours}h {minutes}m" if hours > 0 else f"{minutes}m"

def get_smart_tag(video_name):
    """Return a smart tag based on video name keywords."""
    name = video_name.lower()
    for keyword, tag in smart_tags.items():
        if keyword in name:
            return tag
    return ""

def create_dashboard_for_folder(folder_path, dashboards_dir):
    """Create a checklist file for a folder containing videos in the dashboards directory."""
    folder_name = os.path.basename(folder_path)
    # Generate unique checklist filename based on folder name
    safe_folder_name = re.sub(r'[^\w\-]', '_', folder_name)  # Replace special characters with underscores
    dashboard_file = os.path.join(dashboards_dir, f"checklist_{safe_folder_name}.md")
    
    video_extensions = ('.mp4', '.mkv', '.avi', '.mov', '.flv', '.webm', '.wmv', '.mpeg', '.mpg')
    videos = [file for file in os.listdir(folder_path) if file.lower().endswith(video_extensions)]

    if not videos:
        print(f"No videos found in {folder_path}")
        return None, 0, 0, 0

    checked_files = set()
    if os.path.exists(dashboard_file):
        with open(dashboard_file, "r", encoding="utf-8") as old_file:
            for line in old_file:
                match = re.match(r"- \[x\] 🎞 \[(.+?)\]", line, re.IGNORECASE)
                if match:
                    checked_files.add(match.group(1).lower())  # Case-insensitive comparison
                    print(f"Checked file found: {match.group(1)}")

    emoji = random.choice(emojis)
    tag = random.choice(tags_default)

    next_up = None
    total_time = 0.0
    watched_time = 0.0
    video_data = []

    # Collect video information
    for video in sorted(videos, key=str.lower):  # Sort case-insensitively
        file_path = os.path.join(folder_path, video)
        duration = get_video_duration(file_path)
        total_time += duration
        if video.lower() in checked_files:
            watched_time += duration
        video_data.append((video, duration))

    remaining_time = total_time - watched_time
    percent_time = int((watched_time / total_time) * 100) if total_time > 0 else 0
    print(f"Time progress for {folder_name}: {watched_time}/{total_time} seconds ({percent_time}%)")

    # Find the next unwatched video
    for video in sorted(videos, key=str.lower):
        if video.lower() not in checked_files:
            next_up = video
            break

    # Write checklist file
    with open(dashboard_file, 'w', encoding='utf-8') as f:
        f.write(f"# {emoji} {folder_name}\n")
        f.write(f"**📌 Tag:** {tag}\n\n")
        if next_up:
            f.write(f"> [!note] 🎯 **Next Session:** `{next_up}`\n\n")
        f.write("> [!tip] Click on a video name to open it directly.\n\n")

        for video, duration in video_data:
            status = "x" if video.lower() in checked_files else " "
            file_path = os.path.normpath(os.path.join(folder_path, video))
            file_url = f"file:///{quote(file_path.replace(os.sep, '/'))}"
            duration_fmt = format_time(duration)
            auto_tag = get_smart_tag(video)
            tag_display = f" {auto_tag}" if auto_tag else ""
            f.write(f"- [{status}] 🎞 [{video}]({file_url}) ⏱ `{duration_fmt}` {tag_display}\n")

    percent = calculate_progress(open(dashboard_file, 'r', encoding='utf-8').read())

    # Append summary statistics
    with open(dashboard_file, 'a', encoding='utf-8') as f:
        f.write("\n---\n")
        f.write(f"**🎯 Session Progress:** `{percent}%` {progress_bar(percent)}\n")
        f.write(f"\n**⏳ Time Progress:** `{percent_time}%` {progress_bar(percent_time)}\n")
        f.write(f"\n📦 Total Course Time: `{format_time(total_time)}`")
        f.write(f"\n🕒 Remaining Time: `{format_time(remaining_time)}`\n")
        f.write(f"\n📅 Last Updated: `{datetime.now().strftime('%Y-%m-%d %H:%M')}`\n")
        f.write("\n> [!success] Statistics calculated automatically.\n")

    print(f"Created dashboard: {dashboard_file}")
    return dashboard_file, percent, total_time, watched_time

def create_main_index(base_path, dashboards):
    """Create the main Index.md file with links to all dashboards."""
    index_file = os.path.join(base_path, "Index.md")
    with open(index_file, 'w', encoding='utf-8') as f:
        f.write("# 📂 Main Course Dashboard\n")
        f.write("> [!info] List of all courses and their progress\n\n")
        f.write("| 🎬 Course | Session Progress | Time Progress |\n")
        f.write("|----------|------------------|---------------|\n")
        for dash, percent, total_time, watched_time in dashboards:
            rel_path = os.path.relpath(dash, base_path).replace(os.sep, "/")
            # Extract course name from checklist filename
            course_name = os.path.splitext(os.path.basename(dash))[0].replace("checklist_", "")
            percent_time = int((watched_time / total_time) * 100) if total_time > 0 else 0
            f.write(f"| [{course_name}]({rel_path}) | {progress_bar(percent)} {percent}% | {progress_bar(percent_time)} {percent_time}% |\n")
    print("✅ Index.md created successfully!")

def main():
    """Main function to process folders and create dashboards."""
    base_path = input("📂 Enter the path to the main courses folder: ")
    if not os.path.exists(base_path):
        print(f"Error: Path {base_path} does not exist.")
        return

    # Create Dashboards folder
    dashboards_dir = os.path.join(base_path, "Dashboards")
    os.makedirs(dashboards_dir, exist_ok=True)
    print(f"Created Dashboards directory: {dashboards_dir}")

    dashboards = []
    for root, dirs, files in os.walk(base_path):
        # Skip the Dashboards folder itself
        if root == dashboards_dir:
            continue
        dash, percent, total_time, watched_time = create_dashboard_for_folder(root, dashboards_dir)
        if dash:
            dashboards.append((dash, percent, total_time, watched_time))

    if dashboards:
        create_main_index(base_path, dashboards)
    else:
        print("⚠️ No videos found in any folder.")

if __name__ == "__main__":
    main()