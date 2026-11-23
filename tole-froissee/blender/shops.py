# Vitrines de boutiques de SMASHR : modélisées et éclairées dans Blender, rendues de face (9,2 m x 2,3 m)
import bpy,math,random
OUT='/tmp/claude-0/-home-user-Axooz-football-career/43582ba6-8900-5dca-9b3b-7b12d55a9676/scratchpad/blender/'
def reset():bpy.ops.wm.read_factory_settings(use_empty=True)
def mat(name,col,rough=.6,metal=0.,emit=0.,alpha=1.):
    m=bpy.data.materials.new(name);m.use_nodes=True;b=m.node_tree.nodes['Principled BSDF'];b.inputs['Base Color'].default_value=col;b.inputs['Roughness'].default_value=rough;b.inputs['Metallic'].default_value=metal
    if emit:b.inputs['Emission Color'].default_value=col;b.inputs['Emission Strength'].default_value=emit
    if alpha<1:b.inputs['Alpha'].default_value=alpha;b.inputs['Transmission Weight'].default_value=.9
    return m
def box(s,loc,m):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.active_object;o.scale=s;bpy.ops.object.transform_apply(scale=True);o.data.materials.append(m);return o
def cyl(r,d,loc,m,rot=(0,0,0)):
    bpy.ops.mesh.primitive_cylinder_add(radius=r,depth=d,location=loc,rotation=rot);o=bpy.context.active_object;o.data.materials.append(m);return o
W,H=9.2,2.3
def shop(kind,seed):
    reset();rnd=random.Random(seed)
    P={'cafe':((.55,.36,.22,1),(1,.82,.55,1)),'pain':((.85,.68,.45,1),(1,.88,.6,1)),'phar':((.92,.95,.93,1),(.85,1,.9,1)),'mode':((.25,.25,.28,1),(1,.95,.9,1))}[kind]
    back=mat('back',P[0],.8,0,.6);light=mat('light',P[1],.3,0,3.5);frame=mat('frame',(.12,.12,.13,1),.4,.7);kick=mat('kick',(.2,.2,.22,1),.6);glass=mat('glass',(.75,.85,.9,1),.02,0,0,.15);floor=mat('floor',(.6,.58,.55,1),.7)
    box((W,.2,H),(W/2,3.2,H/2),back);box((W,3.2,.1),(W/2,1.6,0),floor);box((W,3.2,.1),(W/2,1.6,H),light)
    for i in range(6):box((.5,.08,.06),(1+i*1.4,1.2,H-.08),light)
    cols=[(1,.3,.3,1),(.3,.6,1,1),(1,.85,.2,1),(.3,.85,.4,1),(.9,.5,.9,1),(1,.6,.2,1)]
    if kind in('cafe','pain'):
        for i in range(4):
            x=.9+i*1.7;cyl(.35,.04,(x,1.6,.75),mat('t%d'%i,(.35,.22,.12,1)),(0,0,0));cyl(.04,.7,(x,1.6,.38),frame)
        for i in range(10):box((.35,.25,.18),(.6+i*.75,2.9,1.2+(i%2)*.35),mat('p%d'%i,(.85,.6,.3,1) if kind=='pain' else (.25,.15,.1,1),.8,0,.4))
        box((W-2.5,.5,.9),((W-2.5)/2+.2,2.7,.45),mat('cnt',(.3,.2,.12,1)))
    elif kind=='phar':
        for r in range(3):
            for i in range(14):box((.35,.25,.3),(.4+i*.55,3.0,.5+r*.55),mat('b%d%d'%(r,i),cols[(i+r)%6],.5,0,.5))
        box((.6,.12,.6),(W-1.6,3.05,H-.6),mat('cross',(.1,.9,.3,1),.4,0,4))
    else:
        for i in range(5):
            x=.8+i*1.5;cyl(.02,1.4,(x,2.2,1.85),frame,(math.pi/2,0,0))
            for k in range(4):box((.35,.05,.9),(x-.3+k*.2,2.2,1.35),mat('c%d%d'%(i,k),cols[(i*2+k)%6],.8,0,.3))
    box((W,.15,H),(W/2,-.02,H/2),glass)
    for x in [0,2.4,4.8,7.2,W]:box((.1,.18,H),(x,-.05,H/2),frame)
    box((W,.2,.12),(W/2,-.05,H-.06),frame);box((W,.2,.35),(W/2,-.05,.175),kick)
    box((1.5,.12,2.1),(W-1.2,-.06,1.05),mat('door',(.15,.15,.16,1),.4,.5))
    sc=bpy.context.scene;bpy.ops.object.camera_add(location=(W/2,-20,H/2),rotation=(math.pi/2,0,0));cam=bpy.context.active_object;cam.data.type='ORTHO';cam.data.ortho_scale=W;sc.camera=cam;sc.render.resolution_x=1024;sc.render.resolution_y=256
    bpy.ops.object.light_add(type='SUN',rotation=(math.radians(55),math.radians(-20),0));bpy.context.active_object.data.energy=1.8
    w=bpy.data.worlds.new('w');sc.world=w;w.use_nodes=True;w.node_tree.nodes['Background'].inputs[0].default_value=(.6,.68,.8,1);w.node_tree.nodes['Background'].inputs[1].default_value=.6
    sc.render.engine='CYCLES';sc.cycles.device='CPU';sc.cycles.samples=40;sc.cycles.use_denoising=False;sc.view_settings.view_transform='Standard';sc.render.image_settings.file_format='PNG'
    sc.render.filepath=OUT+'shop_'+kind+'.png';bpy.ops.render.render(write_still=True);print('rendu',kind)
for i,k in enumerate(['cafe','pain','phar','mode']):shop(k,i)
