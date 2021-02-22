# MovieColor

Get an average color of video frames each in a bar like this example:

![image of test output](./result.png)

## Usage:

Install python dependencies in virtual envirement (in Windows):
```
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```
Run it with:
```
python videocolor.py input.mp4 [-l 30] [-o output] [--help]
```
>-l , --length: length of video from start (in Minutes)
