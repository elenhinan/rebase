#!/usr/bin/env python
# coding: utf-8
#
# Njål Brekke, 2024-04-15

# Settings:

# For 'topping' bases:
top_d = 29.6    # diameter (mm) of top
top_h = 3.0     # how much (mm) to remove from bottom

# for magnetizing
mag_d  = 5.2    # magnet diameter (mm)
mag_h  = 2.8    # magnet height (mm)
shim_d = 18.4   # shim diameter (mm)
shim_h = 1.7    # shim height (mm)
hollow_d = 0    # diameter to hollow out from stock (mm), 0 = auto-detect (leaves 1.5 mm edge)
hollow_h = 2.2  # height to remove from bottom (mm), 0 = disable
theta = 70      # degrees of edges, 90 = square edges
cut_h = 1.0       # cut from bottom to reduce total thickness (mm)

##############
#    code    #
##############

import numpy as np
from madcad import *
from stl import mesh
import os
import argparse

res=['rad',pi/120]

def masscenter(filename):
    base= mesh.Mesh.from_file(filename)
    center = base.get_mass_properties()[1]
    return center

def printbb(base):
    bb = base.box()
    xmin,ymin,zmin = bb.min
    xmax,ymax,zmax = bb.max
    xsize,ysize,zsize = bb.width
    print(f'x: [{xmin}, {xmax}] : {xsize} mm')
    print(f'y: [{ymin}, {ymax}] : {ysize} mm')
    print(f'z: [{zmin}, {zmax}] : {zsize} mm')

def autocenter(base, center): 
    # get bounding box to auto-rotate and translate
    bb = base.box()
    a = np.argmin(bb.width)
    # use center of mass
    zcen = center[a]
    zmin, zmax = bb.min[a], bb.max[a]
    # check which way to rotate (center of mass should be below geometric center)
    flip = -1 if (zcen-zmin > zmax-zcen) else 1
    # do rotation
    base = base.transform(rotate(np.pi/2,vec3(flip*(a==1),flip*(a==0),0)))
    # center around x and y, z min to 0
    bb = base.box()
    base = base.transform(translate(vec3(-bb.width[0]/2-bb.min[0],-bb.width[1]/2-bb.min[1],-bb.min[2])))
    return base

def topper(base,r,h):
    # create high-res circle for intersection
    c=Circle((0,Z),r,resolution=res)
    profile = flatsurface(web(c)).flip()
    tool = extrusion(translate(base.box().width[2]*Z), profile)
    # move base down to remove bottom by 'h' mm
    base = base.transform(translate(vec3(0,0,-h)))
    top_base = intersection(base,tool)
    top_base.finish()

    scene = []
    if args.show:
        scene.append(top_base)
    if args.debug:
        scene.append(tool)
    if len(scene) > 0:
        show(scene)
    
    return top_base

def magnetize(base,r_mag,h_mag,r_wash,h_wash,r_hollow=0,h_hollow=0,theta=90,cut_h=0):
    #  A_______B
    #         |___________D
    #         C          |__________F
    #                    E         |
    #  H___________________________|G
    
    # angle B and D = theta
    bb = base.box()
    r = (bb.width[0]+bb.width[1])/4
    b = -(cut_h+1)*Z
    # calc beveled edges
    c = cos(radians(theta))
    t1 = abs(h_mag-h_wash)*c
    t2 = abs(h_wash-h_hollow)*c
    t3 = abs(h_hollow)*c
    if r_hollow == 0:
        r_hollow = r-1.5
    points = []
    points.append(h_mag*Z)                  # A
    points.append(h_mag*Z+r_mag*X)          # B
    points.append(h_wash*Z+(r_mag+t1)*X)    # C
    points.append(h_wash*Z+r_wash*X)        # D
    points.append((r_wash+t2)*X+h_hollow*Z) # E
    if h_hollow > 0:
        points.append(h_hollow*Z+r_hollow*X) # F
        points.append(0+(r_hollow+t3)*X)     # G
    points.append((r+5)*X)                   # F
    points.append((r+5)*X+b)                 # G
    points.append(b)                         # F
        
    section = Wire(points).segmented()
    tool = revolution(2*pi,(O,Z),section,resolution=res)
    tool.mergeclose()
  
    if cut_h > 0:
        base = base.transform(-cut_h*Z)

    mag_base = difference(base,tool)
    mag_base.finish()

    scene = []
    if args.show:
        scene.append(mag_base)
    if args.debug:
        scene.append(tool)
    if len(scene) > 0:
        show(scene)

    return mag_base

def loadstl(filepath):
    print(f"Loading {filepath}")
    base = read(filepath)
    base.mergeclose()
    center = masscenter(filepath)
    base = autocenter(base, center)
    printbb(base)
    return base

def savestl(base, filepath, modifier=None,folder='.'):
    if not os.path.isdir(folder):
        os.mkdir(folder)
    filename = os.path.basename(filepath)
    if modifier:
        name, ext = os.path.splitext(filename)
        filename = f'{name}_{modifier}{ext}'
    new_path = os.path.join(folder,filename)
    print(f"Saving to {modifier} as {new_path}")
    write(base,new_path)

def process(filename,folder):
    base = loadstl(filename)
    if args.cen:
        savestl(base,filename,'centered',folder)
    if args.top:
        topped = topper(base,top_d/2,top_h)
        savestl(topped,filename,'topper',folder)
    if args.mag:
        magnetized = magnetize(base,mag_d/2,mag_h,shim_d/2,shim_h,hollow_d,hollow_h,theta,cut_h)
        savestl(magnetized,filename,'magnetized',folder)

parser = argparse.ArgumentParser(
    prog="Minature Base topper/magnetizer",
    description="Modifies base for topping and/or magnetizing"
)
parser.add_argument('input_folder', help="Folder of input STLs")
parser.add_argument('output_folder', help="Folder to place processed STLs")
parser.add_argument('-m','--magnetize', dest='mag', action='store_true', help='Convert to magnetized base')
parser.add_argument('-t','--topper', dest='top', action='store_true', help='Convert to base topper')
parser.add_argument('-c','--center', dest='cen', action='store_true', help='Save base leid flat and centered')
parser.add_argument('-s','--show', dest='show', action='store_true', help='Show model')
parser.add_argument('-d','--debug', dest='debug', action='store_true', help='Show tool')

args = parser.parse_args()
if not (args.mag or args.top or args.cen):
    parser.error('Needs minimum one of -m,-t or -c as an argument')

if os.path.isdir(args.input_folder):
    for filename in os.listdir(args.input_folder):
        if filename.endswith('.stl'):
            filepath = os.path.join(args.input_folder,filename)
            process(filepath, args.output_folder)
else:
    print(f'"{args.input_folder}" is not a valid folder')

