# Functions and vars
from pprint import pformat
import io

current_datetime = None
video_output_dir = ""
video_output_path = ""

def log(tag, varname=None, varvalue=None):
    with open(video_output_dir + "logfile.txt", "a+", encoding="utf-8") as log:
        # If no message (thus division)
        if varname == None:
            log.write("[{0}]\n".format(tag))
        # If message (thus log entry)
        else:
            if type(varvalue) is not str:
                # If possible, use vars() combined with pformat
                if hasattr(varvalue, "__dict__"):
                    log("debug", varname, "parsing vars for pformat")
                    varvalue = vars(varvalue)
                varvalue = "\n\t\t\t" + pformat(varvalue).replace("\n", "\n\t\t\t")

            log.write("\t[{0}]\t{1} = {2}\n".format(tag.upper(), varname, varvalue))
        