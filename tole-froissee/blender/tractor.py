# Tracteur de SMASHR modélisé dans Blender (mêmes outils que decor.py)
import bpy,bmesh,math,json,base64,struct,random
MAT=['m0','m1','m2','m3','m4','m5','m6','m7']
OUT='/tmp/claude-0/-home-user-Axooz-football-career/43582ba6-8900-5dca-9b3b-7b12d55a9676/scratchpad/blender/'
UP=(-math.pi/2,0,0)
def reset():bpy.ops.wm.read_factory_settings(use_empty=True)
def mat(i):return bpy.data.materials.get(MAT[i]) or bpy.data.materials.new(MAT[i])
def setm(o,i):o.data.materials.clear();o.data.materials.append(mat(i))
def smooth(o,on=True):
    for p in o.data.polygons:p.use_smooth=on
def bevel(o,w=.03,seg=1):
    m=o.modifiers.new('b','BEVEL');m.width=w;m.segments=seg;m.limit_method='ANGLE'
    bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier='b')
def box(s,loc,mi,rot=(0,0,0),bv=0):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc,rotation=rot);o=bpy.context.active_object;o.scale=s;bpy.ops.object.transform_apply(scale=True,rotation=True,location=False);setm(o,mi)
    if bv:bevel(o,bv)
    return o
def cyl(r1,r2,d,loc,mi,v=10,rot=UP,sm=True):
    bpy.ops.mesh.primitive_cone_add(vertices=v,radius1=r1,radius2=r2,depth=d,location=loc,rotation=rot);o=bpy.context.active_object;setm(o,mi);smooth(o,sm);return o
def ico(r,loc,mi,sub=1,sc=(1,1,1),jit=.12,seed=0):
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=sub,radius=r,location=loc);o=bpy.context.active_object;rnd=random.Random(seed)
    for v in o.data.vertices:k=1+rnd.uniform(-jit,jit);v.co=(v.co.x*k*sc[0],v.co.y*k*sc[1],v.co.z*k*sc[2])
    setm(o,mi);smooth(o,False);return o
