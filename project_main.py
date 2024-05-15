import bpy

class OpenFilebrowser(bpy.types.Operator):
    bl_idname = "test.open_filebrowser"
    bl_label = "Select a file"
    
    filepath: bpy.props.StringProperty(subtype="FILE_PATH")

    def execute(self, context):
        print("Selected file:", self.filepath)
        context.scene.my_file_path = self.filepath  # Store the filepath in the scene property
        return {'FINISHED'}
    
    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

class AddCustomObject(bpy.types.Operator):
    bl_idname = "mesh.add_custom_object"
    bl_label = "Add Custom Object"
    bl_options = {'REGISTER', 'UNDO'}
    
class DataColumnItem(bpy.types.PropertyGroup):
    """Class to store properties for each data column."""
    name: bpy.props.StringProperty(name="Name")
   
    def draw(self, context):
        layout = self.layout
        scene = context.scene

        obj = context.active_object
        if obj is not None and obj.type == 'MESH':
            row = layout.row()
            row.label(text="Drag object along axis:")
            row = layout.row()
            row.prop(obj, "location", index=0, text="X")
            row.prop(obj, "location", index=1, text="Y")
            row.prop(obj, "location", index=2, text="Z")
            
        column = context.scene.data_columns[context.scene.active_column_index].name
        context.scene.y_axis_column = column
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

class AddLineGraph(bpy.types.Operator):
    bl_idname = "mesh.add_line_graph"
    bl_label = "Add Line Graph"

    def execute(self, context):
        # Add custom code to create a line graph
        print("Creating Line Graph")
        return {'FINISHED'}

class AddBarChart(bpy.types.Operator):
    bl_idname = "mesh.add_bar_chart"
    bl_label = "Add Bar Chart"

    def execute(self, context):
        # Add custom code to create a bar chart
        print("Creating Bar Chart")
        return {'FINISHED'}

class AddPieChart(bpy.types.Operator):
    bl_idname = "mesh.add_pie_chart"
    bl_label = "Add Pie Chart"

    def execute(self, context):
        # Add custom code to create a pie chart
        print("Creating Pie Chart")
        return {'FINISHED'}

class AddScatterPlot(bpy.types.Operator):
    bl_idname = "mesh.add_scatter_plot"
    bl_label = "Add Scatter Plot"

    def execute(self, context):
        # Add custom code to create a scatter plot
        print("Creating Scatter Plot")
        return {'FINISHED'}

class AddHistogram(bpy.types.Operator):
    bl_idname = "mesh.add_histogram"
    bl_label = "Add Histogram"

    def execute(self, context):
        # Add custom code to create a histogram
        print("Creating Histogram")
        return {'FINISHED'}

class SetObjectColor(bpy.types.Operator):
    bl_idname = "object.set_object_color"
    bl_label = "Set Object Color"

    color: bpy.props.FloatVectorProperty(name="Color", subtype='COLOR', size=3, min=0.0, max=1.0, default=(1.0, 1.0, 1.0))

    def execute(self, context):
        obj = context.active_object
        if obj:
            obj.color = self.color
        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "color")

class VIEW3D_PT_my_custom_panel(bpy.types.Panel): 
    bl_space_type = "VIEW_3D"  
    bl_region_type = "UI"  
    bl_category = "3D Visualization"  
    bl_label = "3D Visualization Toolkit"  

    def draw(self, context):
        layout = self.layout

        row = layout.row()
        row.operator("test.open_filebrowser", text="Open CSV File")

        row = layout.row()
        row.label(text="Selected file:")
        row = layout.row()
        row.label(text=context.scene.my_file_path)

        row = layout.row()
        row.operator("mesh.add_custom_object", text="Add Custom Object")
        layout.prop(scene, "x_axis_column", text="X Axis")
        layout.prop(scene, "y_axis_column", text="Y Axis")


        row = layout.row()
        row.label(text="Graphs:")
        row = layout.row()
        row.operator("mesh.add_line_graph", text="Line Graph")
        row.operator("mesh.add_bar_chart", text="Bar Chart")
        row = layout.row()
        row.operator("mesh.add_pie_chart", text="Pie Chart")
        row.operator("mesh.add_scatter_plot", text="Scatter Plot")
        row = layout.row()
        row.operator("mesh.add_histogram", text="Histogram")

        row = layout.row()
        row.label(text="Color:")
        row.operator("object.set_object_color", text="Set Object Color")
        
def register():
    bpy.utils.register_class(CustomPanel)
    
def unregister_columns():
    bpy.utils.unregister_class(DataColumnItem)
    del bpy.types.Scene.data_columns
    del bpy.types.Scene.active_column_index


    bpy.utils.register_class(AddLineGraph)
    bpy.utils.register_class(AddBarChart)
    bpy.utils.register_class(AddPieChart)
    bpy.utils.register_class(AddScatterPlot)
    bpy.utils.register_class(AddHistogram)
    bpy.utils.register_class(SetObjectColor)
    bpy.utils.register_class(VIEW3D_PT_my_custom_panel)
    bpy.types.Scene.my_file_path = bpy.props.StringProperty(
        name="File Path",
        description="Path of the selected file",
        default=""
    )

def unregister():
    del bpy.types.Scene.my_file_path
    bpy.utils.unregister_class(OpenFilebrowser)
    bpy.utils.unregister_class(AddCustomObject)
    del bpy.types.Scene.x_axis_column
    del bpy.types.Scene.y_axis_column
    bpy.utils.unregister_class(AddLineGraph)
    bpy.utils.unregister_class(AddBarChart)
    bpy.utils.unregister_class(AddPieChart)
    bpy.utils.unregister_class(AddScatterPlot)
    bpy.utils.unregister_class(AddHistogram)
    bpy.utils.unregister_class(SetObjectColor)
    bpy.utils.unregister_class(VIEW3D_PT_my_custom_panel)

if __name__ == "__main__":
    register()