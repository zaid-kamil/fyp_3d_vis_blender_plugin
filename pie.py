import bpy
import math

def create_pie_chart(names, values, radius, animation_start_frame, graph_start_position):
    # Calculate total value
    total_value = sum(values)
    
    # Create pie chart
    bpy.ops.object.select_all(action='DESELECT')
    bpy.ops.object.select_by_type(type='MESH')
    bpy.ops.object.delete()

    bpy.ops.mesh.primitive_circle_add(vertices=len(names), radius=radius, fill_type='NOTHING')
    pie_chart = bpy.context.object
    pie_chart.name = "PieChart"

    # Set animation start frame
    bpy.context.scene.frame_start = animation_start_frame

    # Create slices
    current_rotation = graph_start_position
    for i, (name, value) in enumerate(zip(names, values)):
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.mesh.select_face_by_sides(number=4, type='EQUAL', extend=False)
        bpy.ops.mesh.extrude_region_move(TRANSFORM_OT_translate={"value":(0, 0, 0.1)})
        bpy.ops.object.mode_set(mode='OBJECT')

        slice_angle = (value / total_value) * 2 * math.pi
        pie_slice = pie_chart.copy()
        pie_slice.data = pie_chart.data.copy()
        bpy.context.collection.objects.link(pie_slice)

        pie_slice.rotation_euler[2] = current_rotation + slice_angle / 2
        pie_slice.scale[0] = radius
        pie_slice.scale[1] = radius
        pie_slice.scale[2] = 0.1

        current_rotation += slice_angle

        # Keyframe scale for animation
        pie_slice.scale[2] = value / total_value
        pie_slice.keyframe_insert(data_path="scale", frame=animation_start_frame)
        pie_slice.scale[2] = 0.1
        pie_slice.keyframe_insert(data_path="scale", frame=animation_start_frame + 1)

    bpy.context.scene.frame_end = animation_start_frame + 1

# Example usage
names = ["A", "B", "C", "D"]
values = [30, 20, 15, 35]
radius = 1.0
animation_start_frame = 1
graph_start_position = 0

create_pie_chart(names, values, radius, animation_start_frame, graph_start_position)
