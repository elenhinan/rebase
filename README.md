## Intro
This is a simple python script for batch editing bases for miniatures.

## Features
- Auto center and rotate STL
- Magnetize
  - adding space for a small magnet
  - adding space for a metal washer for extra weight
  - hollowing out the rest of the underside
- Create a thin topper to be glued onto another base

## Examples
### Magnetized base
![Magnetized](img/magnetize.png?raw=true)

### Topper
![Topper](img/topper.png?raw=true)

## Installation
- Install Python ver 3.11 or newer
- Install [Microsoft Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/)
- do `pip install -r requirements.txt`

## Usage
The python script will process all STLs in a folder, and output to another folder.
Sizes for magnets, washers etc must for now be changed in the python script.

Run `python rebase.py -t -m <input_folder> <output_folder>`
- `-t` creates a topper
- `-m` creates magnetized base
- `-s` shows each object after processing
- `-d` shows the tool used to create the final file using boolean operators (for debuging parameters)

## Issues
For now there are quite some STLs the pymadcad library won't read, so it might not work for all bases. Some STLs output from the script might need to be run through netfab or similar to correct errors.
