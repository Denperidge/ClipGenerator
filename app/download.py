from os import path, rename
from glob import glob
from youtube_dl import YoutubeDL, DownloadError
from app.functions import log
import app.functions as functions
from re import sub

# Log setup
class ydlLogger(object):
    def debug(self, msg):
        log("debug", "ydlLogger", msg)
    def warning(self, msg):
        log("warning", "ydlLogger", msg)
    def error(self, msg):
        log("error", "ydlLogger", msg)
def ydl_hook(d):
    status = d["status"]
    if status == "error":
        log("error", "ydl_hook_error", str(d))
    elif status == "downloading":
        log("debug", "ydl_hook_downloading", "Downloading...")
        log("debug", "ydl_hook_downloading", str(d))
    elif status == "finished":
        log("debug", "ydl_hook_finished", "Finished downloading, now converting...")
        log("debug", "ydl_hook_finished", str(d))


def main():  
    scriptname = path.basename(__file__)
    log(scriptname)

    youtube_link = None
    while youtube_link == None:
        value = input("Link to YT video: ")
        if "youtube.com/watch?v=" in value or "youtu.be/" in value:
            youtube_link = value
        else:
            print("{0} is not a valid youtube url".format(value))

    log("debug", "youtube_link", youtube_link)

    ydl_opts = {
        "logger": ydlLogger(),
        "progress_hooks": [ydl_hook],
        "format": "bestvideo+bestaudio",
        "outtmpl": functions.video_output_dir + "%(title)s.%(ext)s",
    }
    log("debug", "ydl_opts", ydl_opts)

    print("Downloading...")
    with YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(youtube_link)

            # After download, FFMPEG converts the file depending on the format from ydl_opts
            # However, this is not consistently to the same format, nor does it appear in prepare_filename
            # Hence: discover the extension

            # output vars are gotten from ydl
            output_path = ydl.prepare_filename(info)  # output/*-*-*--*-*-*/{videofilename}.{ext}
            output_dirname = path.dirname(output_path)  # output/*-*-*--*-*-*/

            output_videoname = path.splitext(path.basename(output_path))[0]  # {videofilename} (no ext)
            output_filename = path.basename(
                glob(path.join(output_dirname, output_videoname + "*"))[0])  # {videofilename}.{ext}
            

            output_videoname = sub("[^a-zA-Z0-9 \"'-]", "", output_videoname).replace("  ", " ")  # Clean filename for use in folder name

            # Create new dirname for video file
            new_video_output_dir = functions.video_output_dir.replace(
                functions.current_datetime,
                "{0} {1}".format(output_videoname, functions.current_datetime))
            # Apply new dirname to global vars
            functions.video_output_dir = new_video_output_dir
            functions.video_output_path = new_video_output_dir + output_filename

            rename(output_dirname, functions.video_output_dir)
            log("debug", "output_path", output_path)
            log("debug", "video_output_dir", functions.video_output_dir)
            log("debug", "video_output_path", functions.video_output_path)

        except DownloadError as e:
            log("error", "DownloadError", e)
