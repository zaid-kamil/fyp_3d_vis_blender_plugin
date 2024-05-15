import bpy
import math
import pandas as pds

context = bpy.context
scene = context.scene

###########################################################################
###########################################################################
#
# CHANGE THE FOLLOWING INPUT AS PER YOUR EXCEL FILE
# BE CAREFUL - ANY WRONG INPUT WILL RAISE AN ERROR.


excel_file_path = r"E:\project_24\fyp_3d_vis_blender_plugin\sample.xlsx"
data_column = 5
month_column = 2
currency_symbol = "$"

###########################################################################
###########################################################################

anim_start_frame = 2
anim_length_data = 20
graph_start_position = 1
distance_bet_points = 2

MAJOR_VERSION, MINOR_VERSION, SUB_VERSION = bpy.app.version

# Save the current location of the 3D cursor
saved_cursor_loc = scene.cursor.location.xyz

# Read excel file and store the data in an array
xls_data = pds.read_excel(excel_file_path)
data_list = xls_data.iloc[:,data_column-1]
month_list = xls_data.iloc[:,month_column-1]
number_of_data = len(month_list)
data_height_mean = sum(data_list) / number_of_data

# Initialize the variables.
position_count = graph_start_position
anim_length_text = anim_length_data / 2
anim_curr_frame = anim_start_frame
anim_end_frame = anim_start_frame + anim_length_data * (number_of_data-1)

normalized_data = []
for data in data_list:
    normalized_data.append(data * 10/data_height_mean)

data_height_mean = sum(normalized_data) / number_of_data
data_height_min = min(normalized_data)

display_data = []
if (data_height_min > abs(data_height_mean - data_height_min)):
    for data in normalized_data:
        display_data.append(data - data_height_min + abs(data_height_mean - data_height_min))
else:
    for data in normalized_data:
        display_data.append(data)

# Create a new material for the curve
material_1 = bpy.data.materials.new(name = "anim_material_1")
material_1.use_nodes = True
if material_1.node_tree:
    material_1.node_tree.links.clear()
    material_1.node_tree.nodes.clear()
nodes = material_1.node_tree.nodes
links = material_1.node_tree.links
output = nodes.new(type='ShaderNodeOutputMaterial')
shader = nodes.new(type='ShaderNodeEmission')
nodes["Emission"].inputs['Color'].default_value = (1.0, 0.3, 1.0, 1)
nodes["Emission"].inputs['Strength'].default_value = 1.5
links.new(shader.outputs[0], output.inputs[0])

# Create a new material for the text
material_2 = bpy.data.materials.new(name = "anim_material_2")
material_2.use_nodes = True
if material_2.node_tree:
    material_2.node_tree.links.clear()
    material_2.node_tree.nodes.clear()
nodes = material_2.node_tree.nodes
links = material_2.node_tree.links
output = nodes.new(type='ShaderNodeOutputMaterial')
shader = nodes.new(type='ShaderNodeEmission')
nodes["Emission"].inputs['Strength'].default_value = 3.0
links.new(shader.outputs[0], output.inputs[0])

# Create a new material for the x-axis
material_3 = bpy.data.materials.new(name = "anim_material_3")
material_3.use_nodes = True
if material_3.node_tree:
    material_3.node_tree.links.clear()
    material_3.node_tree.nodes.clear()
nodes = material_3.node_tree.nodes
links = material_3.node_tree.links
output = nodes.new(type='ShaderNodeOutputMaterial')
shader = nodes.new(type='ShaderNodeBsdfPrincipled')
nodes["Principled BSDF"].inputs[0].default_value = (1.0, 0.05, 0.135, 1)
links.new(shader.outputs[0], output.inputs[0])

# Create a new material for the z-axis
material_4 = bpy.data.materials.new(name = "anim_material_4")
material_4.use_nodes = True
if material_4.node_tree:
    material_4.node_tree.links.clear()
    material_4.node_tree.nodes.clear()
nodes = material_4.node_tree.nodes
links = material_4.node_tree.links
output = nodes.new(type='ShaderNodeOutputMaterial')
shader = nodes.new(type='ShaderNodeBsdfPrincipled')
nodes["Principled BSDF"].inputs[0].default_value = (0.0, 0.24, 0.6, 1)
links.new(shader.outputs[0], output.inputs[0])

# Create a curve and add it to the scene
curve = bpy.data.curves.new(name = "data_curve", type = 'CURVE')
curve.dimensions = '3D'
curve_path = bpy.data.objects.new("my_curve", curve)

bezier_curve = curve.splines.new('BEZIER')
bezier_curve.bezier_points.add(number_of_data-1)

for bezier, data in zip(bezier_curve.bezier_points, display_data):
    bezier.co = (position_count, 0, data)
    position_count = position_count + distance_bet_points

context.scene.collection.objects.link(curve_path)
curve_path.select_set(True)
context.view_layer.objects.active = curve_path
bpy.ops.object.editmode_toggle()
bpy.ops.curve.select_all(action='SELECT')
bpy.ops.curve.handle_type_set(type='AUTOMATIC')
bpy.ops.object.editmode_toggle()

