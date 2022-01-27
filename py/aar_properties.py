import bpy




def aar_prop_poll_armature(self, object):
    return object.type == 'ARMATURE'

def aar_prop_poll_action(self, object):
    return True #object.type == 'ARMATURE'




def AAR_RegisterProps():
    bpy.types.Armature.aar_source = bpy.props.PointerProperty(type=bpy.types.Object, poll=aar_prop_poll_armature)
    bpy.types.Armature.aar_labelChecked = bpy.props.BoolProperty(default=False)
    bpy.types.Armature.aar_actionSelected = bpy.props.PointerProperty(type=bpy.types.Action)
    bpy.types.Armature.aar_actionsToCopy = bpy.props.CollectionProperty(type=AAR_PROP_ActionListProperty)
    bpy.types.Action.aar_useGround = bpy.props.BoolProperty()
    bpy.types.Action.aar_loopIdle = bpy.props.BoolProperty(default=True)
    
def AAR_DelProps():
    del bpy.types.Armature.aar_source
    del bpy.types.Armature.aar_actionSelected
    del bpy.types.Armature.aar_actionsToCopy
    del bpy.types.Action.aar_useGround
    del bpy.types.Action.aar_loopIdle




class AAR_PROP_ActionListProperty(bpy.types.PropertyGroup):
    actionProp : bpy.props.PointerProperty(type=bpy.types.Action) #, poll=aar_prop_poll_action)
    
    
    
if __name__ == '__main__':
    bpy.utils.register_class(AAR_PROP_ActionListProperty)