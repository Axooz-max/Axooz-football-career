import bpy,math,sys
OUT='/tmp/claude-0/-home-user-Axooz-football-career/43582ba6-8900-5dca-9b3b-7b12d55a9676/scratchpad/blender/'
cols={'body':(0.92,0.93,0.95,1),'livery':(0.75,0.08,0.06,1),'window':(0.03,0.05,0.09,1),'engine':(0.6,0.62,0.66,1),'dark':(0.05,0.05,0.06,1),'light':(0.1,0.9,0.2,1)}
for key,dist in [('liner',38),('jet',20),('prop',11),('stunt',10),('heli',10)]:
    bpy.ops.wm.open_mainfile(filepath=OUT+key+'.blend')
    for m in bpy.data.materials:
        m.use_nodes=True;b=m.node_tree.nodes.get('Principled BSDF');b.inputs['Base Color'].default_value=cols[m.name];b.inputs['Roughness'].default_value=.35
    ob=bpy.data.objects[0];ob.rotation_euler=(math.pi/2,0,0)
    sc=bpy.context.scene;bpy.ops.object.empty_add(location=(0,0,0));t=bpy.context.active_object
    bpy.ops.object.camera_add(location=(dist*.8,-dist*.95,dist*.45));cam=bpy.context.active_object;c=cam.constraints.new('TRACK_TO');c.target=t;c.track_axis='TRACK_NEGATIVE_Z';c.up_axis='UP_Y';sc.camera=cam;cam.data.lens=35
    bpy.ops.object.light_add(type='SUN',location=(0,20,0),rotation=(math.radians(40),math.radians(20),0));bpy.context.active_object.data.energy=4;sc.render.engine='CYCLES';sc.cycles.device='CPU';sc.cycles.samples=10
    w=bpy.data.worlds.new('w');sc.world=w;w.use_nodes=True;w.node_tree.nodes['Background'].inputs[0].default_value=(0.5,0.65,0.85,1);sc.render.resolution_x=640;sc.render.resolution_y=360;sc.render.filepath=OUT+'r_'+key+'.png';bpy.ops.render.render(write_still=True)
print('ok')
