

#%%
#Going to attempt to get the beer can animation for the power hour.  

import subprocess
import os
import json

output_folder = r"C:\Users\wfloyd\OneDrive - The Kleingers Group\Documents\Python Scripts\MiscellaneousPython"
#%%


url = "https://www.youtube.com/watch?v=z2TAKFJHJnA"

output_path = os.path.join(output_folder, "BeerCan.mp4")



subprocess.run([
    "yt-dlp",
    "-f", "best[ext=mp4]",     # download best single mp4
    "-o", output_path,          # force exact filename
    url
])
#%%


zoloft_url = 'https://www.youtube.com/watch?v=twhvtzd6gXA'
output_path_z = os.path.join(output_folder, "zoloft.mp4")

subprocess.run([
    "yt-dlp",
    "-f", "best[ext=mp4]",     # download best single mp4
    "-o", output_path_z,          # force exact filename
    zoloft_url
])



# %%

#Trim few seconds off
input_file = os.path.join(output_folder, "BeerCan.mp4")
trimmed_file = os.path.join(output_folder, "BeerCan_trimmed.mp4")


# Trim the first 3 seconds
subprocess.run([
    "ffmpeg",
    "-ss", "3",           # start at 3 seconds
    "-i", input_file,     # input file
    "-c", "copy",         # copy video/audio without re-encoding (fast)
    "-y",                 # overwrite if exists
    trimmed_file
], check=True)

print(f"Trimmed video saved as: {trimmed_file}")



# %%

#Define a function to get the size of the videos
def get_video_size(video_path):
    """
    Returns (width, height) of the main video stream using ffprobe
    """
    cmd = [
        "ffprobe",
        "-v", "error",
        "-select_streams", "v:0",
        "-show_entries", "stream=width,height",
        "-of", "json",
        video_path
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    info = json.loads(result.stdout)
    stream = info['streams'][0]
    return stream['width'], stream['height']







#Here's an attempt at directly overlaying two videos
zoloft_video = os.path.join(output_folder, "zoloft.mp4")
can_video = os.path.join(output_folder, "BeerCan_trimmed.mp4")
final_video = os.path.join(output_folder, "FINAL.mp4")

width,height = get_video_size(zoloft_video)

combo_command = [
    "ffmpeg",
    "-i", zoloft_video,
    "-i", can_video,
    "-filter_complex", f'[1:v]scale={width}:{height},colorkey=0x00FF00:0.3:0.2[ckout];[0:v][ckout]overlay[out]',
    "-map","[out]",
    "-map", "0:a?",      # audio from base video (optional)
    "-c:a", "aac",       # encode audio to MP4-compatible AAC
    final_video
]


subprocess.run(combo_command)
print("videos combined")
# %%




