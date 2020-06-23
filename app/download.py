from os import path, rename, name, system
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

    print("(Although the prompt asks for a YT link, a path to a local video file can also be used)")
    youtube_link = None
    while youtube_link == None:
        value = input("Link to YT video/path to video file: ")
        # Valid Youtube link
        if "youtube.com/watch?v=" in value or "youtu.be/" in value:
            log("debug", "Mode", "Downloading file from Youtube")
            youtube_link = value

        # Valid local file
        elif path.isfile(value):
            filename = value
            filedir = path.join(path.dirname(filename), 
                "Clips {0} {1}\\".format(
                    path.splitext(path.basename(filename))[0], functions.current_datetime))

            # Move logfile & cleanup
            rename(functions.video_output_dir, filedir)

            functions.video_output_dir = filedir
            functions.video_output_path = filename
            
            log("debug", "Mode", "Using local file")
            log("debug", "video_output_dir", functions.video_output_dir)
            log("debug", "video_output_path", functions.video_output_path)

            # Set title in Windows console
            if name == "nt":
                system("title {0}".format(path.basename(filename)))

            return

        else:
            print("{0} is not a valid youtube url (nor a file on your HDD)".format(value))

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

            # Set title in Windows console
            if name == "nt":
                system("title {0}".format(output_videoname))


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

            # Write source.txt with original youtube link, title and uploader. Give credit where it's due!
            with open(new_video_output_dir + "/../sources.txt", "a+", encoding="utf-8") as sources:
                line = ""
                seperator = " - "
                for data in [info["title"], info["uploader"], youtube_link]:
                    line += data + " - "
                line = line.strip(seperator)
                sources.write(line + "\n")

        except DownloadError as e:
            log("error", "DownloadError", e)
