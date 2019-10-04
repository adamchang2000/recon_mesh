#Adam Chang 10.1.19
#Performs marching cubes algorithm on point cloud
import sys, os, math
import numpy as np
from plyfile import PlyData, PlyElement

if len(sys.argv) != 2:
	print("usage: python <ply file>")
	exit()

import fusion

plydata = PlyData.read(sys.argv[1])
print('getting vertices')
vertices = np.array(plydata.elements[0].data)


precise = True

block_side_length = 4
half_len = block_side_length / 2 * 1.0
voxel_size = 0.02

if precise:

	print('creating output directory')
	if os.path.isdir("meshes"):
		print("meshes already exists")
	else:
		os.mkdir("meshes", mode=0o777)

	print('generating blocks')

	block_dict = dict()

	for v in vertices:

		x = int(math.floor((v[0] - half_len) / block_side_length)) * block_side_length + half_len
		y = int(math.floor((v[1] - half_len) / block_side_length)) * block_side_length + half_len
		z = int(math.floor((v[2] - half_len) / block_side_length)) * block_side_length + half_len

		pos = (x, y, z)

		if pos in block_dict:
			block_dict.get(pos).append(v)
		else:
			block_dict.update({pos: [v]})

else:
	grid_bounds = np.array([[-2, 2], [-2, 2], [-2, 2]])

if precise:
	for key in block_dict.keys():
		grid_bounds = np.array([[key[0], key[0] + block_side_length], [key[1], key[1] + block_side_length], [key[2], key[2] + block_side_length]])
		print('initializing tsdf with grid_bounds: ', grid_bounds)

		tsdf_vol = fusion.TSDFVolume(grid_bounds,voxel_size=voxel_size)

		tsdf_vol.fill_grid(block_dict.get(key))

		verts, faces, norms, colors = tsdf_vol.get_mesh()

		mesh_name = "meshes/mesh_constructed_" + str(key[0]) + "_" + str(key[1]) + "_" + str(key[2]) + ".ply"

		fusion.meshwrite(mesh_name,verts,faces,norms,colors)

else:

	print('initializing tsdf for what reason idk')

	print(grid_bounds)

	tsdf_vol = fusion.TSDFVolume(grid_bounds,voxel_size=voxel_size)

	tsdf_vol.fill_grid(vertices)

	verts, faces, norms, colors = tsdf_vol.get_mesh()

	fusion.meshwrite("mesh_constructed.ply",verts,faces,norms,colors)

