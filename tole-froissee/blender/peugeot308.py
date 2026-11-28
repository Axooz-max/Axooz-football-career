# Peugeot 308 « HERVÉ » modélisée dans Blender (mêmes outils que decor.py)
# m0 carrosserie · m1 vitres · m2 noir brillant · m3 chrome · m4 phare · m5 LED · m6 feu rouge
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
        nm=me.materials[tri.material_index].name.split('.')[0] if me.materials and tri.material_index<len(me.materials) and me.materials[tri.material_index] else 'm0';mi=MAT.index(nm) if nm in MAT else 0
        for li in tri.loops:
            v=me.vertices[me.loops[li].vertex_index].co;n=me.corner_normals[li].vector
            k=(round(v.x,3),round(v.y,3),round(v.z,3),round(n.x,2),round(n.y,2),round(n.z,2),mi)
            if k not in verts:verts[k]=len(M);PP+=[v.x,v.y,v.z];N+=[n.x,n.y,n.z];M.append(mi)
            I.append(verts[k])
    S=max(abs(x) for x in PP)*1.01
    q=lambda arr,s,fmt,lim:base64.b64encode(struct.pack('<%d%s'%(len(arr),fmt),*[max(-lim,min(lim,int(round(x*s)))) for x in arr])).decode()
    out={'p':q(PP,32767/S,'h',32767),'n':q(N,127,'b',127),'m':base64.b64encode(bytes(M)).decode(),'i':base64.b64encode(struct.pack('<%dH'%len(I),*I)).decode(),'s':round(S,3)}
    print(key,len(M),'sommets',len(I)//3,'triangles');bpy.ops.wm.save_as_mainfile(filepath=OUT+'decor_'+key+'.blend');return out

import math,bmesh,mathutils
R={}
# ===== PEUGEOT 308 (repère du jeu : Y en haut, Z vers l'avant, X sur la largeur) =====
L,W,H=4.37,1.85,1.44
reset()
# profil (z de l'avant vers l'arrière) : (z, y_bas, y_haut_caisse, demi_largeur, y_toit, demi_largeur_toit)
P=[(2.185,.30,.62,.80,None,0),(2.10,.22,.70,.88,None,0),(1.90,.20,.80,.91,None,0),(1.40,.20,.86,.925,None,0),(1.05,.20,.90,.925,1.00,.80),(0.80,.20,.92,.925,1.32,.72),(0.40,.20,.93,.925,1.43,.70),(-0.30,.20,.94,.925,1.44,.70),(-0.95,.20,.95,.92,1.38,.68),(-1.50,.20,.96,.91,1.20,.66),(-1.90,.22,.97,.88,1.05,.62),(-2.12,.30,.95,.82,.98,.58),(-2.185,.40,.90,.76,None,0)]
def ring(z,yb,yt,hw,n=10):
    pts=[]
    for i in range(n+1):
        t=i/n;a=math.pi*t
        # coque arrondie : bas plat, flancs bombés
        y=yb+(yt-yb)*(.5-.5*math.cos(a));x=hw*(.86+.14*math.sin(a))
        pts.append((x,y,z))
    return pts
bm=bmesh.new();rings=[]
for z,yb,yt,hw,yr,hr in P:
    pr=ring(z,yb,yt,hw);full=[(x,y,z) for (x,y,z) in pr]+[(-x,y,z) for (x,y,z) in reversed(pr[1:-1])]
    rings.append([bm.verts.new(v) for v in full])
for a,b in zip(rings,rings[1:]):
    n=len(a)
    for i in range(n):bm.faces.new([a[i],a[(i+1)%n],b[(i+1)%n],b[i]])
bm.faces.new(list(reversed(rings[0])));bm.faces.new(rings[-1])
bmesh.ops.recalc_face_normals(bm,faces=bm.faces[:]);me=bpy.data.meshes.new('caisse');bm.to_mesh(me);bm.free();o=bpy.data.objects.new('caisse',me);bpy.context.collection.objects.link(o);setm(o,0)
# passages de roues (booléen)
for z in (1.34,-1.34):
    bpy.ops.mesh.primitive_cylinder_add(vertices=24,radius=.40,depth=2.4,location=(0,.33,z),rotation=(0,math.pi/2,0));c=bpy.context.active_object
    m=o.modifiers.new('b','BOOLEAN');m.object=c;m.operation='DIFFERENCE';bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier='b');bpy.data.objects.remove(c)
smooth(o)
# habitacle (vitres) en loft
bm=bmesh.new();rs=[]
for z,yb,yt,hw,yr,hr in P:
    if yr is None:continue
    base=yt-.01;pts=[(hw*.97,base,z),(hr,yr,z),(-hr,yr,z),(-hw*.97,base,z)];rs.append([bm.verts.new(v) for v in pts])
for a,b in zip(rs,rs[1:]):
    for i in range(3):bm.faces.new([a[i],a[i+1],b[i+1],b[i]])
bm.faces.new(list(reversed(rs[0])));bm.faces.new(rs[-1])
bmesh.ops.recalc_face_normals(bm,faces=bm.faces[:]);me=bpy.data.meshes.new('vitres');bm.to_mesh(me);bm.free();g=bpy.data.objects.new('vitres',me);bpy.context.collection.objects.link(g);setm(g,1)
# toit noir (par-dessus le haut des vitres)
box((1.28,.03,1.6),(0,1.445,-.25),2)
# montants noirs (A, B, C)
for sx in (-1,1):
    seg((sx*.86,.93,1.05),(sx*.72,1.42,.42),.035,2)
    seg((sx*.80,.94,-.05),(sx*.71,1.43,-.05),.04,2)
    seg((sx*.83,.96,-1.55),(sx*.68,1.40,-.92),.05,2)
# calandre noire sans cadre + prise d'air
box((1.05,.22,.06),(0,.62,2.15),2,bv=.02);box((1.30,.18,.06),(0,.36,2.10),2,bv=.02)
for i in range(4):box((.95,.012,.07),(0,.55+i*.05,2.17),3)
# phares fins et feux de jour en crocs
for sx in (-1,1):
    box((.36,.07,.10),(sx*.58,.80,2.03),4,rot=(0,sx*.25,-sx*.12),bv=.01)
    for k in range(2):box((.025,.20,.04),(sx*(.66-k*.08),.58,2.10),5,rot=(0,0,sx*.3))
# logo
cyl(.07,.07,.02,(0,.66,2.19),3,6,(math.pi/2,0,0))
# feux arrière à 3 griffes dans un bandeau noir
box((1.55,.12,.05),(0,.88,-2.17),2)
for sx in (-1,1):
    for k in range(3):box((.04,.10,.06),(sx*(.48+k*.10),.88,-2.18),6,rot=(0,0,sx*.35))
cyl(.06,.06,.02,(0,.74,-2.20),3,6,(math.pi/2,0,0))
# becquet, diffuseur, rétroviseurs, poignées, bas de caisse
box((1.20,.04,.22),(0,1.37,-1.02),2,rot=(-.2,0,0));box((1.30,.10,.08),(0,.30,-2.16),2)
for sx in (-1,1):
    box((.08,.10,.22),(sx*1.0,1.02,1.0),0,bv=.02);box((.14,.08,.05),(sx*.93,1.0,1.04),2)
    box((.02,.03,.16),(sx*.93,.86,.45),3);box((.02,.03,.16),(sx*.92,.88,-.50),3)
    box((.04,.08,2.2),(sx*.93,.26,0),2)
R['p308']=export('p308')
import json;json.dump(R,open(OUT+'p308.json','w'),separators=(',',':'));print('taille',len(json.dumps(R))//1024,'Ko')
