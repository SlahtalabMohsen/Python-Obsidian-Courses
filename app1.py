import os
import random
import re
import subprocess
from datetime import datetime

# ایموجی‌ها و تگ‌ها
emojis = ["🎬", "📺", "🎥", "📚", "📝", "🔥", "🚀", "⭐", "💡", "🎧"]
tags_default = ["#lesson", "#chapter", "#study", "#watching", "#learning"]

# تگ‌های هوشمند
smart_tags = {
    "intro": "#beginner",
    "project": "#project",
    "advanced": "#advanced",
    "bonus": "#bonus",
    "exercise": "#exercise"
}

def calculate_progress(text):
    total = len(re.findall(r"- \[.\]", text))
    checked = len(re.findall(r"- \[x\]", text, re.IGNORECASE))
    percent = int((checked / total) * 100) if total > 0 else 0
    return percent

def progress_bar(percent):
    blocks = int(percent / 10)
    empty = 10 - blocks
    return "🟩" * blocks + "⬜" * empty

def get_video_duration(file_path):
    """استخراج مدت زمان ویدیو با ffprobe"""
    try:
        result = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", file_path],
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True
        )
        seconds = float(result.stdout.strip())
        return seconds
    except:
        return 0.0

def format_time(seconds):
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    return f"{hours}h {minutes}m" if hours > 0 else f"{minutes}m"

def get_smart_tag(video_name):
    name = video_name.lower()
    for keyword, tag in smart_tags.items():
        if keyword in name:
            return tag
    return ""

def create_dashboard_for_folder(folder_path):
    dashboard_file = os.path.join(folder_path, "checklist.md")
    videos = [file for file in os.listdir(folder_path) if file.endswith(('.mp4', '.mkv', '.avi', '.mov', '.flv', '.webm'))]

    if not videos:
        return None, 0, 0, 0

    checked_files = set()
    if os.path.exists(dashboard_file):
        with open(dashboard_file, "r", encoding="utf-8") as old_file:
            for line in old_file:
                match = re.match(r"- \[x\] 🎞 \[(.+?)\]", line, re.IGNORECASE)
                if match:
                    checked_files.add(match.group(1))

    emoji = random.choice(emojis)
    tag = random.choice(tags_default)
    folder_name = os.path.basename(folder_path)

    next_up = None
    total_time = 0.0
    watched_time = 0.0
    video_data = []

    # جمع‌آوری اطلاعات ویدیوها
    for video in sorted(videos):
        file_path = os.path.join(folder_path, video)
        duration = get_video_duration(file_path)
        total_time += duration
        if video in checked_files:
            watched_time += duration
        video_data.append((video, duration))

    remaining_time = total_time - watched_time
    percent_time = int((watched_time / total_time) * 100) if total_time > 0 else 0

    for video in sorted(videos):
        if video not in checked_files:
            next_up = video
            break

    # نوشتن فایل
    with open(dashboard_file, 'w', encoding='utf-8') as f:
        f.write(f"# {emoji} {folder_name}\n")
        f.write(f"**📌 تگ:** {tag}\n\n")
        if next_up:
            f.write(f"> [!note] 🎯 **جلسه بعدی:** `{next_up}`\n\n")
        f.write("> [!tip] روی نام هر ویدیو کلیک کن تا مستقیماً باز شود.\n\n")

        for video, duration in video_data:
            status = "x" if video in checked_files else " "
            file_path = os.path.join(folder_path, video).replace("\\", "/")
            duration_fmt = format_time(duration)
            auto_tag = get_smart_tag(video)
            tag_display = f" {auto_tag}" if auto_tag else ""
            f.write(f"- [{status}] 🎞 [{video}](file:///{file_path}) ⏱ `{duration_fmt}` {tag_display}\n")

    percent = calculate_progress(open(dashboard_file, 'r', encoding='utf-8').read())

    # اضافه کردن آمار کلی
    with open(dashboard_file, 'a', encoding='utf-8') as f:
        f.write("\n---\n")
        f.write(f"**🎯 پیشرفت جلسات:** `{percent}%` {progress_bar(percent)}\n")
        f.write(f"\n**⏳ پیشرفت زمانی:** `{percent_time}%` {progress_bar(percent_time)}\n")
        f.write(f"\n📦 زمان کل دوره: `{format_time(total_time)}`")
        f.write(f"\n🕒 زمان باقی‌مانده: `{format_time(remaining_time)}`\n")
        f.write(f"\n📅 آخرین بروزرسانی: `{datetime.now().strftime('%Y-%m-%d %H:%M')}`\n")
        f.write("\n> [!success] آمار به‌صورت خودکار محاسبه شد.\n")

    return dashboard_file, percent, total_time, watched_time

def create_main_index(base_path, dashboards):
    index_file = os.path.join(base_path, "Index.md")
    with open(index_file, 'w', encoding='utf-8') as f:
        f.write("# 📂 داشبورد اصلی دوره‌ها\n")
        f.write("> [!info] لیست همه دوره‌ها و درصد پیشرفت آن‌ها\n\n")
        f.write("| 🎬 دوره | پیشرفت جلسات | پیشرفت زمانی |\n")
        f.write("|---------|----------------|----------------|\n")
        for dash, percent, total_time, watched_time in dashboards:
            rel_path = os.path.relpath(dash, base_path).replace("\\", "/")
            course_name = os.path.basename(os.path.dirname(dash))
            percent_time = int((watched_time / total_time) * 100) if total_time > 0 else 0
            f.write(f"| [{course_name}]({rel_path}) | {progress_bar(percent)} {percent}% | {progress_bar(percent_time)} {percent_time}% |\n")
    print("✅ Index.md ساخته شد!")

def main():
    base_path = input("📂 مسیر پوشه اصلی دوره‌ها را وارد کنید: ")
    dashboards = []

    for root, dirs, files in os.walk(base_path):
        if files:
            dash, percent, total_time, watched_time = create_dashboard_for_folder(root)
            if dash:
                dashboards.append((dash, percent, total_time, watched_time))

    if dashboards:
        create_main_index(base_path, dashboards)
    else:
        print("⚠️ هیچ ویدیویی یافت نشد.")

if __name__ == "__main__":
    main()