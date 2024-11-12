import bpy, math
from bpy.utils import register_class, unregister_class
from subprocess import Popen
from os import system, path, makedirs

def dks_ruv_get_export_path():
    _export_path = bpy.path.abspath('//') + bpy.context.preferences.addons[__package__].preferences.option_export_folder + '\\'

    if not path.exists(_export_path):
        makedirs(_export_path)

    return _export_path

def dks_ruv_filename(self, context):
    _object_name = bpy.context.active_object.name
    _export_path = dks_ruv_get_export_path()
    _export_file = _export_path + _object_name + '_ruv.fbx'

    if bpy.context.preferences.addons[__package__].preferences.option_save_before_export:
        bpy.ops.wm.save_mainfile()

    return _export_file

def dks_ruv_fbx_export(self, context):
    _export_file = dks_ruv_filename(self, context)

    bpy.ops.object.mode_set(mode='OBJECT')

    bpy.ops.export_scene.fbx(filepath=_export_file, use_selection=True, check_existing=False, axis_forward='-Z', axis_up='Y', filter_glob="*.fbx", global_scale=1.0, apply_unit_scale=True, bake_space_transform=False, object_types={'MESH'}, use_mesh_modifiers=True, mesh_smooth_type='OFF', use_mesh_edges=False, use_tspace=False, use_custom_props=False, add_leaf_bones=False, primary_bone_axis='Y', secondary_bone_axis='X', use_armature_deform_only=False, bake_anim=True, bake_anim_use_all_bones=True, bake_anim_use_nla_strips=True, bake_anim_use_all_actions=True, bake_anim_force_startend_keying=True, bake_anim_step=1.0, bake_anim_simplify_factor=1.0, path_mode='AUTO', embed_textures=False, batch_mode='OFF', use_batch_own_dir=True, use_metadata=True)

    return _export_file

class dks_ruv_fbx_export_execute(bpy.types.Operator):
    bl_idname = "dks_ruv.obj_export"
    bl_label = "Export FBX."

    def execute(self, context):
        _export_file = dks_ruv_fbx_export(self, context)
        return {'FINISHED'}

class dks_ruv_export(bpy.types.Operator):
    bl_idname = "dks_ruv.export"
    bl_label = "RizomUV"
    bl_description = "Export to RizomUV"

    def execute(self, context):
        _export_file = dks_ruv_fbx_export(self, context)
        ruv_exe = bpy.context.preferences.addons[__package__].preferences.option_ruv_exe

        # Print the path for debugging
        print(f"RizomUV Executable Path: {ruv_exe}")

        try:
            Popen([ruv_exe, _export_file])
        except FileNotFoundError as e:
            self.report({'ERROR'}, f"RizomUV executable not found: {e}")
            return {'CANCELLED'}

        return {'FINISHED'}

class dks_ruv_import(bpy.types.Operator):
    bl_idname = "dks_ruv.import"
    bl_label = "RizomUV"
    bl_description = "Import from RizomUV"

    def execute(self, context):
        obj_selected = bpy.context.object
        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

        bpy.ops.import_scene.fbx(filepath=dks_ruv_filename(self, context), axis_forward='-Z', axis_up='Y')

        obj_imported = bpy.context.selected_objects[0]

        obj_imported.select_set(True)
        obj_selected.select_set(True)
        bpy.context.view_layer.objects.active = obj_imported

        bpy.ops.object.join_uvs()

        obj_selected.select_set(False)

        bpy.ops.object.delete()

        bpy.context.view_layer.objects.active = obj_selected
        obj_selected.select_set(True)

        bpy.ops.object.mode_set(mode='EDIT', toggle=False)
        bpy.ops.uv.seams_from_islands(mark_seams=True, mark_sharp=False)
        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

        return {'FINISHED'}

classes = (
    dks_ruv_fbx_export_execute,
    dks_ruv_import,
    dks_ruv_export,
)

def register():
    for cls in classes:
        register_class(cls)

def unregister():
    for cls in reversed(classes):
        unregister_class(cls)
