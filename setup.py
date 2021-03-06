import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="moviecolor",
    version="1.2.1",
    author="Mehran Asaad",
    author_email = 'mehran.asaad@gmail.com',
    license='MIT',
    url = 'https://github.com/AsaadMe/MovieColor',
    download_url = 'https://github.com/AsaadMe/MovieColor/releases/tag/v1.2.1',
    keywords = ['moviebarcode'],
    description="Generate a 'Moviebarcode' of a video from shrinked frames or average color of frames using ffmpeg with real-time progress interface.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
    install_requires=[
        'ffmpeg-python==0.2.0',
        'future==0.18.2',
        'numpy==1.20.1',
        'Pillow==8.1.0',
    ],
    entry_points={
        "console_scripts":[
            "moviecolor=moviecolor.__main__:main"
        ]
    },
)