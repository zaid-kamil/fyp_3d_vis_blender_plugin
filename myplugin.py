# blender plugin

import bpy
import pandas as pd
import os
import math
import random

# global variables
context = bpy.context
scene = context.scene

# initial properties
def init_properties():
    bpy.types.Scene.my_file_path = bpy.props.StringProperty(name="File Path", default="")
    bpy.types.Scene.x_axis_column = bpy.props.IntProperty(name="X Axis", default=0)
    bpy.types.Scene.y_axis_column = bpy.props.IntProperty(name="Y Axis", default=0)

bl_info = {
    "name": "3D Visualization",
    "category": "Object",
}

### bpy.types
### Operator, PropertyGroup, Panel, UIList, Menu, Header, Footer, KeyingSetInfo, Node, NodeSocket, NodeLink, UILayout

### bpy.props
### BoolProperty, BoolVectorProperty, CollectionProperty, EnumProperty, FloatProperty, FloatVectorProperty, IntProperty, IntVectorProperty, PointerProperty, StringProperty




class OpenFilebrowser(bpy.types.Operator):
    ## Open a file browser and store the selected file path in a scene property
    bl_idname = "test.open_filebrowser"
    bl_label = "Select a dataset for your 3d graph"
    
    filepath: bpy.props.StringProperty(subtype="FILE_PATH")

    def execute(self, context):
        print("Selected file:", self.filepath)
        context.scene.my_file_path = self.filepath  # Store the filepath in the scene property
        return {'FINISHED'}
    
    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

