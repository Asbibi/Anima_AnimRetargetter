import bpy
from bpy.types import Operator


class AAR_OT_LabelBone(Operator):
	bl_idname = "pose.aar_label_bone"
	bl_label = "Label A Bone"
	bl_description = "Label a bone by assigning it to the dedicated Bone Group"
	
	aar_group : bpy.props.StringProperty(default="AAR_Base")
	aar_colorNormal : bpy.props.FloatVectorProperty(default=(0.0, 0.0, 0.0), min=0, max=1)
	aar_colorSelect : bpy.props.FloatVectorProperty(default=(0.5, 0.5, 0.5), min=0, max=1)
	aar_colorActive : bpy.props.FloatVectorProperty(default=(1.0, 1.0, 1.0), min=0, max=1)
	

	@classmethod
	def poll(cls, context):
		obj = context.object
		if obj is not None:
			if obj.mode == "POSE":
				if len(context.selected_pose_bones) > 0:
					return True
		return False


	def execute(self, context):
		bone_groups = context.object.pose.bone_groups
		#self.report({'WARNING'}, self.aar_group)
		
		if not(self.aar_group in bone_groups):
			bpy.ops.pose.group_add()
			new_group = bone_groups[len(bone_groups) -1]
			new_group.name = self.aar_group
			new_group.color_set = "CUSTOM"
			theme = new_group.colors
			theme.normal = self.aar_colorNormal
			theme.select = self.aar_colorSelect
			theme.active = self.aar_colorActive
		
		groupIndex = 0
		for i in range(0, len(bone_groups)):
			if bone_groups[i].name == self.aar_group:
				groupIndex = i
				break
		bpy.ops.pose.group_assign(type = groupIndex + 1)
		
		context.object.data.aar_labelChecked = False;
		return {'FINISHED'}





class AAR_OT_UnlabelBone(Operator):
	bl_idname = "pose.aar_unlabel_bone"
	bl_label = "Unlabel selected Bones"
	bl_description = "Unlabel selected bones by removing them from the dedicated Bone Group"
	
	aar_group : bpy.props.StringProperty(default="AAR_Base")
	

	@classmethod
	def poll(cls, context):
		obj = context.object
		if obj is not None:
			if obj.mode == "POSE":
				if len(context.selected_pose_bones) > 0:
					return True
		return False


	def execute(self, context):
		bone_groups = context.object.pose.bone_groups
		if not(self.aar_group in bone_groups):
			return {'FINISHED'}
		
		selectedBones = context.selected_pose_bones
		group = bone_groups[self.aar_group]
		for bone in selectedBones:
			if bone.bone_group == group:
				bone.bone_group = None
		
		context.object.data.aar_labelChecked = False;
		return {'FINISHED'}
	
	
	
	
	
	
class AAR_PROP_GroupNameListProperty(bpy.types.PropertyGroup):
    groupName : bpy.props.StringProperty(default="AAR_Base")
	
	
class AAR_OT_UnlabelBoneAll(Operator):
	bl_idname = "pose.aar_unlabel_bones_all"
	bl_label = "Unlabel selected Bones from All"
	bl_description = "Unlabel selected bones by removing them from all the Label Bone Groups"
	
	aar_groups : bpy.props.CollectionProperty(type=AAR_PROP_GroupNameListProperty)
	

	@classmethod
	def poll(cls, context):
		obj = context.object
		if obj is not None:
			if obj.mode == "POSE":
				if len(context.selected_pose_bones) > 0:
					return True
		return False


	def execute(self, context):
		all_bone_groups = context.object.pose.bone_groups
		my_bone_groups = []
		for groupName_prop in self.aar_groups:
			if groupName_prop.groupName in all_bone_groups:
				my_bone_groups.append(all_bone_groups[groupName_prop.groupName])
		
		selectedBones = context.selected_pose_bones
		for bone in selectedBones:
			if bone.bone_group in my_bone_groups:
				bone.bone_group = None
		
		context.object.data.aar_labelChecked = False;
		return {'FINISHED'}




class AAR_OT_AutoLabel(Operator):
	bl_idname = "pose.aar_auto_label"
	bl_label = "Auto-Label Armature"
	bl_description = "Auto-Label an armature's bones"
	
	aar_groups : bpy.props.CollectionProperty(type=AAR_PROP_GroupNameListProperty)
	

	@classmethod
	def poll(cls, context):
		obj = context.object
		if obj is not None:
			if obj.type == "ARMATURE":
				return True
		return False


	def execute(self, context):
		self.report({'WARNING'}, "TODO - Not implemented yet")
		return {'FINISHED'}
	




if __name__ == "__main__":
	bpy.utils.register_class(AAR_PROP_GroupNameListProperty)
	bpy.utils.register_class(AAR_OT_LabelBone)
	bpy.utils.register_class(AAR_OT_UnlabelBone)
	bpy.utils.register_class(AAR_OT_UnlabelBoneAll)
	bpy.utils.register_class(AAR_OT_AutoLabel)