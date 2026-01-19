import os
import moviepy.editor as mp
from moviepy.config import change_settings
from PIL import Image, ImageDraw
import numpy as np

# ==========================================
# CONFIGURATION
# ==========================================
# GitHub uses standard Linux paths. We look in the current folder.
change_settings({"IMAGEMAGICK_BINARY": r"/usr/bin/convert"})

# Updated Paths to point to your GitHub repository folders
MAIN_VIDEO_PATH = "sample.mp4"
BG_VIDEO_PATH   = "Assets/ff-background-video.mp4"
LOGO_PATH       = "Assets/ff-logo.png"
FONT_PATH       = "Assets/Fredoka-Bold.ttf"
OUTPUT_FOLDER   = "output"
OUTPUT_NAME     = "final_facebook_video.mp4"

if not os.path.exists(OUTPUT_FOLDER):
    os.makedirs(OUTPUT_FOLDER)

OUTPUT_PATH = os.path.join(OUTPUT_FOLDER, OUTPUT_NAME)

# Content & Layout Settings
CAPTION_TEXT = "A morning raid turned into a fatal tragedy. Three shots were fired, and a life was lost in the blink of an eye. Minneapolis is demanding the truth about what happened today."

# Layout Coordinates
MAIN_X, MAIN_Y = 254.7, 116
MAIN_W, MAIN_H = 570.7, 1016
BORDER_COLOR = (2, 150, 177)  # #0296b1
BORDER_RADIUS = 40
BORDER_WEIGHT = 6

LOGO_X, LOGO_Y = 293.3, 149.8
LOGO_W, LOGO_H = 103.7, 72.6

BOX_COLOR = (2, 150, 177)
BOX_X, BOX_Y = 0, 1094.5
BOX_W, BOX_H = 1080, 255.5

FONT_X, FONT_Y = 42, 1124.2
FONT_SIZE = 36
FONT_COLOR = "white"
CANVAS_SIZE = (1080, 1350)

# ==========================================
# SCRIPT LOGIC
# ==========================================

print("--- Starting Video Processing ---")

# 1. Load Clips
print("[1/7] Loading video files...")
bg_video = mp.VideoFileClip(BG_VIDEO_PATH).resize(CANVAS_SIZE)

# Force RGB to avoid color space issues that cause the "thermal" look
main_video = (mp.VideoFileClip(MAIN_VIDEO_PATH)
              .resize(width=MAIN_W, height=MAIN_H)
              .set_audio(mp.VideoFileClip(MAIN_VIDEO_PATH).audio))

# 2. Create Rounded Border
print("[2/7] Generating rounded border...")
border_canvas_size = (int(MAIN_W + BORDER_WEIGHT*2), int(MAIN_H + BORDER_WEIGHT*2))
border_img = Image.new("RGBA", border_canvas_size, (0, 0, 0, 0))
draw_border = ImageDraw.Draw(border_img)
draw_border.rounded_rectangle(
    (0, 0, border_canvas_size[0], border_canvas_size[1]), 
    radius=BORDER_RADIUS + BORDER_WEIGHT, 
    fill=BORDER_COLOR
)
border_clip = (mp.ImageClip(np.array(border_img))
               .set_duration(main_video.duration)
               .set_position((MAIN_X - BORDER_WEIGHT, MAIN_Y - BORDER_WEIGHT)))

# 3. Create Mask (Correctly Formatted)
print("[3/7] Applying rounded mask...")
# Use 'L' mode for a 1-channel grayscale mask
mask_pill = Image.new("L", (int(MAIN_W), int(MAIN_H)), 0)
draw_mask = ImageDraw.Draw(mask_pill)
draw_mask.rounded_rectangle((0, 0, MAIN_W, MAIN_H), radius=BORDER_RADIUS, fill=255)

# Convert to a normalized numpy array (0.0 to 1.0)
mask_array = np.array(mask_pill).astype(float) / 255.0
mask_clip = mp.ImageClip(mask_array, ismask=True).set_duration(main_video.duration)

# Apply the mask
main_video = main_video.set_mask(mask_clip)

# 4. Load Logo
print("[4/7] Overlaying logo...")
logo = (mp.ImageClip(LOGO_PATH)
        .set_duration(main_video.duration)
        .resize(width=LOGO_W, height=LOGO_H)
        .set_position((LOGO_X, LOGO_Y)))

# 5. Create Color Box
print("[5/7] Adding color box background...")
color_box = (mp.ColorClip(size=(int(BOX_W), int(BOX_H)), color=BOX_COLOR)
             .set_duration(main_video.duration)
             .set_position((BOX_X, BOX_Y)))

# 6. Create Text
print("[6/7] Generating text overlay...")
txt_clip = (mp.TextClip(CAPTION_TEXT, fontsize=FONT_SIZE, color=FONT_COLOR, 
                        font=FONT_PATH, method='caption', size=(996, None))
            .set_duration(main_video.duration)
            .set_position((FONT_X, FONT_Y)))

# 7. Composition
print("[7/7] Finalizing composition...")
final_video = mp.CompositeVideoClip([
    bg_video,
    border_clip,
    main_video.set_position((MAIN_X, MAIN_Y)),
    logo,
    color_box,
    txt_clip
], size=CANVAS_SIZE).set_duration(main_video.duration)

# 8. Render
print(f"--- Rendering Video to {OUTPUT_PATH} ---")
final_video.write_videofile(OUTPUT_PATH, fps=24, codec="libx264", audio_codec="aac", temp_audiofile='temp-audio.m4a', remove_temp=True, logger='bar')

print(f"\nSuccess! Video saved to: {OUTPUT_PATH}")
