# MovieColor

Create a "MovieBarcode" using average color of each frame as bars:

![image of test output](https://github.com/AsaadMe/MovieColor/blob/master/doc/outresult.png)

or using shrinked frames as bars (with `--alt` argument):

![image of test output2](https://github.com/AsaadMe/MovieColor/blob/master/doc/outresult2.jpg)

## Usage:

Install python dependencies in Virtual Environment:
```
python -m venv venv
venv\Scripts\activate (on Windows)
source venv/bin/activate (on Linux)
pip install -r requirements.txt
```
Run it with:
```
python moviecolor.py input.mp4 [-l 30] [-o output_name] [--alt] [--help]
```
>-l , --length: chosen part of the video from start (in Minutes)

>-a , --alt: instead of using average color, use shrinked frames


![Usage](https://github.com/AsaadMe/MovieColor/blob/master/doc/usage.gif)