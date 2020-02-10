#Adam Chang 10.1.19
#Performs marching cubes algorithm on point cloud
import sys, os, math
import numpy as np
from plyfile import PlyData, PlyElement

import fusion
import subprocess
import time
import datetime



precise = True
block_side_length = 3
half_len = block_side_length / 2 * 1.0
voxel_size = 0.03



def merge_meshes():

	print("mering meshes, ", datetime.datetime.now())

	meshes = set()

	for file in os.listdir("meshes"):
		meshes.add("meshes/" + file)

	verts = []
	faces = []
	norms = []
	colors = []

	total_verts = 0

	for mesh in meshes:
		f = open(mesh, 'r')
		f.readline()
		f.readline()
		vertex_line = f.readline()
		face_line = f.readline()
		while ('face' not in face_line):
			face_line = f.readline()
		f.readline()
		f.readline()

		num_vertices = int(vertex_line.split(" ")[2])
		num_faces = int(face_line.split(" ")[2])


		for i in range(num_vertices):
			line = f.readline().split(" ")
			verts.append([float(line[0]), float(line[1]), float(line[2])])
			norms.append([float(line[3]), float(line[4]), float(line[5])])
			colors.append([int(line[6]), int(line[7]), int(line[8])])

		for i in range(num_faces):
			line = f.readline().split(" ")
			faces.append([int(line[1]) + total_verts, int(line[2]) + total_verts, int(line[3]) + total_verts])

		total_verts = len(verts)

	verts = np.array(verts)
	faces = np.array(faces)
	norms = np.array(norms)
	colors = np.array(colors)

	fusion.meshwrite("mesh_combined.ply",verts,faces,norms,colors)

#def simplify_mesh():

def bad_parallel():

	print("beginning mesh construction, parallel, ", datetime.datetime.now())

	blocks = []
	for file in os.listdir("blocks"):
		blocks.append("blocks/" + file)

	if os.path.isdir("meshes"):
		print("meshes already exists")
	else:
		os.mkdir("meshes", mode=0o777)

	counter = 0
	lst = []
	for block in blocks:
	# 	if counter > 12:
	# 		break
	# 	counter += 1

		print(block)

		lst.append(subprocess.Popen(["python", "bad_parallel_thread.py", block, str(voxel_size), str(block_side_length)], creationflags = subprocess.CREATE_NEW_CONSOLE))
		
		while (len(lst) == 10):
			while (all([p.poll() is None for p in lst])):
				time.sleep(2)
			idx = 0
			while idx < len(lst):
				if lst[idx].poll() is not None:
					lst = lst[:idx] + lst[idx + 1:]
				else:
					idx += 1


def generate_mesh_blocks():

	plydata = PlyData.read(sys.argv[1])
	print('getting vertices')
	vertices = np.array(plydata.elements[0].data)


	if precise:

		print('creating output directory')
		if os.path.isdir("meshes"):
			print("meshes already exists")
		else:
			os.mkdir("meshes", mode=0o777)

		if os.path.isdir("blocks"):
			print("blocks already exists")
		else:
			os.mkdir("blocks", mode=0o777)

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

		already_done_blocks = set()

		for file in os.listdir("meshes"):
			already_done_blocks.add("meshes/" + file)

		print(already_done_blocks)

		for key in block_dict.keys():

			verts = block_dict.get(key)

			file_name = "blocks/" + str(key[0]) + "_" + str(key[1]) + "_" + str(key[2]) + ".ply"
			ply_file = open(file_name, "w")
			ply_file.write("ply\n")
			ply_file.write("format ascii 1.0\n")
			ply_file.write("element vertex %d\n"%(len(verts)))
			ply_file.write("property float x\n")
			ply_file.write("property float y\n")
			ply_file.write("property float z\n")
			ply_file.write("property uchar red\n")
			ply_file.write("property uchar green\n")
			ply_file.write("property uchar blue\n")
			ply_file.write("end_header\n")

			for i in range(len(verts)):
			    ply_file.write("%f %f %f %d %d %d\n"%(verts[i][0],verts[i][1],verts[i][2],verts[i][3],verts[i][4],verts[i][5]))

			ply_file.close()

		bad_parallel()

	else:

		print('initializing tsdf for what reason idk')

		print(grid_bounds)

		tsdf_vol = fusion.TSDFVolume(grid_bounds,voxel_size=voxel_size)

		tsdf_vol.fill_grid(vertices)

		verts, faces, norms, colors = tsdf_vol.get_mesh()

		fusion.meshwrite("mesh_constructed.ply",verts,faces,norms,colors)

def main():
	if len(sys.argv) != 2:
		print("usage: python <ply file>")
		exit()

	print("beginning time ", datetime.datetime.now())
	#generate_mesh_blocks()
	bad_parallel()

	merge_meshes()
	#simplify_mesh()

	print("finishing time ", datetime.datetime.now())



main()

