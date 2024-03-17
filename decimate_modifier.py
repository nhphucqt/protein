import bpy
import time
import os

from config import *

def cleanScene():
	for obj in bpy.data.objects:
		bpy.data.objects.remove(obj)
	for mesh in bpy.data.meshes:
		bpy.data.meshes.remove(mesh)

	print("Scene Cleaned!")
	print("Number of Objects:", len(bpy.data.objects))
	print("Number of Meshes:", len(bpy.data.meshes))

startTime = time.time()

def log(msg):
	s = round(time.time() - startTime, 2)
	print("{}s {}".format(s, msg))
  
def decimate(obj, ratio):
	print("Object:", obj)
	print("Decimate Ratio:", ratio)
	decimate_modifier = obj.modifiers.new(type="DECIMATE", name="Decimate")
	decimate_modifier.decimate_type = 'COLLAPSE'
	decimate_modifier.ratio = 0.1
	bpy.ops.object.modifier_apply(modifier=decimate_modifier.name)



def decimate_all(ptype, ratio, start_id = 0):
	for i in range(start_id, ptype["num"]):
		print("Mesh", i, "...")

		cleanScene()
		bpy.ops.wm.ply_import(filepath=os.path.join(PATH_PREFIX, ptype["type"], f"{i}.ply"))
		bpy.ops.object.make_single_user(object=True, obdata=True)
		obj = bpy.data.objects[0]

		print("Before Decimation:")
		print("Number of Vertices:", len(obj.data.vertices))
		print("Number of Faces:", len(obj.data.polygons))
		print()

		decimate(obj, ratio)

		print()
		print("After Decimation:")
		print("Number of Vertices:", len(obj.data.vertices))
		print("Number of Faces:", len(obj.data.polygons))

		bpy.ops.wm.ply_export(filepath=os.path.join(PATH_PREFIX, ptype["decimate"], f"{i}.ply"))

def main():
	ratio = 0.1
	ptype = MESH_CONF["query"]
	decimate_all(ptype, ratio, 349)
	ptype = MESH_CONF["target"]
	decimate_all(ptype, ratio)

if __name__ == "__main__":
	main()
	print("Done!")