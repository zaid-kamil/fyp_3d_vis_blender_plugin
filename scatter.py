import bpy

bl_info = {
    "name": "Scatter Plot Generator",
    "author": "Zaid Kamil",
    "version": (1, 0),
    "blender": (3,1,2),
    "location": "View3D > Add > Mesh > Scatter Plot",
    "description": "Generates a scatter plot with random data",
    "warning": "",
    "wiki_url": "",
    "category": "Add Mesh",
}

from random import uniform

# color parameters
r = 0.5
g = 0.5
b = 0.5
a = 0.5
sun_height = 15
plain_height = -5
point_radius = 0.5
qlty = 5

addon_keymaps = []


class ScatterPlot(bpy.types.Operator):
    """Generates a scatter plot with random data"""

    bl_idname = "mesh.scatter_plot"
    bl_label = "Scatter Plot"
    bl_options = {'REGISTER', 'UNDO'}


    # Create a scatter plot with random data
    def create_scatter_plot(self, context):
        # Delete any existing data
        bpy.ops.object.select_all(action='SELECT')
        bpy.ops.object.delete()

        # center the cursor
        context.scene.cursor.location = (0, 0, 0)
        
        # Add a sun light
        bpy.ops.object.light_add(type='SUN', location=(0, 0, sun_height))

        # Add a plane for the scatter plot
        bpy.ops.mesh.primitive_plane_add(size=20, location=(0, 0, plain_height))

        # add a material to the plane
        mat = bpy.data.materials.new("point_material")
        mat.diffuse_color = (r, g, b, a)

        # Generate random data for the scatter plot
        data = [[uniform(-5, 5), uniform(-5, 5), uniform(-5, 5)] for i in range(100)]

        # Create a new scatter plot
        for x, y, z in data:
            bpy.ops.mesh.primitive_ico_sphere_add(radius=point_radius, location=(x, y, z), subdivisions=qlty)
            # set material to the sphere
            context.object.data.materials.append(mat)
            # scale items from 0 to 1 scale using keyframes 0 to 100
            context.object.scale = (0, 0, 0)
            context.object.keyframe_insert(data_path="scale", frame=0)
            context.object.scale = (1, 1, 1)
            context.object.keyframe_insert(data_path="scale", frame=100)
        
        # place text on each point with the coordinates
        

        

        return {'FINISHED'}
    
    def execute(self, context):
        return self.create_scatter_plot(context)
    
    def invoke(self, context, event):
        return self.execute(context)
    
def menu_func(self, context):
    self.layout.operator(ScatterPlot.bl_idname, text="Scatter Plot", icon='PLUGIN')




def register():
    bpy.utils.register_class(ScatterPlot)
    bpy.types.VIEW3D_MT_mesh_add.append(menu_func)
    # handle the keymap

    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc:
        km = kc.keymaps.new(name='3D View', space_type='VIEW_3D')
        kmi = km.keymap_items.new(ScatterPlot.bl_idname, 'S', 'PRESS', ctrl=True, shift=True) # ctrl + shift + s
        addon_keymaps.append((km, kmi))

    


def unregister():
    bpy.utils.unregister_class(ScatterPlot)
    bpy.types.VIEW3D_MT_mesh_add.remove(menu_func)
    # handle the keymap
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()


if __name__ == "__main__":
    register()

    

    