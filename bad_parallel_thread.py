import sys, os, math
import numpy as np
from plyfile import PlyData, PlyElement

import fusion

print(sys.argv)

grid = [float(x) for x in sys.argv[1][sys.argv[1].find("/") + 1:sys.argv[1].rfind(".")].split("_")]
print(grid)

voxel_size = float(sys.argv[2])

block_length = float(sys.argv[3])

grid_bounds = np.array([[grid[0], grid[0] + block_length], [grid[1], grid[1] + block_length], [grid[2], grid[2] + block_length]])

plydata = PlyData.read(sys.argv[1])
print('getting vertices')
vertices = np.array(plydata.elements[0].data)

print('initializing tsdf with grid_bounds: ', grid_bounds)

mesh_name = "meshes/mesh_constructed_" + str(grid[0]) + "_" + str(grid[1]) + "_" + str(grid[2]) + ".ply"

print(mesh_name)

if os.path.exists(mesh_name):
	print("already done")
	exit()

tsdf_vol = fusion.TSDFVolume(grid_bounds,voxel_size=voxel_size)

tsdf_vol.fill_grid(vertices)

verts, faces, norms, colors = tsdf_vol.get_mesh()

fusion.meshwrite(mesh_name,verts,faces,norms,colors)