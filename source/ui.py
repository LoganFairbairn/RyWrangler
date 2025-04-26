# This file contains the user interface for this add-on.

import bpy

UI_Y_SCALE = 1

class RYWRANGLER_PT_side_panel(bpy.types.Panel):
    bl_label = "Custom Shader Tools"
    bl_idname = "rywrangler.shader_panel"
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'
    bl_category = 'RyWrangler'

    @classmethod
    def poll(cls, context):
        return context.space_data.tree_type == 'ShaderNodeTree'

    def draw(self, context):
        layout = self.layout

        # Draw operators to add material layers.
        layout.operator("rywrangler.add_material_layer", text="Material")
        layout.operator("rywrangler.add_paint_layer", text="Paint")
        layout.operator("rywrangler.add_image_layer", text="Image")
        layout.operator("rywrangler.add_decal_layer", text="Decal")
        layout.operator("rywrangler.add_triplanar_layer", text="Triplanar")
        layout.operator("rywrangler.add_triplanar_hexgrid_layer", text="Triplanar Hex Grid")
        layout.operator("rywrangler.add_grunge", text="Grunge")
        layout.operator("rywrangler.add_edge_wear", text="Edge Wear")
        layout.operator("rywrangler.add_blur", text="Blur")
        layout.operator("rywrangler.adjust_normal_intensity", text="Adjust Normal Intensity")
        layout.operator("rywrangler.mix_normal_maps", text="Mix Normal Maps")

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

class RYWRANGLER_MT_pie_menu(bpy.types.Menu):
    bl_label = "RyWrangler"
    bl_idname = "rywrangler.pie_menu"

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()
        pie.operator("rywrangler.isolate_node", text="Isolate", icon='MATERIAL')
        pie.operator("rywrangler.auto_link_nodes", text="Auto-Link", icon='LINKED')
