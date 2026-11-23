# Façades d'immeubles de SMASHR : modélisées et éclairées dans Blender, puis « cuites » en textures
# (rendu orthographique de face avec soleil et ciel : les creux, appuis et corniches gardent leurs ombres)
import bpy,math,random
OUT='/tmp/claude-0/-home-user-Axooz-football-career/43582ba6-8900-5dca-9b3b-7b12d55a9676/scratchpad/blender/'
def reset():bpy.ops.wm.read_factory_settings(use_empty=True)
def mat(name,col,rough=.8,metal=0.,noise=0.):
    m=bpy.data.materials.new(name);m.use_nodes=True;nt=m.node_tree;b=nt.nodes['Principled BSDF'];b.inputs['Base Color'].default_value=col;b.inputs['Roughness'].default_value=rough;b.inputs['Metallic'].default_value=metal
    if noise>0:
        n=nt.nodes.new('ShaderNodeTexNoise');n.inputs['Scale'].default_value=18;n.inputs['Detail'].default_value=8
        mx=nt.nodes.new('ShaderNodeMixRGB');mx.blend_type='MULTIPLY';mx.inputs['Fac'].default_value=noise;mx.inputs['Color1'].default_value=col
        ramp=nt.nodes.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].color=(.82,.82,.82,1);ramp.color_ramp.elements[1].color=(1,1,1,1)
        nt.links.new(n.outputs['Fac'],ramp.inputs['Fac']);nt.links.new(ramp.outputs['Color'],mx.inputs['Color2']);nt.links.new(mx.outputs['Color'],b.inputs['Base Color'])
    return m
def box(s,loc,m):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.active_object;o.scale=s;bpy.ops.object.transform_apply(scale=True);o.data.materials.append(m);return o
def camlight(W,H,res):
    sc=bpy.context.scene;bpy.ops.object.camera_add(location=(W/2,-30,H/2),rotation=(math.pi/2,0,0));cam=bpy.context.active_object;cam.data.type='ORTHO';cam.data.ortho_scale=max(W,H);sc.camera=cam
    sc.render.resolution_x=res if W>=H else int(res*W/H);sc.render.resolution_y=res if H>=W else int(res*H/W)
    bpy.ops.object.light_add(type='SUN',rotation=(math.radians(52),math.radians(-28),math.radians(-18)));s=bpy.context.active_object;s.data.energy=2.1;s.data.angle=math.radians(6)
    w=bpy.data.worlds.new('w');sc.world=w;w.use_nodes=True;w.node_tree.nodes['Background'].inputs[0].default_value=(.62,.72,.88,1);w.node_tree.nodes['Background'].inputs[1].default_value=.55
    sc.render.engine='CYCLES';sc.cycles.device='CPU';sc.cycles.samples=48;sc.cycles.use_denoising=False;sc.view_settings.view_transform='Standard';sc.render.image_settings.file_format='JPEG';sc.render.image_settings.quality=86
def render(name):bpy.context.scene.render.filepath=OUT+name;bpy.ops.render.render(write_still=True);print('rendu',name)
# ===== 1. façade crépie : tuile de 16,8 m x 14,4 m = 4 travées x 4 étages (même grille que l'éclairage de nuit) =====
reset();W,H=16.8,14.4
wall=mat('wall',(.9,.88,.84,1),.9,0,.6);trim=mat('trim',(.98,.98,.97,1),.6);glass=mat('glass',(.10,.13,.17,1),.08,.6);frame=mat('frame',(.85,.86,.87,1),.5);sill=mat('sill',(.78,.77,.74,1),.85);shade=mat('shade',(.55,.56,.58,1),.7)
box((W,.2,H),(W/2,.6,H/2),shade)
for j in range(4):
    for i in range(4):
        cx0,cy0=4.2*i,H-3.6*(j+1);x0=cx0+.79;wx,wy=2.6,2.0;yb=cy0+3.6-.79-wy
        box((.79,.32,3.6),(cx0+.395,.16,cy0+1.8),wall);box((.81,.32,3.6),(x0+wx+.405,.16,cy0+1.8),wall)
        box((wx,.32,.79),(x0+wx/2,.16,yb+wy+.395),wall);box((wx,.32,yb-cy0),(x0+wx/2,.16,cy0+(yb-cy0)/2),wall)
        box((wx,.05,wy),(x0+wx/2,.36,yb+wy/2),glass)
        for (sx,sy,cx,cy) in [(wx,.1,x0+wx/2,yb+wy-.05),(wx,.1,x0+wx/2,yb+.05),(.1,wy,x0+.05,yb+wy/2),(.1,wy,x0+wx-.05,yb+wy/2),(.07,wy,x0+wx/2,yb+wy/2)]:box((sx,.06,sy),(cx,.31,cy),frame)
        box((wx+.4,.34,.1),(x0+wx/2,-.02,yb-.05),sill)
        if (i+j)%3==0:box((wx+.1,.6,.08),(x0+wx/2,-.1,yb+wy+.25),shade)
    box((W,.22,.24),(W/2,-.06,cy0+.12),trim)
for i in range(5):box((.3,.3,H),(4.2*i,-.05,H/2),trim)
camlight(W,H,512);render('facade_plaster.jpg')
# ===== 2. mur-rideau en verre : tuile de 10 m x 10 m =====
reset();W,H=10,10
gl=mat('gl',(.22,.32,.42,1),.05,.85);mul=mat('mul',(.62,.65,.68,1),.35,.8);band=mat('band',(.30,.33,.36,1),.4,.6)
box((W,.4,H),(W/2,.2,H/2),gl)
for i in range(5):box((.14,.22,H),(i*2.5,-.05,H/2),mul)
for j in range(3):box((W,.22,.5 if j%2==0 else .14),(W/2,-.05,j*3.333),band if j%2==0 else mul)
camlight(W,H,512);render('facade_glass.jpg')