class DatasetHelper:

    def __init__(self, filepath):
        self.filepath = filepath
        if self.filepath.endswith('.csv'):
            self.df = pd.read_csv(self.filepath, nrows=1000)
        elif self.filepath.endswith('.xlsx'):
            self.df = pd.read_excel(self.filepath, nrows=1000)
        else:
            self.df = pd.DataFrame({
                'A': [1, 2, 3],
                'B': [4, 5, 6],
                'C': [7, 8, 9]
            })

    def get_all_columns(self):
        return self.df.columns
    
    def create_line_graph(self, data_column, month_column, currency_symbol, anim_start_frame=2, anim_length_data=20, graph_start_position=1, distance_bet_points=2):
        context = bpy.context
        scene = context.scene

        # Save the current location of the 3D cursor
        saved_cursor_loc = scene.cursor.location.xyz

        data_list = self.df.iloc[:, data_column - 1]
        month_list = self.df.iloc[:, month_column - 1]
        number_of_data = len(month_list)
        data_height_mean = sum(data_list) / number_of_data

        # Initialize the variables.
        position_count = graph_start_position
        anim_length_text = anim_length_data / 2
        anim_curr_frame = anim_start_frame
        anim_end_frame = anim_start_frame + anim_length_data * (number_of_data - 1)

        normalized_data = []
        for data in data_list:
            normalized_data.append(data * 10 / data_height_mean)

        data_height_mean = sum(normalized_data) / number_of_data
        data_height_min = min(normalized_data)

        display_data = []
        if data_height_min > abs(data_height_mean - data_height_min):
            for data in normalized_data:
                display_data.append(data - data_height_min + abs(data_height_mean - data_height_min))
        else:
            for data in normalized_data:
                display_data.append(data)

        # Create a new material for the curve
        material_1 = bpy.data.materials.new(name="anim_material_1")
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
        material_2 = bpy.data.materials.new(name="anim_material_2")
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
        material_3 = bpy.data.materials.new(name="anim_material_3")
        material_3.use_nodes = True
        if material_3.node_tree:
            material_3.node_tree.links.clear()
            material_3.node_tree.nodes.clear()
        nodes = material_3.node_tree.nodes
        links = material_3.node_tree.links
        output = nodes.new(type='ShaderNodeOutputMaterial')
        shader = nodes.new(type='ShaderNodeEmission')
        nodes["Emission"].inputs['Color'].default_value = (1.0, 0.0, 0.0, 1)
        nodes["Emission"].inputs['Strength'].default_value = 1.5
        links.new(shader.outputs[0], output.inputs[0])

        # Create a new material for the z-axis
        material_4 = bpy.data.materials.new(name="anim_material_4")
        material_4.use_nodes = True
        if material_4.node_tree:
            material_4.node_tree.links.clear()
            material_4.node_tree.nodes.clear()
        nodes = material_4.node_tree.nodes
        links = material_4.node_tree.links
        output = nodes.new(type='ShaderNodeOutputMaterial')
        shader = nodes.new(type='ShaderNodeEmission')
        nodes["Emission"].inputs['Color'].default_value = (0.0, 0.0, 1.0, 1)
        nodes["Emission"].inputs['Strength'].default_value = 1.5
        links.new(shader.outputs[0], output.inputs[0])

        # Create a curve and add it to the scene
        curve = bpy.data.curves.new(name="data_curve", type='CURVE')
        curve.dimensions = '3D'
        curve_path = bpy.data.objects.new("my_curve", curve)

        bezier_curve = curve.splines.new('BEZIER') # other options: 'NURBS', 'POLY', 'BSPLINE'
        bezier_curve.bezier_points.add(number_of_data - 1)

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
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.15)
        sphere = context.active_object
        sphere.location = [0, 0, 0]

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

            geometry_nodes = bpy.data.node_groups.new(type="GeometryNodeTree", name="Geometry Nodes")

            if bpy.app.version[0] >= 4:
                geometry_nodes.interface.new_socket('NodeInterfaceInput', in_out='INPUT', socket_type='NodeSocketGeometry')
            else:
                geometry_nodes.inputs.new("NodeSocketGeometry", "Geometry")

            group_input = geometry_nodes.nodes.new("NodeGroupInput")
            group_input.location = (-340.0, 0.0)
            group_input.width, group_input.height = 140.0, 100.0

            if bpy.app.version[0] >= 4:
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

        while data_counter < number_of_data:

            text_month = str(month_list[data_counter])
            text_data = currency_symbol + str(data_list[data_counter])

            # Add a sphere, set its location and animate its size
            bpy.ops.mesh.primitive_uv_sphere_add(radius=0.15)
            sph = context.active_object
            sph.location = [graph_start_position + distance_bet_points * data_counter, 0, display_data[data_counter]]
            sph.scale = [0, 0, 0]
            sph.keyframe_insert(data_path="scale", frame=anim_curr_frame + 4)
            sph.scale = [1, 1, 1]
            sph.keyframe_insert(data_path="scale", frame=anim_curr_frame + 6)

            # Assign the yellow material created above
            sph.data.materials.append(material_1)

            # Add the 1st caption
            bpy.ops.object.text_add()
            ob = bpy.context.object
            ob.data.body = text_month
            ob.data.align_x = "CENTER"
            ob.data.align_y = "CENTER"
            ob.data.extrude = 0.01

            ob.location = [graph_start_position + distance_bet_points * data_counter, 0, display_data[data_counter] + 1.5]
            ob.rotation_euler = [math.radians(90), 0, 0]

            # Animate the caption horizontally
            ob.scale = [0, 0, 0]
            ob.keyframe_insert(data_path="scale", frame=anim_curr_frame - 1)
            ob.scale = [0, 0.5, 0.5]
            ob.keyframe_insert(data_path="scale", frame=anim_curr_frame)
            anim_curr_frame += anim_length_text
            ob.scale = [0.5, 0.5, 0.5]
            ob.keyframe_insert(data_path="scale", frame=anim_curr_frame)

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

            ob.location = [graph_start_position + distance_bet_points * data_counter, 0, display_data[data_counter] + 1]
            ob.rotation_euler = [math.radians(90), 0, 0]

            # Animate the caption horizontally
            ob.scale = [0, 0, 0]
            ob.keyframe_insert(data_path="scale", frame=anim_curr_frame - 1)
            ob.scale = [0, 0.5, 0.5]
            ob.keyframe_insert(data_path="scale", frame=anim_curr_frame)
            anim_curr_frame += anim_length_text
            ob.scale = [0.5, 0.5, 0.5]
            ob.keyframe_insert(data_path="scale", frame=anim_curr_frame)

            # Assign the white material created above
            ob.data.materials.append(material_2)

            # Increase the loop counters
            data_counter += 1
            anim_curr_frame -= anim_length_text
            anim_curr_frame += anim_length_data

        # Add x-axis and set its dimensions
        bpy.ops.mesh.primitive_cube_add()
        ob = context.active_object
        axis_length = graph_start_position + distance_bet_points * (number_of_data - 1) + 2
        ob.dimensions = [axis_length, 0.05, 0.05]
        ob.location = [axis_length / 2, 0, 0]

        # Assign the red material created above
        ob.data.materials.append(material_3)

        bpy.ops.mesh.primitive_cylinder_add(vertices=3, radius=0.3, depth=0.1)
        cyl1 = context.active_object
        cyl1.location = [axis_length, 0, 0]
        cyl1.scale = [1, 1.7, 1]
        cyl1.rotation_euler = [0, math.radians(90), -math.radians(90)]

        # Assign the red material created above
        cyl1.data.materials.append(material_3)

        # Add z-axis and set its dimensions
        bpy.ops.mesh.primitive_cube_add()
        ob = context.active_object
        axis_height = max(display_data) + 3
        ob.dimensions = [0.05, 0.05, axis_height]
        ob.location = [0, 0, axis_height / 2]

        # Assign the blue material created above
        ob.data.materials.append(material_4)

        bpy.ops.mesh.primitive_cylinder_add(vertices=3, radius=0.3, depth=0.1)
        cyl2 = context.active_object
        cyl2.location = [0, 0, axis_height]
        cyl2.scale = [1, 1.7, 1]

        # Assign the blue material created above
        cyl2.data.materials.append(material_4)

        # Set the 3D cursor back to where it was
        bpy.context.scene.cursor.location = saved_cursor_loc

        return {'FINISHED'}
    
    def create_bar_graph(self, x_column, y_column, symbol, anim_start_frame=2, anim_length_data=20, graph_start_position=1, distance_bet_points=2):
        context = bpy.context
        scene = context.scene
        saved_cursor_loc = scene.cursor.location.xyz
        bar_spacing = 1.5
        bar_width = 1
        readout = self.df.iloc[:, [x_column, y_column]].values.tolist()
        # make y log scale
        for i in range(len(readout)):
            readout[i][1] = math.log(readout[i][1])

        # [[names, values],[names, values],[names, values]] format
        # generate bars with names and heights on x axis. Height should be log scale
        # generate text on top of each bar with the value

        # Create a new material for the bars
        material_1 = bpy.data.materials.new(name="anim_material_1")
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
        material_2 = bpy.data.materials.new(name="anim_material_2")
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
        material_3 = bpy.data.materials.new(name="anim_material_3")
        material_3.use_nodes = True
        if material_3.node_tree:
            material_3.node_tree.links.clear()
            material_3.node_tree.nodes.clear()
        nodes = material_3.node_tree.nodes
        links = material_3.node_tree.links
        output = nodes.new(type='ShaderNodeOutputMaterial')
        shader = nodes.new(type='ShaderNodeEmission')
        nodes["Emission"].inputs['Color'].default_value = (1.0, 0.0, 0.0, 1)
        nodes["Emission"].inputs['Strength'].default_value = 1.5
        links.new(shader.outputs[0], output.inputs[0])

        # Create a new material for the z-axis
        material_4 = bpy.data.materials.new(name="anim_material_4")
        material_4.use_nodes = True
        if material_4.node_tree:
            material_4.node_tree.links.clear()
            material_4.node_tree.nodes.clear()
        nodes = material_4.node_tree.nodes
        links = material_4.node_tree.links
        output = nodes.new(type='ShaderNodeOutputMaterial')
        shader = nodes.new(type='ShaderNodeEmission')
        nodes["Emission"].inputs['Color'].default_value = (0.0, 0.0, 1.0, 1)
        nodes["Emission"].inputs['Strength'].default_value = 1.5
        links.new(shader.outputs[0], output.inputs[0])

        # Create the bars in a loop
        data_counter = 0
        anim_curr_frame = anim_start_frame
        for a in readout:
            name = a[0]
            value = round(a[1],1)
            # Add a cube, set its location and animate its size, make height log scale on positive z axis
            bpy.ops.mesh.primitive_cube_add(size=1, location=(data_counter * bar_spacing, 0, 0))
            # set the 3d cursor to the 0,0,0
            bpy.context.scene.cursor.location = (0, 0, 0)
            # set origin to 3d cursor
            bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
            cube = context.active_object
            cube.scale = [bar_width, bar_width, 0] # start with 0 height
            cube.keyframe_insert(data_path="scale", frame=anim_curr_frame + 4)
            # scale z axis to 5
            cube.scale = [bar_width, bar_width, value] # end with the value
            cube.keyframe_insert(data_path="scale", frame=anim_curr_frame + 6)
            # Assign the yellow material created above
            cube.data.materials.append(material_1)
            # Add the caption
            bpy.ops.object.text_add()
            ob = bpy.context.object
            ob.data.body = str(name)
            ob.data.align_x = "CENTER"
            ob.data.align_y = "CENTER"
            # put text above the bar
            ob.data.extrude = 0.01
            ob.location = [data_counter * bar_spacing, 0, -2] # [x, y, z] # 
            ob.rotation_euler = [math.radians(90), 0, 0]
            # Animate the caption horizontally
            ob.scale = [0, 0, 0]
            ob.keyframe_insert(data_path="scale", frame=anim_curr_frame - 1)
            ob.scale = [0, 0.5, 0.5]
            ob.keyframe_insert(data_path="scale", frame=anim_curr_frame)
            anim_curr_frame += anim_length_data
            ob.scale = [0.5, 0.5, 0.5]
            ob.keyframe_insert(data_path="scale", frame=anim_curr_frame)
            # Assign the white material created above
            ob.data.materials.append(material_2)
            # Increase the loop counters
            data_counter += 1
            anim_curr_frame -= anim_length_data
            anim_curr_frame += anim_length_data

        # Add x-axis and set its dimensions
        # bpy.ops.mesh.primitive_cube_add(size=1, location=(data_counter * bar_spacing, 0, 0))
        # ob = context.active_object
        # ob.dimensions = [data_counter * bar_spacing, 0.05, 0.05]
        # ob.location = [data_counter * bar_spacing / 2, 0, 0]
        # Assign the red material created above
        # Set the 3D cursor back to where it was
        bpy.context.scene.cursor.location = saved_cursor_loc

            
        return {'FINISHED'}

    def create_area_graph(self, data_column, month_column, currency_symbol, anim_start_frame=2, anim_length_data=20, graph_start_position=1, distance_bet_points=2):
        context = bpy.context
        scene = context.scene

        # Save the current location of the 3D cursor
        saved_cursor_loc = scene.cursor.location.xyz

        data_list = self.df.iloc[:, data_column - 1]
        month_list = self.df.iloc[:, month_column - 1]
        number_of_data = len(month_list)
        data_height_mean = sum(data_list) / number_of_data

        # Initialize the variables.
        position_count = graph_start_position
        anim_length_text = anim_length_data / 2
        anim_curr_frame = anim_start_frame
        anim_end_frame = anim_start_frame + anim_length_data * (number_of_data - 1)

        normalized_data = []
        for data in data_list:
            normalized_data.append(data * 10 / data_height_mean)

        data_height_mean = sum(normalized_data) / number_of_data
        data_height_min = min(normalized_data)

        display_data = []
        if data_height_min > abs(data_height_mean - data_height_min):
            for data in normalized_data:
                display_data.append(data - data_height_min + abs(data_height_mean - data_height_min))
        else:
            for data in normalized_data:
                display_data.append(data)

        # Create a new material for the curve
        material_1 = bpy.data.materials.new(name="anim_material_1")
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
        material_2 = bpy.data.materials.new(name="anim_material_2")
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
        material_3 = bpy.data.materials.new(name="anim_material_3")
        material_3.use_nodes = True
        if material_3.node_tree:
            material_3.node_tree.links.clear()
            material_3.node_tree.nodes.clear()
        nodes = material_3.node_tree.nodes
        links = material_3.node_tree.links
        output = nodes.new(type='ShaderNodeOutputMaterial')
        shader = nodes.new(type='ShaderNodeEmission')
        nodes["Emission"].inputs['Color'].default_value = (1.0, 0.0, 0.0, 1)
        nodes["Emission"].inputs['Strength'].default_value = 1.5
        links.new(shader.outputs[0], output.inputs[0])

        # Create a new material for the z-axis
        material_4 = bpy.data.materials.new(name="anim_material_4")
        material_4.use_nodes = True
        if material_4.node_tree:
            material_4.node_tree.links.clear()
            material_4.node_tree.nodes.clear()
        nodes = material_4.node_tree.nodes
        links = material_4.node_tree.links
        output = nodes.new(type='ShaderNodeOutputMaterial')
        shader = nodes.new(type='ShaderNodeEmission')
        nodes["Emission"].inputs['Color'].default_value = (0.0, 0.0, 1.0, 1)
        nodes["Emission"].inputs['Strength'].default_value = 1.5
        links.new(shader.outputs[0], output.inputs[0])
        
    def create_scatter_graph(self, x_column, y_column, anim_start_frame=2, anim_length_data=10):
        r = 0.5
        g = 0.5
        b = 0.5
        a = 0.5
        point_radius = .35
        qlty = 5
        plain_height = -1
        sun_height = 15
        
        context = bpy.context
        scene = context.scene
        bpy.ops.object.select_all(action='SELECT')
        bpy.ops.object.delete()
        scene.cursor.location = (0, 0, 0)
        bpy.ops.object.light_add(type='SUN', location=(0, 0, sun_height))
        bpy.ops.mesh.primitive_plane_add(size=20, location=(0, 0, plain_height))
        
        # add a material to plane
        mat = bpy.data.materials.new('point_material')
        mat.diffuse_color = (r,g,b,a)
        # generate data from x and y columns of the dataframe
        x = self.df.iloc[:, x_column - 1]
        y = self.df.iloc[:, y_column - 1]
        print(x)
        print(y)
        # convert data to float
        try:
            x = x.astype(float) 
            y = y.astype(float)
            
            # keep the data in -5 to 5 range
            x = (x - x.min()) / (x.max() - x.min()) * 10 - 5
            y = (y - y.min()) / (y.max() - y.min()) * 10 - 5
            # random height based on the data points
            z = random.choices(range(0, 5), k=len(x))
            # create points
            for ix, iy, iz in zip(x, y, z):
                print(ix, iy, iz)
                try:
                    bpy.ops.mesh.primitive_uv_sphere_add(radius=point_radius, location=(ix, iy, iz))
                    context.object.data.materials.append(mat)
                    
                    # scale items from 0 to 1 scale using keyframes 0 to 100
                    context.object.scale = (0, 0, 0)
                    context.object.keyframe_insert(data_path="scale", frame=anim_start_frame)
                    context.object.scale = (1, 1, 1)
                    context.object.keyframe_insert(data_path="scale", frame=anim_start_frame + anim_length_data)
                    
                    # add keyframes to location
                    context.object.location = (ix, iy, iz)
                    context.object.keyframe_insert(data_path="location", frame=anim_start_frame)
                    context.object.location = (ix, iy, iz)
                    context.object.keyframe_insert(data_path="location", frame=anim_start_frame + anim_length_data)
                    
                    # add text to the points in (x, y) format just above the point
                    bpy.ops.object.text_add(location=(ix, iy, iz+1 ))
                    text = context.object
                    text.data.body = f"({round(ix,1)}, {round(iy,1)})"
                    text.data.align_x = 'CENTER'
                    text.data.align_y = 'CENTER'
                
                    text.data.extrude = 0.1
                    text.data.materials.append(mat)

                    text.scale = (0, 0, 0)
                    text.keyframe_insert(data_path="scale", frame=anim_start_frame)
                    text.scale = (.5, .5, .5)
                    text.keyframe_insert(data_path="scale", frame=anim_start_frame + anim_length_data)
                    
                    
                    
                    
                except:
                    pass 
        except Exception as e:
            # display error message in blender
            self.report({'ERROR'}, str(e))
        return {'FINISHED'}
    
        