# Assign the yellow material created above
curve_path.data.materials.append(material_1)

# Add a sphere and set its dimensions
bpy.ops.mesh.primitive_uv_sphere_add(radius = 0.15)
sphere = context.active_object
sphere.location = [0,0,0]

# Assign the yellow material created above
sphere.data.materials.append(material_1)

follow_path = sphere.constraints.new(type='FOLLOW_PATH')
follow_path.target = curve_path
follow_path.forward_axis = 'TRACK_NEGATIVE_Z'
follow_path.up_axis = 'UP_Y'
follow_path.use_fixed_location = True
follow_path.offset_factor = 0.0
follow_path.keyframe_insert("offset_factor", frame=anim_start_frame)
follow_path.offset_factor = 1.0
follow_path.keyframe_insert("offset_factor", frame=anim_end_frame)

fcurves = sphere.animation_data.action.fcurves
for fcurve in fcurves:
    for kf in fcurve.keyframe_points:
        kf.interpolation = 'LINEAR'
        kf.easing = 'AUTO'
bpy.ops.constraint.followpath_path_animate(constraint=follow_path.name)

def geometry_nodes_node_group(start_frame, end_frame, material):

    geometry_nodes = bpy.data.node_groups.new(type = "GeometryNodeTree", name = "Geometry Nodes")

    if (MAJOR_VERSION >= 4):
        geometry_nodes.interface.new_socket('NodeInterfaceInput', in_out='INPUT', socket_type='NodeSocketGeometry')
    else:
        geometry_nodes.inputs.new("NodeSocketGeometry", "Geometry")

    group_input = geometry_nodes.nodes.new("NodeGroupInput")
    group_input.location = (-340.0, 0.0)
    group_input.width, group_input.height = 140.0, 100.0

    if (MAJOR_VERSION >= 4):
        geometry_nodes.interface.new_socket('NodeInterfaceOutput', in_out='OUTPUT', socket_type='NodeSocketGeometry')
    else:
        geometry_nodes.outputs.new("NodeSocketGeometry", "Geometry")

    group_output = geometry_nodes.nodes.new("NodeGroupOutput")
    group_output.location = (609.8951416015625, 0.0)
    group_output.width, group_output.height = 140.0, 100.0

    trim_curve = geometry_nodes.nodes.new("GeometryNodeTrimCurve")
    trim_curve.location = (-63.592041015625, 22.438913345336914)
    trim_curve.width, trim_curve.height = 140.0, 100.0
    trim_curve.mode = 'FACTOR'
    trim_curve.inputs[1].default_value = True
    trim_curve.inputs[2].default_value = 0.0
    trim_curve.inputs[3].default_value = 0.0
    trim_curve.inputs[3].keyframe_insert('default_value', frame=start_frame)
    trim_curve.inputs[3].default_value = 1.0
    trim_curve.inputs[3].keyframe_insert('default_value', frame=end_frame)

    curve_to_mesh = geometry_nodes.nodes.new("GeometryNodeCurveToMesh")
    curve_to_mesh.location = (169.89512634277344, 18.004777908325195)
    curve_to_mesh.width, curve_to_mesh.height = 140.0, 100.0
    curve_to_mesh.inputs[2].default_value = False

    curve_circle = geometry_nodes.nodes.new("GeometryNodeCurvePrimitiveCircle")
    curve_circle.location = (-340.7394104003906, -86.51416015625)
    curve_circle.width, curve_circle.height = 140.0, 100.0
    curve_circle.mode = 'RADIUS'
    curve_circle.inputs[0].default_value = 32
    curve_circle.inputs[1].default_value = (-1.0, 0.0, 0.0)
    curve_circle.inputs[2].default_value = (0.0, 1.0, 0.0)
    curve_circle.inputs[3].default_value = (1.0, 0.0, 0.0)
    curve_circle.inputs[4].default_value = 0.03

    set_material = geometry_nodes.nodes.new("GeometryNodeSetMaterial")
    set_material.location = (389.71429443359375, 25.688528060913086)
    set_material.width, set_material.height = 140.0, 100.0
    set_material.inputs[1].default_value = True
    set_material.inputs[2].default_value = material

    geometry_nodes.links.new(set_material.outputs[0], group_output.inputs[0])
    geometry_nodes.links.new(group_input.outputs[0], trim_curve.inputs[0])
    geometry_nodes.links.new(trim_curve.outputs[0], curve_to_mesh.inputs[0])
    geometry_nodes.links.new(curve_circle.outputs[0], curve_to_mesh.inputs[1])
    geometry_nodes.links.new(curve_to_mesh.outputs[0], set_material.inputs[0])
    
    fcurves = geometry_nodes.animation_data.action.fcurves
    for fcurve in fcurves:
        for kf in fcurve.keyframe_points:
            kf.interpolation = 'LINEAR'
            kf.easing = 'AUTO'

    return geometry_nodes

