# ClipGenerator
A Python script to grab specific or random segments from youtube videos. Simply enter the link, the desired start and end (or random clip length) in mm:ss or ss, repeat for every clip you want to make, and done!

## Why use this tool?

- After selecting a clip, the application previews the first and last 5 seconds so you're sure you've got the clip you want.
- Quickly create multiple clips from a simple CLI.
- Creates video files in the background, so you can keep selecting clips whilst the other ones are being written.
- (When creating random clips) doesn't accidentally re-use the same footage multiple times.

## Usage example

![Gif of example input](/screenshots/demo.gif)

Will result in:

![Screenshot of example output](/screenshots/output.png)

## Installation

- Make sure FFMPEG is installed and added to path.
- Use `pip3 install -r requirements.txt` to ensure that all required python packages are installed.
- Done!

## License

This software is licensed under [MIT](/LICENSE.md), just don't do anything illegal.