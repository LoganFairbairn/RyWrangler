# This file contains the user interface for this add-on.

import bpy

class RYWRANGLER_MT_pie_menu(bpy.types.Menu):
    bl_idname = "RYWRANGLER_MT_pie_menu"
    bl_label = "RyWrangler"

    def draw(self, context):
        pie = self.layout.menu_pie()

        # Masks
        row = pie.row(align=True)
        row.scale_x = 2.0
        row.scale_y = 2.0
        row.operator("rywrangler.add_grunge", text="", icon='FORCE_TURBULENCE')
        row.operator("rywrangler.add_edge_wear", text="", icon='EDGESEL')
        
        # Layers
        row = pie.row(align=True)
        row.scale_x = 2.0
        row.scale_y = 2.0
        row.operator("rywrangler.add_paint_layer", text="", icon='TPAINT_HLT')
        row.operator("rywrangler.add_uv_layer", text="", icon='UV')
        row.operator("rywrangler.add_decal_layer", text="", icon='STICKY_UVS_DISABLE')
        row.operator("rywrangler.add_triplanar_layer", text="", icon='FILE_3D')

        pie.operator("rywrangler.auto_link_nodes", text="Auto-Link")
        pie.operator("rywrangler.isolate_node", text="Isolate")
        pie.operator("rywrangler.edit_image_externally", text="Edit Externally")
        pie.operator("rywrangler.import_texture_set", text="Import Texture Set")

class RYWRANGLER_OT_open_pie_menu(bpy.types.Operator):
    bl_idname = "wm.call_custom_pie"
    bl_label = "Call Shader Editor Pie Menu"

    def execute(self, context):
        bpy.ops.wm.call_menu_pie(name=RYWRANGLER_MT_pie_menu.bl_idname)
        return {'FINISHED'}

class RYWRANGLER_PT_side_panel(bpy.types.Panel):
    bl_label = "RyWrangler"
    bl_idname = "RYWRANGLER_PT_shader_panel"
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'
    bl_category = 'RyWrangler'

    @classmethod
    def poll(cls, context):
        return context.space_data.tree_type == 'ShaderNodeTree'

    def draw(self, context):
        layout = self.layout

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
