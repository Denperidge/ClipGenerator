from os import path, name
from app.functions import log
import app.functions as functions
from threading import Thread
from re import sub

class Mode:
    def __init__(self, name, clip_length_prompt, second_clip_length_prompt=None):
        self.name = name
        self.clip_length_prompt = clip_length_prompt
        if second_clip_length_prompt is not None:
            self.second_clip_length_prompt = second_clip_length_prompt


random = Mode("random", "Length: ")
exact = Mode("exact", "Start time: ", "End time: ")
def prompt_mode():
    selected_mode = input("1: {0} 2: {1}: ".format(random.name, exact.name)).lower().strip()
    if selected_mode == "1":
        return random
    elif selected_mode == "2":
        return exact
    else:
        return prompt_mode()


def prompt_time(clip_length_prompt):
    clip_length = input(clip_length_prompt)
    clip_length = sub("[^0-9:.]", "", clip_length)  # Filter out anything non-numeric/':'

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
        return prompt_time(clip_length_prompt)

def random_subclip(clip_length, chosen_clips, full_duration):
    from random import randint, uniform

    if clip_length > full_duration:
        print("Please insert a clip length that is smaller than the full video's duration")
        return False, False

    if len(chosen_clips) < 1:
        clip_start = round(uniform(0, full_duration - clip_length), 2)
        clip_end = clip_start + clip_length
        return clip_start, clip_end


    chosen_clips.sort()  # Sort chosen clips to find free space easier
    free_space = []  # Sets of values where a clip can be made

    # Check from second 0
    first_chosen_clip = chosen_clips[0]
    if first_chosen_clip[0] != 0:
        free_space.append((0, first_chosen_clip[0]))
    
    # Check all chosen clips for free space (besides the last one, which is handled in last_chosen_clip)
    for i in range(0, len(chosen_clips)-1):
        start_space = chosen_clips[i][1]
        end_space = chosen_clips[i+1][0]
        free_space.append((start_space, end_space))
    
    # Check from last chosen clip to the end
    last_chosen_clip = chosen_clips[len(chosen_clips)-1]
    if last_chosen_clip[1] != full_duration:
        free_space.append((last_chosen_clip[1], full_duration))
    

    # Check if clip_length can be met in free space
    possible_ranges = []
    for space in free_space:
        if space[1] - space[0] >= clip_length:
            possible_ranges.append(space)
    
    if len(possible_ranges) < 1:
        print("No subclip possible with length {0}".format(clip_length))
        return False, False
    

    # If at least one possible range is found, select a random range in between one random range
    start_range, end_range = possible_ranges[randint(0, len(possible_ranges) - 1)]

    clip_start = round(uniform(start_range, end_range - clip_length), 2)
    clip_end = clip_start + clip_length

    return clip_start, clip_end

def exact_subclip(mode, clip_start):
    clip_end = prompt_time(mode.second_clip_length_prompt)
    return clip_start, clip_end

def write_video(clip, filename):
    # The bitrate won't go higher than the source file, but has to be put high to achieve max quality output
    try:
        clip.write_videofile(filename, bitrate="12000k", threads=2, logger=None)
    except ValueError:
        from os import path
        # If current format isn't supported, fallback on mp4 with codec mpeg4, which should returner high quality than libx264
        # https://zulko.github.io/moviepy/ref/VideoClip/VideoClip.html?highlight=videofileclip#moviepy.video.VideoClip.VideoClip.write_videofile
        
        filename_no_ext = filename[:filename.rindex(".")]
        clip.write_videofile(filename_no_ext + ".mp4", bitrate="12000k", threads=2, logger=None, codec="mpeg4")

def main():
    scriptname = path.basename(__file__)
    log(scriptname)

    log("debug", "functions.video_output_path", functions.video_output_path)

    choosing_clips = True
    chosen_clips = []

    threads = []

    print("Do you want to generate random clips, or set a specific start and endtime?")
    mode = prompt_mode()

    print("Insert desired clip {0} in mm:ss or seconds".format("length" if mode == random else "start"))
    print("You can make as many clips as liked, leave clip length empty (just press ENTER) to stop making clips")

    while choosing_clips:
        clip_length_or_start = prompt_time(mode.clip_length_prompt)
        # If no value returned, finish clipping
        # Do note: 0 is also a False value, so double check that the clip_length_or_start isn't 0 when stopping the clipping process
        if clip_length_or_start == False and str(clip_length_or_start) != str(float(0)):
            log("debug", "clip_length_or_start", "\"{0}\", done clipping".format(clip_length_or_start))
            choosing_clips = False
        else:
            from moviepy.editor import VideoFileClip
            full_video = VideoFileClip(functions.video_output_path)
            full_duration = full_video.duration
            log("debug", "full_duration", full_duration)

            if mode == random:
                clip_start, clip_end = random_subclip(clip_length_or_start, chosen_clips, full_duration)
                if clip_start == False or clip_end == False:
                    # If no valid clip could be found, prompt again
                    continue
            elif mode == exact:
                if clip_length_or_start > full_duration:
                    print("The start of the clip has to be smaller than the video's full duration")
                    continue
                
                clip_start, clip_end = exact_subclip(mode, clip_length_or_start)
                
                if clip_end > full_duration:
                    print("The end of the clip has to be smaller than the video's full duration")
                    continue
                
                if clip_end <= clip_start:
                    print("The end of the clip has to be larger than the start of the clip")
                    continue
            
            log("debug", "clip_start", clip_start)
            log("debug", "clip_end", clip_end)

            clip = full_video.subclip(clip_start, clip_end)

            if (clip_end - clip_start) > 10:
                print("The application will now show the first 5 and last 5 seconds of the clip")
                clip.subclip(0, 5).preview()
                clip.subclip(clip.duration - 5, clip.duration).preview()
            else:
                print("Since this is a short clip, it will be viewed in its entirety")
                clip.preview()


            clip_approved = input("Is this clip good? (y or empty if Yes, n if no): ").lower().strip()
            if clip_approved in ["", "y", "ye", "yes", "ys"]:
                clip_filename, clip_ext = path.splitext(path.basename(functions.video_output_path))
                # clip_ext includes '.'

                chosen_clips.append((clip_start, clip_end))

                clip_path = functions.video_output_dir +\
                    "clip {0} ({1}-{2}) {3}{4}".format(len(chosen_clips), clip_start, clip_end, clip_filename, clip_ext)
                
                write_videofile = Thread(target=write_video, args=(clip, clip_path))
                print("Clip selected, writing in the background. Feel free to continue making clips!")
                write_videofile.start()
                threads.append(write_videofile)

    print("Making sure all clips are finished writing")
    
    for i in range(0, len(threads)):
        print("Waiting for thread {0}...".format(i))
        threads[i].join()
        print("Thread {0} done!".format(i))

    # Startfile only works in Windows
    if name == "nt":
        from os import startfile
        log("debug", "os", "Windows, opening output in explorer")
        startfile(path.realpath(functions.video_output_dir))

    log("debug", "status", "done")