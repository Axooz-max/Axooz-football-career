# Génère des roues 3D (pneu + 5 jantes) avec Blender et les exporte en données compactes pour le jeu
import bpy, bmesh, math, json, base64, struct
from mathutils import Vector, Matrix
MAT=['rim','dark','chrome','tire','tread']
def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)
def mat(i):
    m=bpy.data.materials.get(MAT[i]) or bpy.data.materials.new(MAT[i]);return m
def setmat(obj,i):
    obj.data.materials.clear();obj.data.materials.append(mat(i))
def spin_profile(pts,segs,name,mi,axis='X'):
    # profil (r, x) tourné autour de l'axe X
    bm=bmesh.new();verts=[]
    for k in range(segs):
        a=2*math.pi*k/segs;ring=[]
        for (r,x) in pts: ring.append(bm.verts.new((x,r*math.cos(a),r*math.sin(a))))
        verts.append(ring)
    for k in range(segs):
        A=verts[k];B=verts[(k+1)%segs]
        for j in range(len(pts)-1): bm.faces.new((A[j],B[j],B[j+1],A[j+1]))
    me=bpy.data.meshes.new(name);bm.to_mesh(me);bm.free();ob=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(ob);setmat(ob,mi)
    for p in me.polygons:p.use_smooth=True
    return ob
def box(name,size,loc,rot,mi,bev=0):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc,rotation=rot);ob=bpy.context.active_object;ob.name=name;ob.scale=size;bpy.ops.object.transform_apply(scale=True)
    if bev>0:
        m=ob.modifiers.new('b','BEVEL');m.width=bev;m.segments=2;bpy.ops.object.modifier_apply(modifier='b')
    setmat(ob,mi);return ob
def cyl(name,r,depth,loc,mi,verts=16,rot=(0,math.pi/2,0)):
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts,radius=r,depth=depth,location=loc,rotation=rot);ob=bpy.context.active_object;ob.name=name;setmat(ob,mi)
    for p in ob.data.polygons:p.use_smooth=True
    return ob
def radial(obj,n):
    out=[obj]
    for k in range(1,n):
        c=obj.copy();c.data=obj.data.copy();bpy.context.collection.objects.link(c);c.rotation_euler[0]=obj.rotation_euler[0]+2*math.pi*k/n;out.append(c)
    return out
def join(objs,name):
    bpy.ops.object.select_all(action='DESELECT')
    for o in objs:o.select_set(True)
    bpy.context.view_layer.objects.active=objs[0];bpy.ops.object.transform_apply(location=True,rotation=True,scale=True);bpy.ops.object.join();ob=bpy.context.active_object;ob.name=name;return ob
# ---------- PNEU (rayon 1, largeur 1, axe X)
def tire():
    reset()
    prof=[(.62,-.5),(.78,-.53),(.9,-.52),(.97,-.46),(1.0,-.36),(1.0,.36),(.97,.46),(.9,.52),(.78,.53),(.62,.5)]
    t=spin_profile(prof,48,'tire',3)
    parts=[t]
    # pavés de la bande de roulement
    for side in (-1,1):
        b=box('blk',(0.3,0.12,0.025),(side*.2,0,1.004),(0,0,0),4,0)
        parts+=radial(b,36)
    g=box('grv',(.9,0.015,0.02),(0,0,1.002),(0,0,0),4,0);parts+=radial(g,36)
    return join(parts,'tire')
# ---------- JANTES (rayon .64, largeur .82)
def rim_base(parts):
    parts.append(spin_profile([(.6,-.41),(.64,-.38),(.64,.38),(.6,.41)],40,'barrel',1))        # fût
    parts.append(spin_profile([(.56,.41),(.645,.41),(.66,.43),(.6,.45)],40,'lip',0))             # rebord extérieur
    parts.append(spin_profile([(.16,.40),(.2,.39),(.2,.33)],20,'hubring',0))
    parts.append(cyl('cap',.11,.06,(.43,0,0),2,20))
    for k in range(5):
        a=2*math.pi*k/5;parts.append(cyl('nut',.022,.05,(.42,.14*math.cos(a),.14*math.sin(a)),2,8))
