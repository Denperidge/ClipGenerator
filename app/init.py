from os import path, mkdir
import app.functions as functions
from datetime import datetime

functions.current_datetime = datetime.now().strftime("%Y-%m-%d %H-%M-%S")

output_dir = "output/"

if not path.exists(output_dir):
    mkdir(output_dir)

functions.video_output_dir = output_dir + functions.current_datetime + "/"
mkdir(functions.video_output_dir)
    



