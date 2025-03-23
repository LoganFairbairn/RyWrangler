# This file contains the user interface for this add-on.

import bpy
from bpy.types import Operator

UI_Y_SCALE = 1.5

class RYWRANGLER_OT_open_menu(Operator):
    bl_label = "Open RyWrangler Menu"
    bl_idname = "rywrangler.open_menu"
    bl_description = "Opens the RyWrangler menu"

    def execute(self, context):
        return {'FINISHED'}

    # Opens the popup menu.
    def invoke(self, context, event):
        return context.window_manager.invoke_popup(self, width=300)

    # Draws the properties in the popup.
    def draw(self, context):
        layout = self.layout

        # Draw a grip icon so users can move the pop-up around if they desire.
        layout.label(text="", icon='GRIP')

        # Draw operators to help quickly adjust node connections.
        row = layout.row()
        row.scale_x = 2
        row.scale_y = UI_Y_SCALE
        row.operator("rywrangler.auto_link_nodes", text="", icon='LINKED')
        row.operator("rywrangler.isolate_node", text="", icon='MATERIAL')

        # Draw operators to add material layers.
        row = layout.row()
        row.scale_y = UI_Y_SCALE
        row.operator("rywrangler.add_material_layer", text="Material")
        row.operator("rywrangler.add_paint_layer", text="Paint")
        row = layout.row()
        row.scale_y = UI_Y_SCALE
        row.operator("rywrangler.add_image_layer", text="Image")
        row.operator("rywrangler.add_decal_layer", text="Decal")
        row = layout.row()
        row.scale_y = UI_Y_SCALE
        row.operator("rywrangler.add_triplanar_layer", text="Triplanar")
        row.operator("rywrangler.add_triplanar_hexgrid_layer", text="Triplanar Hex Grid")

        row = layout.row()
        row.scale_y = UI_Y_SCALE
        row.operator("rywrangler.add_grunge", text="Grunge")
        row.operator("rywrangler.add_edge_wear", text="Edge Wear")

        row = layout.row()
        row.scale_y = UI_Y_SCALE
        row.operator("rywrangler.add_blur", text="Blur")
        row = layout.row()
        row.scale_y = UI_Y_SCALE
        row.operator("rywrangler.adjust_normal_intensity", text="Adjust Normal Intensity")
        row.operator("rywrangler.mix_normal_maps", text="Mix Normal Maps")

        split = layout.split(factor=0.25)
        first_column = split.column()
        second_column = split.column()

        texture_settings = bpy.context.scene.rywrangler_texture_settings
        row = first_column.row()
        row.label(text="Shader: ")
        row = second_column.row()
        shader_node = texture_settings.shader_node
        row.prop(texture_settings, "shader_node", text="")
        if shader_node == "GROUP_NODE":
            row = first_column.row()
            row.label(text="")
            row = second_column.row()
            row.prop(bpy.context.scene, "rywrangler_shader_node", text="")

        row = first_column.row()
        row.label(text="Resolution:")
        row = second_column.row()
        row.prop(texture_settings, "image_width", text="")
        match_image_resolution = texture_settings.match_image_resolution
        if match_image_resolution:
            row.prop(texture_settings, "match_image_resolution", toggle=True, icon='LOCKED', text="")
        else:
            row.prop(texture_settings, "match_image_resolution", toggle=True, icon='UNLOCKED', text="")
        row.prop(texture_settings, "image_height", text="")

        row = first_column.row()
        row.label(text="32-bit: ")
        row = second_column.row()
        thirty_two_bit_color = texture_settings.thirty_two_bit
        if thirty_two_bit_color:
            row.prop(texture_settings, "thirty_two_bit", text="True", toggle=True)
        else:
            row.prop(texture_settings, "thirty_two_bit", text="False", toggle=True)

        row = layout.row(align=True)
        row.prop(texture_settings, "raw_image_folder", text="")
        row.operator("rywrangler.set_raw_texture_folder", text="", icon="FOLDER_REDIRECT")
        row.operator("rywrangler.open_raw_texture_folder", text="", icon="FILE_FOLDER")

        row = layout.row()
        row.scale_y = UI_Y_SCALE
        row.operator("rywrangler.edit_image_externally")

        # Draw the add-on name and version.
        layout.separator(type='LINE')
        row = layout.row()
        row.alignment = 'CENTER'
        row.label(text="RyWrangler 1.0.0")