def rim_five():
    reset();parts=[];rim_base(parts)
    for k in range(5):
        a=2*math.pi*k/5
        s=box('sp',(.08,.11,.40),(.37,0,.37),(0,0,0),0,.015);s.rotation_euler=(a,0,0);parts.append(s)
    return join(parts,'five')
def rim_bbs():
    reset();parts=[];rim_base(parts)
    for k in range(10):
        a=2*math.pi*k/10
        for t in (.16,-.16):
            s=box('sp',(.045,.035,.44),(.36,0,.36),(0,0,0),0,.006);s.rotation_euler=(a+t,0,0);parts.append(s)
    parts.append(spin_profile([(.56,.38),(.6,.38),(.6,.33)],40,'ring',0))
    return join(parts,'bbs')
def rim_turbine():
    reset();parts=[];rim_base(parts)
    parts.append(spin_profile([(.2,.36),(.58,.34),(.58,.30),(.2,.31)],40,'disc',0))
    for k in range(14):
        a=2*math.pi*k/14;s=box('fin',(.05,.06,.34),(.37,0,.37),(0,0,0),1,.01);s.rotation_euler=(a,0,0);parts.append(s)
    return join(parts,'turbine')
def rim_steel():
    reset();parts=[];rim_base(parts)
    parts.append(spin_profile([(.18,.34),(.4,.36),(.5,.33),(.6,.36)],40,'dish',0))
    for k in range(8):
        a=2*math.pi*k/8;parts.append(cyl('hole',.05,.04,(.37,.32*math.cos(a),.32*math.sin(a)),1,10))
    parts.append(spin_profile([(.0,.44),(.22,.42),(.26,.37)],24,'hubcap',2))
    return join(parts,'steel')
def rim_multi():
    reset();parts=[];rim_base(parts)
    for k in range(7):
        a=2*math.pi*k/7
        for t in (.09,-.09):
            s=box('sp',(.06,.055,.40),(.37,0,.37),(0,0,0),0,.01);s.rotation_euler=(a+t,0,0);parts.append(s)
    return join(parts,'multi')
def export(ob):
    bpy.context.view_layer.objects.active=ob;ob.select_set(True)
    me=ob.data;me.calc_loop_triangles()
    verts={};P=[];N=[];M=[];I=[]
    for tri in me.loop_triangles:
        mi=MAT.index(me.materials[tri.material_index].name) if me.materials else 0
        for li in tri.loops:
            v=me.vertices[me.loops[li].vertex_index].co;n=me.corner_normals[li].vector if hasattr(me,'corner_normals') else me.loops[li].normal
            key=(round(v.x,4),round(v.y,4),round(v.z,4),round(n.x,2),round(n.y,2),round(n.z,2),mi)
            if key not in verts:
                verts[key]=len(P)//3;P+= [v.x,v.y,v.z];N+=[n.x,n.y,n.z];M.append(mi)
            I.append(verts[key])
    q=lambda arr,s,fmt:base64.b64encode(struct.pack('<%d%s'%(len(arr),fmt),*[max(-32767 if fmt=='h' else -127,min(32767 if fmt=='h' else 127,int(round(x*s)))) for x in arr])).decode()
    return {'p':q(P,32767/1.2,'h'),'n':q(N,127,'b'),'m':base64.b64encode(bytes(M)).decode(),'i':base64.b64encode(struct.pack('<%dH'%len(I),*I)).decode(),'v':len(M),'t':len(I)//3}
out={}
for name,fn in [('tire',tire),('five',rim_five),('bbs',rim_bbs),('turbine',rim_turbine),('steel',rim_steel),('multi',rim_multi)]:
    ob=fn();out[name]=export(ob);print(name,out[name]['v'],'sommets',out[name]['t'],'triangles')
    if name=='five':
        bpy.ops.wm.save_as_mainfile(filepath='/tmp/claude-0/-home-user-Axooz-football-career/43582ba6-8900-5dca-9b3b-7b12d55a9676/scratchpad/blender/jante_five.blend')
json.dump(out,open('wheels.json','w'))
print('taille',len(json.dumps(out))//1024,'Ko')
