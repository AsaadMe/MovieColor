import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="MovieColor",
    version="1.0.1",
    author="Mehran Asaad",
    author_email = 'mehran.asaad@gmail.com',
    license='MIT',
    url = 'https://github.com/AsaadMe/MovieColor',
    download_url = 'https://github.com/AsaadMe/MovieColor/releases/tag/v1.0.1',
    keywords = ['moviebarcode'],
    description="Fast program to generate a 'Moviebarcode' of a video from average color of its frames with embedded ffmpeg and real-time progress interface.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=['Moviecolor'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.9',
    install_requires=[
        'ffmpeg-python==0.2.0',
        'future==0.18.2',
        'numpy==1.20.1',
        'Pillow==8.1.0',
    ],
    entry_points={
        "console_scripts":[
            "moviecolor=MovieColor.__main__:main"
        ]
    },
)