########################################
######### LINE GRAPH ###################
########################################

class AddLineGraph(bpy.types.Operator):
    bl_idname = "mesh.add_line_graph"
    bl_label = "Add Line Graph"

    def execute(self, context):
        dataset = DatasetHelper(context.scene.my_file_path)
        dataset.create_line_graph(context.scene.y_axis_column, context.scene.x_axis_column, "$", 2, 20, 1, 2)
        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.prop(self, "axis_x")
        row = layout.row()
        row.prop(self, "axis_y")

########################################
#########BAR CHART######################
########################################

class AddBarChart(bpy.types.Operator):
    bl_idname = "mesh.add_bar_chart"
    bl_label = "Add Bar Chart"

    def execute(self, context):
        # Add custom code to create a bar chart
        dataset = DatasetHelper(context.scene.my_file_path)
        dataset.create_bar_graph(context.scene.y_axis_column, context.scene.x_axis_column, "", 2, 20, 1, 2)
        print("Creating Bar Chart")
        return {'FINISHED'}
    
    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)
    
    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.prop(self, "axis_x")
        row = layout.row()
        row.prop(self, "axis_y")

########################################
#########PIE CHART######################
########################################
class AddAreaChart(bpy.types.Operator):
    bl_idname = "mesh.add_area_chart"
    bl_label = "Add Area Chart"

    def execute(self, context):
        # Add custom code to create a pie chart
        dataset = DatasetHelper(context.scene.my_file_path)
        dataset.create_area_graph(context.scene.y_axis_column, context.scene.x_axis_column, "👇", 2, 20, 1, 2)
        print("Creating Area Chart")
        return {'FINISHED'}
    
    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)
    
    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.prop(self, "axis_x")
        row = layout.row()
        row.prop(self, "axis_y")

