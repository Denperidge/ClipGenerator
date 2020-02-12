from os import path, name
from app.functions import log
import app.functions as functions

modes = ["random", "exact"]
def prompt_mode():
    selected_mode = input("1: {0} 2: {1}: ".format(modes[0], modes[1])).lower().strip()
    if selected_mode == "1" or selected_mode == "2":
        return modes[int(selected_mode) - 1]
    else:
        return prompt_mode()


def prompt_time():
    clip_length = input("Length: ").strip()
    log("debug", "raw clip_length", clip_length)

    try:
        # If empty value, return False
        if clip_length == "":
            return False
            
        # If mm:ss
        elif ":" in clip_length:
            clip_length_split = clip_length.split(":")
            minutes = float(clip_length_split[0])
            seconds = float(clip_length_split[1])
            clip_length = (minutes * 60) + seconds
            log("debug", "clip_length (from mm:ss)", clip_length)
            return clip_length
        # If seconds
        else:
            seconds = float(clip_length)
            clip_length = seconds
            log("debug", "clip_length (from seconds)", clip_length)
            return clip_length
    except ValueError:
        # If not empty nor numeric, reprompt recursively
        print("Please enter an empty value, the desired seconds or a min:sec value (f.e. 5:23)")
        return prompt_time()

def random_subclip(clip_length):
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
                #print(chosen_clip)
                #print(str(clip_start) + " " + str(clip_end))
                    
                if not chosen_clip[0] < clip_start < chosen_clip[1] and not chosen_clip[0] < clip_end < chosen_clip[1]:
                    clip_start_and_end_chosen = True
                    break
            subclip_attempts += 1
    
    return clip_start, clip_end

def exact_subclip(clip_start):
    clip_end = prompt_time()
    return clip_start, clip_end


scriptname = path.basename(__file__)
log(scriptname)

log("debug", "functions.video_output_path", functions.video_output_path)

choosing_clips = True
chosen_clips = []

print("Do you want to generate random clips, or set a specific start and endtime?")
mode, time_prompt = prompt_mode()

print("Insert desired clip {0} in mm:ss or seconds".format("length" if mode == modes[0] else "start"))
print("You can make as many clips as liked, leave clip length empty (just press ENTER) to stop making clips")

while choosing_clips:
    clip_length_or_start = prompt_time()
    if clip_length_or_start == False:  # If no value returned, finish clipping
        log("debug", "clip_length_or_start", "\"{0}\", done clipping".format(clip_length_or_start))
        choosing_clips = False
    else:
        from random import uniform
        from moviepy.editor import *
        full_video = VideoFileClip(functions.video_output_path)
        full_duration = full_video.duration
        log("debug", "full_duration", full_duration)
    

        if mode == modes[0]:
            clip_start, clip_end = random_subclip(clip_length_or_start)
        elif mode == modes[1]:
            clip_start, clip_end = exact_subclip(clip_length_or_start)
        
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

            # The bitrate won't go higher than the source file, but has to be put high to achieve max quality output
            clip.write_videofile(
                functions.video_output_path.replace(
                    clip_filename, 
                    "clip {0} ({1}-{2}) {3}".format(len(chosen_clips), clip_start, clip_end, clip_filename)), bitrate="12000k")


# Startfile only works in Windows
if name == "nt":
    from os import startfile
    log("debug", "os", "\"{0}\", opening explorer")
    startfile(path.realpath(functions.video_output_dir))

log("debug", "status", "done")