geometry_nodes = geometry_nodes_node_group(anim_start_frame, anim_end_frame, material_1)
modifier = curve_path.modifiers.new("Geometry Nodes Temp", "NODES")
modifier.node_group = geometry_nodes

# Create the text fields in a loop
data_counter = 0
anim_curr_frame = anim_start_frame

while (data_counter < number_of_data):
    
    text_month = str(month_list[data_counter])
    text_data = currency_symbol + str(data_list[data_counter])
    
    # Add a sphere, set its location and animate its size
    bpy.ops.mesh.primitive_uv_sphere_add(radius = 0.15)
    sph = context.active_object
    sph.location = [graph_start_position+distance_bet_points*data_counter, 0, display_data[data_counter]]
    sph.scale = [0,0,0]
    sph.keyframe_insert(data_path="scale", frame = anim_curr_frame+4)
    sph.scale = [1,1,1]
    sph.keyframe_insert(data_path="scale", frame = anim_curr_frame+6)
    
    # Assign the yellow material created above
    sph.data.materials.append(material_1)
    
    # Add the 1st caption
    bpy.ops.object.text_add()
    ob = bpy.context.object
    ob.data.body = text_month
    ob.data.align_x = "CENTER"
    ob.data.align_y = "CENTER"
    ob.data.extrude = 0.01

    ob.location = [graph_start_position+distance_bet_points*data_counter, 0, display_data[data_counter]+1.5]
    ob.rotation_euler = [math.radians(90),0,0]
    
    # Animate the caption horizontally
    ob.scale = [0,0,0]
    ob.keyframe_insert(data_path="scale", frame = anim_curr_frame-1)
    ob.scale = [0,0.5,0.5]
    ob.keyframe_insert(data_path="scale", frame = anim_curr_frame)
    anim_curr_frame += anim_length_text
    ob.scale = [0.5,0.5,0.5]
    ob.keyframe_insert(data_path="scale", frame = anim_curr_frame)
    
    # Assign the white material created above
    ob.data.materials.append(material_2)
    
    anim_curr_frame -= anim_length_text

    # Add the 2nd caption
    bpy.ops.object.text_add()
    ob = bpy.context.object
    ob.data.body = text_data
    ob.data.align_x = "CENTER"
    ob.data.align_y = "CENTER"
    ob.data.extrude = 0.01

    ob.location = [graph_start_position+distance_bet_points*data_counter, 0, display_data[data_counter]+1]
    ob.rotation_euler = [math.radians(90),0,0]

    # Animate the caption horizontally
    ob.scale = [0,0,0]
    ob.keyframe_insert(data_path="scale", frame = anim_curr_frame-1)
    ob.scale = [0,0.5,0.5]
    ob.keyframe_insert(data_path="scale", frame = anim_curr_frame)
    anim_curr_frame += anim_length_text
    ob.scale = [0.5,0.5,0.5]
    ob.keyframe_insert(data_path="scale", frame = anim_curr_frame)
    
    # Assign the white material created above
    ob.data.materials.append(material_2)
    
    #increase the loop counters
    data_counter += 1
    anim_curr_frame -= anim_length_text
    anim_curr_frame += anim_length_data
    
# Add x-axis and set its dimensions
bpy.ops.mesh.primitive_cube_add()
ob = context.active_object
axis_length = graph_start_position + distance_bet_points * (number_of_data - 1) + 2
ob.dimensions = [axis_length,0.05,0.05]
ob.location = [axis_length/2,0,0]

# Assign the red material created above
ob.data.materials.append(material_3)

bpy.ops.mesh.primitive_cylinder_add(vertices = 3, radius = 0.3, depth = 0.1)
cyl1 = context.active_object
cyl1.location = [axis_length, 0, 0]
cyl1.scale = [1,1.7,1]
cyl1.rotation_euler = [0,math.radians(90),-math.radians(90)]
    
# Assign the red material created above
cyl1.data.materials.append(material_3)

# Add z-axis and set its dimensions
bpy.ops.mesh.primitive_cube_add()
ob = context.active_object
axis_height = max(display_data) + 3
ob.dimensions = [0.05,0.05,axis_height]
ob.location = [0,0,axis_height/2]

# Assign the blue material created above
ob.data.materials.append(material_4)

bpy.ops.mesh.primitive_cylinder_add(vertices = 3, radius = 0.3, depth = 0.1)
cyl2 = context.active_object
cyl2.location = [0, 0, axis_height]
cyl2.scale = [1,1.7,1]
cyl2.rotation_euler = [math.radians(90),0,0]
    
# Assign the blue material created above
cyl2.data.materials.append(material_4)

# Clean-up work
# Reset 3D cursor location back to the original
scene.cursor.location.xyz = saved_cursor_loc
context.active_object.select_set(False)

# Set the current frame to frame# 1
scene.frame_set(1)

# Set the scene length
scene.frame_start = 1
scene.frame_end = anim_end_frame + 50

# Turn on bloom effect
scene.render.engine = 'BLENDER_EEVEE'
scene.eevee.use_bloom = True