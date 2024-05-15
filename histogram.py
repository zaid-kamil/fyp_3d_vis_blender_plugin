import bpy
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Sample DataFrame
data = {
    'x': np.random.normal(size=100),
    'y': np.random.normal(size=100)
}
df = pd.DataFrame(data)

# Create histogram data
hist, xedges, yedges = np.histogram2d(df['x'], df['y'], bins=20)

# Set up figure and axis
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

# Construct arrays for the anchor positions of the bars.
xpos, ypos = np.meshgrid(xedges[:-1] + 0.1, yedges[:-1] + 0.1, indexing="ij")
xpos = xpos.ravel()
ypos = ypos.ravel()
zpos = 0

# Construct arrays with the dimensions for the bars.
dx = dy = 0.2 * np.ones_like(zpos)
dz = hist.ravel()

# Create 3D histogram
ax.bar3d(xpos, ypos, zpos, dx, dy, dz, zsort='average')

# Save histogram as an image
plt.savefig('/tmp/histogram.png')

# Clear previous meshes and objects
bpy.ops.wm.read_factory_settings(use_empty=True)

# Create material
material = bpy.data.materials.new(name="HistogramMaterial")
material.use_nodes = True
bsdf = material.node_tree.nodes["Principled BSDF"]
tex_image = material.node_tree.nodes.new('ShaderNodeTexImage')
tex_image.image = bpy.data.images.load('/tmp/histogram.png')
material.node_tree.links.new(bsdf.inputs['Base Color'], tex_image.outputs['Color'])

# Create plane
bpy.ops.mesh.primitive_plane_add(size=2, enter_editmode=False, align='WORLD', location=(0, 0, 0))
plane = bpy.context.active_object
plane.data.materials.append(material)

# Set up the camera
bpy.ops.object.camera_add(location=(0, -3, 3))
camera = bpy.context.active_object
camera.rotation_euler = (np.radians(60), 0, np.radians(90))

# Set up the light
bpy.ops.object.light_add(type='SUN', align='WORLD', location=(0, -3, 3))
light = bpy.context.active_object

# Set the camera as the active camera
bpy.context.scene.camera = camera

# Render the scene
bpy.context.scene.render.filepath = '/tmp/histogram_render.png'
bpy.ops.render.render(write_still=True)

print("Histogram render saved to /tmp/histogram_render.png")