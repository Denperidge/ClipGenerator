from os import path, name
from app.functions import log
import app.functions as functions
from threading import Thread

class Mode:
    def __init__(self, name, clip_length_promp, second_clip_length_promp=None):
        self.name = name
        self.clip_length_promp = clip_length_promp
        if second_clip_length_promp is not None:
            self.second_clip_length_promp = second_clip_length_promp


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
    clip_length = input(clip_length_prompt).strip()
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
    from random import uniform
    # Check if there's enough space in the video to get clip from
    subclip_attempts = 0
    allowed_subclip_attempts = 100000  # How many times there can be searched for more subclip space before giving up
    if len(chosen_clips) != 0:
        clip_start_and_end_chosen = False
    else:
        clip_start_and_end_chosen = True
        clip_start = round(uniform(0, full_duration - clip_length), 2)
        clip_end = round(clip_start + clip_length, 2)
    
    in_between_clips = False
    while not clip_start_and_end_chosen:
        if subclip_attempts >= allowed_subclip_attempts:
            log("warning", "exit", "No more subclips possible")
            input("No more subclips possible! Tried {0} times. Press ENTER to exit".format(subclip_attempts))
            return False, False

        clip_start = round(uniform(0, full_duration - clip_length), 2)
        clip_end = clip_start + clip_length
        
        for chosen_clip in chosen_clips:
            if (chosen_clip[0] < clip_start < chosen_clip[1]) or (chosen_clip[0] < clip_end < chosen_clip[1]):
                in_between_clips = True
                continue
        
        if not in_between_clips:
            clip_start_and_end_chosen = True
        subclip_attempts += 1
    
    return clip_start, clip_end

def exact_subclip(mode, clip_start):
    clip_end = prompt_time(mode.second_clip_length_promp)
    return clip_start, clip_end

def write_video(clip, filename):
    # The bitrate won't go higher than the source file, but has to be put high to achieve max quality output
    clip.write_videofile(filename, bitrate="12000k", threads=2, logger=None)

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
        clip_length_or_start = prompt_time(mode.clip_length_promp)
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
                clip_start, clip_end = exact_subclip(mode, clip_length_or_start)
            
            log("debug", "clip_start", clip_start)
            log("debug", "clip_end", clip_end)

            clip = full_video.subclip(clip_start, clip_end)

            if (clip_end - clip_start) >= 5:
                print("The application will now show the first 5 and last 5 seconds of the clip")
                clip.subclip(0, 5).preview()
                clip.subclip(clip.duration - 5, clip.duration).preview()
            else:
                print("Since this is a short clip, it will be viewed in it's entirety")
                clip.preview()


            clip_approved = input("Is this clip good? (y or empty if Yes, n if no): ").lower().strip()
            if clip_approved in ["", "y", "ye", "yes", "ys"]:
                clip_filename = path.splitext(path.basename(functions.video_output_path))[0]

                chosen_clips.append((clip_start, clip_end))

                clip_path = functions.video_output_path.replace(
                    clip_filename, "clip {0} ({1}-{2}) {3}".format(len(chosen_clips), clip_start, clip_end, clip_filename))
                
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