########################################
#########SCATTER PLOT###################
########################################
class AddScatterPlot(bpy.types.Operator):
    bl_idname = "mesh.add_scatter_plot"
    bl_label = "Add Scatter Plot"

    def execute(self, context):
        dataset = DatasetHelper(context.scene.my_file_path)
        dataset.create_scatter_graph(context.scene.y_axis_column, context.scene.x_axis_column, 2, 20)
        print("Creating Scatter Plot")
        return {'FINISHED'}
    
    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)
    
    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.prop(self, "axis_x")
        row = layout.row()
        row.prop(self, "axis_y")


class XAxisColumn(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(name="X Axis", default="")
    value: bpy.props.IntProperty(name="Value", default=0, min=1, max=10)

class YAxisColumn(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(name="Y Axis", default="")
    value: bpy.props.IntProperty(name="Value", default=0, min=1, max=10)
   
########################################
#########3D VISUALIZATION PANEL#########
########################################
class View3DPanel(bpy.types.Panel):
    bl_label = "3D Visualization Toolkit"
    bl_idname = "VIEW3D_PT_my_custom_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = '3D Visualization'

    # declare properties

    def draw(self, context):
        if not hasattr(context.scene, "my_file_path"):
            context.scene.my_file_path = ""
        else:
            print(context.scene.my_file_path)
        dataset = DatasetHelper(context.scene.my_file_path)

        info = "Blender 3D Visualization Toolkit by Team 3"

        layout = self.layout

        row = layout.row()
        row.operator("test.open_filebrowser", text="Open CSV File")

        row = layout.row()
        row.label(text="Selected file:")
        row = layout.row()
        row.label(text=context.scene.my_file_path)

        # dropdown for selecting the x-axis column
        row = layout.row()
        row.label(text="X Axis:")
        row = layout.row()
        row.prop(context.scene, "x_axis_column", text="X Axis")

        # dropdown for selecting the y-axis column
        row = layout.row()
        row.label(text="Y Axis:")
        row = layout.row()
        row.prop(context.scene, "y_axis_column", text="Y Axis")

        # buttons for adding different types of graphs
        row = layout.row()
        row.label(text="Graphs:")
        row = layout.row()
        row.operator("mesh.add_line_graph", text="Line Graph")
        row.operator("mesh.add_bar_chart", text="Bar Chart")
        row = layout.row()
        row.operator("mesh.add_area_chart", text="Pie Chart")
        row.operator("mesh.add_scatter_plot", text="Scatter Plot")
        row = layout.row()
        row.operator("mesh.add_histogram", text="Histogram")

        

        
def clear_properties():
    del bpy.types.Scene.my_file_path
    del bpy.types.Scene.x_axis_column
    del bpy.types.Scene.y_axis_column

########################################
#########REGISTER AND UNREGISTER########
########################################
def register():
    init_properties()
    bpy.utils.register_class(OpenFilebrowser)
    bpy.utils.register_class(View3DPanel)
    bpy.utils.register_class(AddLineGraph)
    bpy.utils.register_class(AddBarChart)
    bpy.utils.register_class(AddScatterPlot)
    bpy.utils.register_class(AddAreaChart)
    bpy.utils.register_class(XAxisColumn)
    bpy.utils.register_class(YAxisColumn)
    bpy.types.Scene.my_file_path = bpy.props.StringProperty(name="File Path", default="")

def unregister():
    bpy.utils.unregister_class(OpenFilebrowser)
    bpy.utils.unregister_class(View3DPanel)
    bpy.utils.unregister_class(AddLineGraph)
    bpy.utils.unregister_class(AddBarChart)
    bpy.utils.unregister_class(AddScatterPlot)
    bpy.utils.unregister_class(AddAreaChart)
    bpy.utils.unregister_class(XAxisColumn)
    bpy.utils.unregister_class(YAxisColumn)
    del bpy.types.Scene.my_file_path
    del bpy.types.Scene.x_axis_column
    del bpy.types.Scene.y_axis_column
    clear_properties()




# execution part
if __name__ == "__main__":
    register()
