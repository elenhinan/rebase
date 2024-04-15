Simple python script to edit an STL base for miniatures

It can do the following:
- Auto center and rotate STL
- Magnetize
  - adding space for a small magnet
  - adding space for a metal washer for extra weight
  - hollowing out the rest of the underside
- Create a thin topper to be glued onto another base

![Magnetized](img/magnetize.png?raw=true)

![Topper](img/topper.png?raw=true)

The python script will process all STLs in a folder, and output to another folder.
Some STLs might need to be run through netfab or similar to correct errors.
Sizes for magnets, washers etc must for now be changed in the python script.

For now there are quite some STLs the pymadcad library won't read, so it might not work for all bases
