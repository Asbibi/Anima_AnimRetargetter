import bpy
from bpy.types import Operator



class AAR_OT_RegisterAction(Operator):
    bl_idname = "pose.aar_register_action"
    bl_label = "Register Action"
    bl_description = "Register an Action for the retargetting process"
    
    
    

    @classmethod
    def poll(cls, context):
        obj = context.object
        if obj is not None:
            if obj.type == "ARMATURE":
                if obj.data.aar_actionSelected is not None:
                    for act in context.object.data.aar_actionsToCopy:
                        if act.actionProp is obj.data.aar_actionSelected:
                            return False
                    return True
        return False


    def execute(self, context):
        action = context.object.animation_data.action
        newAction = context.object.data.aar_actionsToCopy.add()
        newAction.actionProp = context.object.data.aar_actionSelected #context.object.animation_data.action #context.object.animation_data.action.name #
        context.object.data.aar_actionSelected = None
        
        self.report({'WARNING'}, context.object.data.aar_actionsToCopy[0].actionProp.name)
        return {'FINISHED'}



class AAR_OT_UnregisterAction(Operator):
    bl_idname = "pose.aar_unregister_action"
    bl_label = "Unregister Action"
    bl_description = "Unregister one Action for the retargetting process"
    
    aar_action : bpy.props.StringProperty()
    

    @classmethod
    def poll(cls, context):
        obj = context.object
        if obj is not None:
            if obj.type == "ARMATURE":
                return True
        return False


    def execute(self, context):
        collection = context.object.data.aar_actionsToCopy
        remove = []
        for i in range(0, len(collection)):
            if collection[i].actionProp.name == self.aar_action:
                remove.append(i)
                
        for j in range(0, len(remove)):
                collection.remove(remove[j])
        return {'FINISHED'}



class AAR_OT_UnregisterAllActions(Operator):
    bl_idname = "pose.aar_unregister_actions"
    bl_label = "Unregister Actions"
    bl_description = "Unregister all Actions for the retargetting process"
    

    @classmethod
    def poll(cls, context):
        obj = context.object
        if obj is not None:
            if obj.type == "ARMATURE":
                return True
        return False


    def execute(self, context):
        context.object.data.aar_actionsToCopy.clear()
        return {'FINISHED'}





if __name__ == '__main__':
    bpy.utils.register_class(AAR_OT_RegisterAction)
    bpy.utils.register_class(AAR_OT_UnregisterAction)
    bpy.utils.register_class(AAR_OT_UnregisterAllActions)