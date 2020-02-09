from os import path, name
from app.functions import log
import app.functions as functions

scriptname = path.basename(__file__)
log(scriptname)

log("debug", "functions.video_output_path", functions.video_output_path)

choosing_clips = True
chosen_clips = []

print("Insert desired clip length in mm:ss")
print("You can make as many clips as liked, leave clip length empty (just press ENTER) to stop making clips")

while choosing_clips:
    clip_length = input("Length: ").strip()
    if clip_length == "":
        log("debug", "clip_length", "\"{0}\", done clipping".format(clip_length))
        choosing_clips = False
    else:
        log("debug", "clip_length", clip_length)
        try:
            clip_length_split = clip_length.split(":")
            minutes = float(clip_length_split[0])
            seconds = float(clip_length_split[1])
            clip_length = (minutes * 60) + seconds
        except IndexError:
            # If no : is used, assume seconds
            seconds = float(clip_length)
            clip_length = seconds
        except ValueError:
            print("Please enter an empty value or a proper min:second value (f.e. 5:23)")
            
        from random import uniform
        from moviepy.editor import *
        full_video = VideoFileClip(functions.video_output_path)
        full_duration = full_video.duration

        log("debug", "full_duration", full_duration)

        # Check if there's enough space in the video to get clip from
        subclip_attempts = 0
        allowed_subclip_attempts = 100  # How many times there can be searched for more subclip space before giving up
        clip_start_and_end_chosen = False
        while not clip_start_and_end_chosen:
            if subclip_attempts >= allowed_subclip_attempts:
                log("warning", "exit", "No more subclips possible")
                input("No more subclips possible! Tried {0} times. Press ENTER to exit".format(subclip_attempts))
                exit()

            clip_start = round(uniform(0, full_duration - clip_length), 2)
            clip_end = clip_start + clip_length

            if len(chosen_clips) == 0:
                clip_start_and_end_chosen = True
                    
            else:
                for chosen_clip in chosen_clips:
                    print(chosen_clip)
                    print(str(clip_start) + " " + str(clip_end))
                    
                    if not chosen_clip[0] < clip_start < chosen_clip[1] and not chosen_clip[0] < clip_end < chosen_clip[1]:
                        clip_start_and_end_chosen = True
                        break
                subclip_attempts += 1
        
        log("debug", "clip_start", clip_start)
        log("debug", "clip_end", clip_end)

        clip = full_video.subclip(clip_start, clip_end)

        print("The application will now show the first 5 and last 5 seconds of the clip")

        clip.subclip(0, 5).preview()
        clip.subclip(clip.duration - 5, clip.duration).preview()

        clip_approved = input("Is this clip good? (y or empty if Yes, n if no): ").lower().strip()
        if clip_approved in ["", "y", "ye", "yes", "ys"]:
            clip_filename = path.splitext(path.basename(functions.video_output_path))[0]

            chosen_clips.append((clip_start, clip_end))

            clip.write_videofile(
                functions.video_output_path.replace(
                    clip_filename, 
                    "clip {0} ({1}-{2}) {3}".format(len(chosen_clips), clip_start, clip_end, clip_filename)))


# Startfile only works in Windows
if name == "nt":
    from os import startfile
    log("debug", "os", "\"{0}\", opening explorer")
    startfile(path.realpath(functions.video_output_dir))

log("debug", "status", "done")