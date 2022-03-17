import bpy

from bpy.types import Panel


def actionLayout(subBox, action):
    row = subBox.row()
    row.label(text=action.name, icon="ACTION")
    row.prop(action, "aar_loopIdle", text="", icon="POSE_HLT")
    row.prop(action, "aar_useGround", text="", icon="GRID")
    op = row.operator("pose.aar_unregister_action", text="", icon="PANEL_CLOSE")
    op.aar_action = action.name
    
def labelSingleLayout(colName, colLabel, colUnLabel, name, colorNormal, colorSelect, colorActive):
    colName.label(text=name + ":")
    
    op = colLabel.operator("pose.aar_label_bone", text="Label", icon="ARROW_LEFTRIGHT")
    op.aar_group = "AAR_" + name
    op.aar_colorNormal = colorNormal
    op.aar_colorSelect = colorSelect
    op.aar_colorActive = colorActive

    op = colUnLabel.operator("pose.aar_unlabel_bone", text="Unlabel", icon="REMOVE")
    op.aar_group = "AAR_" + name
    

def labelComboLayout(colName, colLabel, colUnLabel, name, colorsNormal, colorSelect, colorActive):
    colName.label(text=name + ":")
    
    row = colLabel.row()
    op = row.operator("pose.aar_label_bone", text="Label Origin", icon="TRACKING_BACKWARDS_SINGLE")
    op.aar_group = "AAR_" + name + "_Origin"
    op.aar_colorNormal = colorsNormal[0]
    op.aar_colorSelect = colorSelect
    op.aar_colorActive = colorActive

    op = row.operator("pose.aar_label_bone", text=" Label Extremity", icon="TRACKING_FORWARDS_SINGLE")
    op.aar_group = "AAR_" + name + "_Final"
    op.aar_colorNormal = colorsNormal[1]
    op.aar_colorSelect = colorSelect
    op.aar_colorActive = colorActive
    
    op = colUnLabel.operator("pose.aar_unlabel_bones_all", text="Unlabel", icon="REMOVE")
    groupOrigin = op.aar_groups.add()
    groupOrigin.groupName = "AAR_" + name + "_Origin"
    groupFinal = op.aar_groups.add()
    groupFinal.groupName = "AAR_" + name + "_Final"
    

def addGroupToOperator(groupName, opAuto, opAll):
    group_auto = opAuto.aar_groups.add()
    group_auto.groupName = groupName
    group_uAll = opAll.aar_groups.add()
    group_uAll.groupName = groupName


class AAR_PT_Panel(Panel):
    #bl_idname = "ANIMATION_PT_Retargetter"
    bl_label = "Retargetter"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "data"
    bl_category = "Animation"
        

    @classmethod
    def poll(cls, context):
        return ((context.object is not None) & (context.object.type == "ARMATURE"))   
    


    def draw(self, context):
        label_name_single = ["Base", "Body", "Head", "Neck"]
        label_name_combo = ["Arm", "Leg", "Wing", "Tail"]
        label_normal_single = [[1,0.4,0.3],[1,0.8,0.15],[1,0,0.4],[1,0.6,0.8]]
        label_normal_combo = [[[0.5,0.8,1],[0,0.8,1]],[[0.5,0.6,1],[0,0.2,1]],[[0.7,1,0.8],[0,1,0.3]],[[0.8,0.5,1],[0.6,0,1]]]
        label_select = [0.75,0.75,0.75]
        label_active = [1,1,1]
        
        
        layout = self.layout
        layout.label(text="Source")
        row = layout.row()
        row.prop(context.object.data, "aar_source", text="")
        row.operator("pose.aar_check_source_labels", text="Check Source Labels", icon="CHECKMARK")
        
        
        #########################################################
        
        
        layout.separator()
        layout.label(text="Actions")
        box = layout.box()
        for act in context.object.data.aar_actionsToCopy:
            if act.actionProp is None:
                continue
            subBox = box.box()
            actionLayout(subBox, act.actionProp)
            
        row = layout.row()
        col = row.column()
        #col.separator()
        col.prop(context.object.data, "aar_actionSelected", text="")
        col = row.column()
        col.operator("pose.aar_register_action", text="Add Action", icon="ADD")
        col.operator("pose.aar_unregister_actions", text="Clear All", icon="PANEL_CLOSE")
        
        
        #########################################################
        
        
        layout.separator()
        layout.label(text="Label Bones")
        box = layout.box()
        row = box.row()
        
        colName = row.column()
        colLabel = row.column()
        colUnLabel = row.column()
        for i in range(0, len(label_name_single)):
            labelSingleLayout(colName, colLabel, colUnLabel, label_name_single[i], label_normal_single[i], label_select, label_active)
            
        for i in range(0, len(label_name_combo)):
            labelComboLayout(colName, colLabel, colUnLabel, label_name_combo[i], label_normal_combo[i], label_select, label_active)

        
        row = layout.row()
        op_auto = row.operator("pose.aar_auto_label", text="Auto-Label", icon="PRESET")
        op_uAll = row.operator("pose.aar_unlabel_bones_all", text="Unlabel All Groups", icon="PANEL_CLOSE")
        for label in label_name_single:
            addGroupToOperator("AAR_" + label, op_auto, op_uAll)
        for label in label_name_combo:
            addGroupToOperator("AAR_" + label + "_Origin", op_auto, op_uAll)
            addGroupToOperator("AAR_" + label + "_Final", op_auto, op_uAll)
        
        
        
        #########################################################
        
        
        layout.separator()
        layout.separator()
        
        row = layout.row()
        row.label(text="Retarget")
        row.separator()
        row.separator()
        row.separator()
        row.prop(context.scene, "aar_retargetStepByStep", text="Step by step", toggle =1, icon="LONGDISPLAY")
        
        if context.scene.aar_retargetStepByStep:
            col = layout.column()        
            col.operator("pose.aar_reset_checks_links", text="Reset Checks & Links", icon="UNLINKED")
            col.operator("pose.aar_check_labels", text="Check Object Labels", icon="CHECKMARK")
            col.operator("pose.aar_link_armatures", text="Link To Source Armature", icon="RESTRICT_INSTANCED_OFF")
            col.operator("pose.aar_retarget", text="Retarget", icon="IMPORT")
        
        else:
            layout.operator("pose.aar_retarget_full", text="Retarget (Full Process)", icon="IMPORT")
        
        
        

if __name__ == '__main__':
    bpy.utils.register_class(AAR_PT_Panel)