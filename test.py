import os, sys
import numpy as np
from plyfile import PlyData, PlyElement



plydata = PlyData.read(sys.argv[1])
vertices = np.array(plydata.elements[0].data)

counter = 0
for v in vertices:
	counter += 1

	if counter == 1000:
		break

	v[4] *= v[6]
	v[5] *= v[6] * 256
	print(v)
	print(v[0], " ", v[1], " ", v[2])
	print(v[3], " ", v[4], " ", v[5])