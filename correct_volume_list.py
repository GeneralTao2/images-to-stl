import numpy as np
import cv2
import pyvista as pv
import vtk
import shapely as sh
from shapely.geometry import Polygon
import matplotlib.pyplot as plt
import create_sphere_sector as cs
import threading
from StoppableThread import *
import time

import json
from VolumeIndexClass import *

data = None

def angle_betwee_vectors(vector_1, vector_2):
    unit_vector_1 = vector_1 / np.linalg.norm(vector_1)
    unit_vector_2 = vector_2 / np.linalg.norm(vector_2)
    dot_product = np.dot(unit_vector_1, unit_vector_2)
    return np.arccos(dot_product)

with open("C:\\Users\\gener\\OneDrive\\Documents\\Python\\images-to-stl\\jsons\\vi.json") as json_file:
    data = json.load(json_file)

volume_index_array = [VolumeIndex(**(dict)) for dict in data]

pa0st0se2=pv.read("C:\\Users\\gener\\OneDrive\\Documents\\Python\\images-to-stl\\models\\pa0st0se2_o3d.ply")
center_pos = (256, 256, 0)

sector = cs.SphereSector(0.80, 90, 10) #todo

pa0st0se2 = pa0st0se2.compute_normals()
pa0st0se2_tr = pa0st0se2.triangulate()

front_vertices_indexed = []
for i in range(0, pa0st0se2.n_points):
    vector_1 = pa0st0se2.points[i] - center_pos
    vector_2 = pa0st0se2.active_normals[i]
    angle = angle_betwee_vectors(vector_1, vector_2)
    if(angle < 0.47):
        front_vertices_indexed.append(i)


for j in range(len(front_vertices_indexed)):
    if volume_index_array[j].volume > 10:
        continue
    idx = front_vertices_indexed[j]
    sector.move_to_and_rotate_foward(pa0st0se2.points[idx], pa0st0se2.active_normals[idx])
    result = sector.sector.boolean_intersection(pa0st0se2_tr)
    volume = result.volume
    print(volume)
    volume_index_array[j].volume = volume
 
  
json_string = [ob.__dict__ for ob in volume_index_array]

with open("C:\\Users\\gener\\OneDrive\\Documents\\Python\\images-to-stl\\jsons\\vi_corrected.json", 'w') as outfile:
    json.dump(json_string, outfile)



