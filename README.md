# MovieColor

Create a "MovieBarcode" using average color of each frame as bars:

![image of test output](https://raw.githubusercontent.com/AsaadMe/MovieColor/master/doc/outresult.png)

or using shrinked frames as bars (with `--alt` argument):

![image of test output2](https://raw.githubusercontent.com/AsaadMe/MovieColor/master/doc/outresult2.jpg)

------------------
## Installation:

Install via pip:
```
pip install moviecolor
```
Or clone the project and Install it in Virtual Environment:
```
git clone https://github.com/AsaadMe/MovieColor.git
cd MovieColor
python -m venv venv
venv\Scripts\activate (on Windows)
source venv/bin/activate (on Linux)
pip install -e .
```

\* Make sure you have [ffmpeg](https://www.ffmpeg.org/) installed.

----------------
## Usage:

Run it with:
```
moviecolor input.mp4 [-e 30] [-o output_name] [--alt] [--help]
```
>-e , --end: chosen part of the video from start (in Minutes)

>-a , --alt: instead of using average color, use shrinked frames


![Usage](https://raw.githubusercontent.com/AsaadMe/MovieColor/master/doc/usage.gif)