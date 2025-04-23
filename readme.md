# 3D Visualization Toolkit for Blender - README

## Overview
The **3D Visualization Toolkit** is a Blender plugin designed to enhance data visualization directly within the Blender environment. This plugin allows users to import CSV files and generate interactive visualizations, including line graphs, bar charts, pie charts, scatter plots, and histograms. Additionally, users can customize object properties and colors, making it an ideal tool for creating compelling 3D data visualizations.

## Features

1. **CSV File Import**:
   - Open and select a CSV file directly within Blender.
   - Store the selected file path for further processing.

2. **Data Visualization**:
   - Add and customize 3D objects based on imported data.
   - Generate various types of graphs:
     - Line Graph
     - Bar Chart
     - Pie Chart
     - Scatter Plot
     - Histogram

3. **Object Manipulation**:
   - Drag objects along the X, Y, and Z axes.
   - Set custom colors for objects using an intuitive color picker.

4. **User Interface Integration**:
   - A dedicated panel in the Blender 3D Viewport under the "3D Visualization" tab for easy access to plugin features.

## Installation

1. Clone or download this repository:
   ```
   git clone https://github.com/zaid-kamil/fyp_3d_vis_blender_plugin.git
   ```

2. Copy the `project_main.py` file to your Blender scripts directory:
   ```
   <Blender Installation Directory>/scripts/addons/
   ```

3. Open Blender, go to `Edit > Preferences > Add-ons`, and enable the "3D Visualization Toolkit" plugin.

## Usage

1. **Activate the Plugin**:
   - After enabling the plugin in Blender preferences, a new tab named "3D Visualization" will appear in the 3D Viewport's side panel.

2. **Import CSV Data**:
   - Click the "Open CSV File" button to browse and select a CSV file.
   - The selected file path is displayed for reference.

3. **Create Visualizations**:
   - Use the buttons under the "Graphs" section to add various types of visualizations:
     - Line Graph
     - Bar Chart
     - Pie Chart
     - Scatter Plot
     - Histogram

4. **Customize Objects**:
   - Drag objects along the X, Y, and Z axes using the provided controls.
   - Set object color using the "Set Object Color" option.

## Development

This plugin is written in Python and leverages Blender's `bpy` library for creating custom operators and panels.

### Key Classes and Functions
- `OpenFilebrowser`: Open a file browser to select a CSV file.
- `AddCustomObject`: Add a custom 3D object to the scene.
- `AddLineGraph`, `AddBarChart`, `AddPieChart`, `AddScatterPlot`, `AddHistogram`: Generate different types of visualizations.
- `SetObjectColor`: Customize the color of selected objects.
- `VIEW3D_PT_my_custom_panel`: Define the user interface panel in the 3D Viewport.

## License

This project is licensed under the MIT License. See the `LICENSE` file for more details.

## Contribution

Contributions are welcome! Feel free to open issues or submit pull requests to improve the plugin.

---

With this plugin, you can transform your data into stunning 3D visualizations directly within Blender. Happy visualizing!