def sph(r,loc,mi,sc=(1,1,1),seg=12):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=seg,ring_count=max(6,seg//2),radius=r,location=loc);o=bpy.context.active_object;o.scale=sc;bpy.ops.object.transform_apply(scale=True);setm(o,mi);smooth(o);return o
def poly(verts,faces,mi,name='p'):
    bm=bmesh.new();V=[bm.verts.new(v) for v in verts];V2=[bm.verts.new(v) for v in verts]
    for f in faces:bm.faces.new([V[i] for i in f]);bm.faces.new([V2[i] for i in reversed(f)])
    me=bpy.data.meshes.new(name);bm.normal_update();bm.to_mesh(me);bm.free();o=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(o);setm(o,mi);return o
def seg(a,b,r,mi,v=8):
    """cylindre entre deux points"""
    ax,ay,az=a;bx,by,bz=b;dx,dy,dz=bx-ax,by-ay,bz-az;L=math.sqrt(dx*dx+dy*dy+dz*dz)
    bpy.ops.mesh.primitive_cylinder_add(vertices=v,radius=r,depth=L,location=((ax+bx)/2,(ay+by)/2,(az+bz)/2));o=bpy.context.active_object
    import mathutils;q=mathutils.Vector((0,0,1)).rotation_difference(mathutils.Vector((dx,dy,dz)).normalized());o.rotation_mode='QUATERNION';o.rotation_quaternion=q;bpy.ops.object.transform_apply(rotation=True);setm(o,mi);smooth(o);return o
def export(key):
    bpy.ops.object.select_all(action='DESELECT')
    for o in bpy.data.objects:o.select_set(True)
    bpy.context.view_layer.objects.active=bpy.data.objects[0];bpy.ops.object.transform_apply(location=True,rotation=True,scale=True);bpy.ops.object.join();ob=bpy.context.active_object
    me=ob.data;me.calc_loop_triangles();verts={};PP=[];N=[];M=[];I=[]
    for tri in me.loop_triangles:
        mi=MAT.index(me.materials[tri.material_index].name.split('.')[0])
        for li in tri.loops:
            v=me.vertices[me.loops[li].vertex_index].co;n=me.corner_normals[li].vector
            k=(round(v.x,3),round(v.y,3),round(v.z,3),round(n.x,2),round(n.y,2),round(n.z,2),mi)
            if k not in verts:verts[k]=len(M);PP+=[v.x,v.y,v.z];N+=[n.x,n.y,n.z];M.append(mi)
            I.append(verts[k])
    S=max(abs(x) for x in PP)*1.01
    q=lambda arr,s,fmt,lim:base64.b64encode(struct.pack('<%d%s'%(len(arr),fmt),*[max(-lim,min(lim,int(round(x*s)))) for x in arr])).decode()
    out={'p':q(PP,32767/S,'h',32767),'n':q(N,127,'b',127),'m':base64.b64encode(bytes(M)).decode(),'i':base64.b64encode(struct.pack('<%dH'%len(I),*I)).decode(),'s':round(S,3)}
    print(key,len(M),'sommets',len(I)//3,'triangles');bpy.ops.wm.save_as_mainfile(filepath=OUT+'decor_'+key+'.blend');return out

import math
R={}
def arc(cx,cy,cz,r,w,th,mi,a0=15,a1=165,n=7):
    for i in range(n):
        a=math.radians(a0+(a1-a0)*(i+.5)/n);L=2*r*math.sin(math.radians((a1-a0)/n/2))*1.08
        box((w,th,L),(cx,cy+r*math.sin(a),cz+r*math.cos(a)),mi,rot=(-(a+math.pi/2),0,0))
# ===== TRACTEUR (repère du jeu : Y en haut, Z vers l'avant ; roues exportées à part) =====
reset()
box((.72,.34,2.7),(0,.78,.3),1)
box((.78,.72,1.5),(0,1.17,1.05),0,bv=.06)
box((.68,.56,.05),(0,1.13,1.81),1)
for i in range(6):box((.6,.025,.03),(0,.92+i*.08,1.84),1)
for sx in (-1,1):cyl(.08,.08,.06,(sx*.25,1.32,1.85),5,12,(0,0,0));cyl(.11,.11,.03,(sx*.25,1.32,1.83),1,12,(0,0,0))
box((1.5,.12,.16),(0,.45,1.15),1)
box((.62,.36,.32),(0,.86,1.98),1,bv=.03)
box((1.34,.12,1.25),(0,1.16,-.75),1)
for sx in (-1,1):
    seg((sx*.62,1.2,-.18),(sx*.6,2.68,-.24),.035,1);seg((sx*.62,1.2,-1.32),(sx*.6,2.68,-1.3),.035,1)
box((1.48,.08,1.4),(0,2.72,-.76),0,bv=.02)
box((1.18,1.32,.03),(0,1.96,-.21),4);box((1.18,1.1,.03),(0,2.05,-1.31),4)
for sx in (-1,1):box((.03,1.0,1.02),(sx*.61,2.08,-.76),4)
box((.5,.12,.46),(0,1.46,-.95),7);box((.5,.52,.1),(0,1.72,-1.18),7)
seg((0,1.2,-.25),(0,1.82,-.48),.025,1);cyl(.19,.19,.035,(0,1.86,-.5),1,16,(math.radians(-55),0,0))
seg((.3,1.5,1.45),(.3,2.95,1.45),.055,7,10);cyl(.075,.06,.12,(.3,3.0,1.45),7,10,(0,0,0))
for sx in (-1,1):
    arc(sx*.82,.78,-.9,.9,.52,.06,0)
    box((.22,.1,.08),(sx*.82,1.0,-1.82),6)
    arc(sx*.7,.45,1.15,.55,.34,.04,0,25,155,5)
box((.3,.14,.3),(0,.7,-1.86),1)
for sx in (-1,1):box((.08,.08,.6),(sx*.55,2.78,.05),5)
R['tractor']=export('tractor')
def wheel(r,w,key,lugs):
    reset();cyl(r,r,w,(0,0,0),2,28,(0,math.pi/2,0));cyl(r*.58,r*.58,w+.02,(0,0,0),3,20,(0,math.pi/2,0));cyl(r*.18,r*.18,w+.06,(0,0,0),1,10,(0,math.pi/2,0))
    for i in range(lugs):
        a=2*math.pi*i/lugs
        for sd in (-1,1):box((w*.42,r*.09,r*.16),(sd*w*.22,r*math.sin(a)*1.02,r*math.cos(a)*1.02),2,rot=(math.pi/2-a,0,sd*.45))
    R[key]=export(key)
wheel(.78,.46,'twb',18);wheel(.45,.3,'twf',14)
import json;json.dump(R,open(OUT+'tractor.json','w'),separators=(',',':'));print('taille',len(json.dumps(R))//1024,'Ko')
