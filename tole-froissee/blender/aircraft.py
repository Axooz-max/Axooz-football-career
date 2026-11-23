# Modèles d'avions et d'hélicoptère pour SMASHR, construits avec Blender et exportés en données compactes
import bpy,bmesh,math,json,base64,struct,sys
MAT=['body','livery','window','engine','dark','light']
OUT='/tmp/claude-0/-home-user-Axooz-football-career/43582ba6-8900-5dca-9b3b-7b12d55a9676/scratchpad/blender/'
def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)
def mat(i):
    m=bpy.data.materials.get(MAT[i]) or bpy.data.materials.new(MAT[i]);return m
def setm(o,i):o.data.materials.clear();o.data.materials.append(mat(i))
def link(me,name,mi):
    o=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(o);setm(o,mi);return o
def lathe(prof,segs,name,mi,yc=None,sy=1.0,sx=1.0):
    bm=bmesh.new();rings=[]
    for (z,r) in prof:
        c=yc(z) if yc else 0;rings.append([bm.verts.new((sx*r*math.cos(2*math.pi*k/segs),c+sy*r*math.sin(2*math.pi*k/segs),z)) for k in range(segs)])
    for j in range(len(rings)-1):
        for k in range(segs):bm.faces.new((rings[j][k],rings[j][(k+1)%segs],rings[j+1][(k+1)%segs],rings[j+1][k]))
    if prof[0][1]>0.01:bm.faces.new(list(reversed(rings[0])))
    if prof[-1][1]>0.01:bm.faces.new(rings[-1])
    me=bpy.data.meshes.new(name);bm.to_mesh(me);bm.free();o=link(me,name,mi)
    for p in me.polygons:p.use_smooth=True
    return o
def wing(name,root,tip,span,sweep,thick,x0,y0,z0,mi,dih=0.0,side=1,vert=False):
    bm=bmesh.new();c=[]
    for (zc,ch,s) in [(z0,root,0),(z0-sweep,tip,span)]:
        t=thick*ch;sec=[(ch*.5,0),(ch*.25,t*.55),(-ch*.1,t*.45),(-ch*.5,t*.05),(-ch*.5,-t*.05),(-ch*.1,-t*.3),(ch*.25,-t*.35)]
        if vert:c.append([bm.verts.new((x0+tt,y0+s,zc+zz)) for (zz,tt) in sec])
        else:c.append([bm.verts.new((x0+side*s,y0+s*dih+tt,zc+zz)) for (zz,tt) in sec])
    A,B=c;n=len(A)
    for k in range(n):bm.faces.new((A[k],A[(k+1)%n],B[(k+1)%n],B[k]) if side>0 or vert else (B[k],B[(k+1)%n],A[(k+1)%n],A[k]))
    bm.faces.new(list(reversed(A)) if side>0 or vert else A);bm.faces.new(B if side>0 or vert else list(reversed(B)))
    me=bpy.data.meshes.new(name);bm.to_mesh(me);bm.free();o=link(me,name,mi)
    for p in me.polygons:p.use_smooth=False
    return o
def cyl(name,r,d,loc,mi,v=16,rot=(0,0,0),r2=None):
    if r2 is None:bpy.ops.mesh.primitive_cylinder_add(vertices=v,radius=r,depth=d,location=loc,rotation=rot)
    else:bpy.ops.mesh.primitive_cone_add(vertices=v,radius1=r,radius2=r2,depth=d,location=loc,rotation=rot)
    o=bpy.context.active_object;o.name=name;setm(o,mi)
    for p in o.data.polygons:p.use_smooth=True
    return o
def box(name,s,loc,mi,rot=(0,0,0)):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc,rotation=rot);o=bpy.context.active_object;o.name=name;o.scale=s;bpy.ops.object.transform_apply(scale=True);setm(o,mi);return o
def sph(name,r,loc,mi,sc=(1,1,1),seg=16):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=seg,ring_count=seg//2,radius=r,location=loc);o=bpy.context.active_object;o.name=name;o.scale=sc;bpy.ops.object.transform_apply(scale=True);setm(o,mi)
    for p in o.data.polygons:p.use_smooth=True
    return o
def export(key):
    bpy.ops.object.select_all(action='DESELECT')
    for o in bpy.data.objects:o.select_set(True)
    bpy.context.view_layer.objects.active=bpy.data.objects[0];bpy.ops.object.transform_apply(location=True,rotation=True,scale=True);bpy.ops.object.join();ob=bpy.context.active_object
    me=ob.data;me.calc_loop_triangles();verts={};PP=[];N=[];M=[];I=[]
    for tri in me.loop_triangles:
        mi=MAT.index(me.materials[tri.material_index].name)
        for li in tri.loops:
            v=me.vertices[me.loops[li].vertex_index].co;n=me.corner_normals[li].vector
            k=(round(v.x,3),round(v.y,3),round(v.z,3),round(n.x,2),round(n.y,2),round(n.z,2),mi)
            if k not in verts:verts[k]=len(M);PP+=[v.x,v.y,v.z];N+=[n.x,n.y,n.z];M.append(mi)
            I.append(verts[k])
    S=max(abs(x) for x in PP)*1.01
    q=lambda arr,s,fmt,lim:base64.b64encode(struct.pack('<%d%s'%(len(arr),fmt),*[max(-lim,min(lim,int(round(x*s)))) for x in arr])).decode()
    out={'p':q(PP,32767/S,'h',32767),'n':q(N,127,'b',127),'m':base64.b64encode(bytes(M)).decode(),'i':base64.b64encode(struct.pack('<%dH'%len(I),*I)).decode(),'s':round(S,3)}
    print(key,len(M),'sommets',len(I)//3,'triangles');bpy.ops.wm.save_as_mainfile(filepath=OUT+key+'.blend');return out
R={}
# ===== AVION DE LIGNE (amélioré) =====
reset()
prof=[(15.3,0),(15.15,.42),(14.7,.9),(13.8,1.3),(12.4,1.56),(10.5,1.66),(-7.5,1.66),(-9.5,1.55),(-11.5,1.22),(-13.2,.82),(-14.6,.42),(-15.3,.12),(-15.5,0)]
lathe(prof,28,'fus',0,yc=lambda z:max(0,(-z-7.5))*.13)
lathe([(11.2,1.675),(-9.5,1.675)],28,'stripe',1,sy=.16)
bpy.data.objects['stripe'].location=(0,-.42,0)
lathe([(14.3,1.0),(13.1,1.38)],28,'cockpitband',2,sy=.22);bpy.data.objects['cockpitband'].location=(0,.55,0)
for k in range(30):
    z=10.2-k*.66
    for sx in (-1,1):box('win',(.05,.3,.22),(sx*1.645,.45,z),2)
for z in (11.3,-8.6):
    for sx in (-1,1):box('door',(.04,1.5,.85),(sx*1.66,.15,z),4)
box('belly',(2.6,.6,7),(0,-1.45,2.4),0)
for sx in (-1,1):
    wing('wing',5.6,1.5,16.5,6.5,.12,sx*1.2,-.75,3.6,0,dih=.09,side=sx)
    wing('winglet',1.5,.6,1.9,1.3,.1,sx*17.6,-.75+16.5*.09,-3.1,1,vert=True)
    cyl('nac',.95,4.2,(sx*5.8,-1.75,4.6),3,24)
    cyl('lip',.97,.25,(sx*5.8,-1.75,6.75),0,24)
    cyl('fan',.78,.05,(sx*5.8,-1.75,6.72),4,24)
    cyl('spin',.25,.5,(sx*5.8,-1.75,6.75),3,12,r2=0)
    cyl('noz',.6,.9,(sx*5.8,-1.75,2.2),4,20,r2=.45)
    box('pyl',(.28,.95,2.6),(sx*5.8,-1.0,4.2),0)
    wing('stab',2.8,1.1,5.8,2.3,.1,sx*.45,1.35,-12.4,0,dih=.06,side=sx)
    cyl('navl',.16,.16,(sx*17.65,-.75+16.5*.09+1.0,-3.4),5 if sx>0 else 1,8,(0,0,math.pi/2))
fin=wing('fin',4.6,1.7,6.8,3.4,.1,0,1.5,-11.3,1,vert=True)
cyl('apu',.22,.6,(0,1.6,-15.6),4,10,(math.pi,0,0),r2=.1)
for (x,z) in [(0,12),(-2.6,1.8),(2.6,1.8)]:
    cyl('leg',.13,1.6,(x,-2.3,z),3,8,(math.pi/2,0,0))
    for dx in ((-.28,.28) if x else (-.2,.2)):cyl('whl',.48,.32,(x+dx,-3.1,z),4,16,(0,math.pi/2,0))
R['liner']=export('liner')
# ===== JET PRIVÉ =====
reset()
prof=[(7.6,0),(7.45,.25),(7.0,.55),(6.2,.82),(5.0,.98),(3.6,1.02),(-3.0,1.0),(-4.6,.86),(-6.0,.6),(-7.2,.3),(-7.7,0)]
lathe(prof,24,'fus',0,yc=lambda z:max(0,(-z-3))*.08)
lathe([(4.6,1.0),(-4.8,.88)],24,'stripe',1,sy=.12);bpy.data.objects['stripe'].location=(0,-.2,0)
lathe([(6.9,.62),(5.9,.88)],24,'cock',2,sy=.3);bpy.data.objects['cock'].location=(0,.32,0)
for k in range(6):
    for sx in (-1,1):sph('win',.2,(sx*1.0,.25,3.4-k*.95),2,(.15,1,1.3),10)
box('door',(.04,1.2,.7),(-1.0,.0,5.0),4)
for sx in (-1,1):
    wing('wing',2.6,.9,6.2,2.3,.11,sx*.8,-.55,1.2,0,dih=.07,side=sx)
    wing('wlet',.9,.4,1.1,.8,.1,sx*7.0,-.55+6.2*.07,-1.1,1,vert=True)
    cyl('eng',.5,2.6,(sx*1.55,.45,-4.1),3,20)
    cyl('engf',.42,.05,(sx*1.55,.45,-2.79),4,20)
    cyl('engn',.38,.5,(sx*1.55,.45,-5.6),4,16,r2=.3)
    box('pyl',(.9,.18,1.0),(sx*1.1,.4,-4.0),0)
    cyl('navl',.1,.1,(sx*7.05,-.55+6.2*.07+1.15,-1.5),5 if sx>0 else 1,8)
fin=wing('fin',2.2,1.3,2.6,1.8,.11,0,.7,-5.6,1,vert=True)
for sx in (-1,1):wing('ttail',1.3,.7,2.4,.8,.1,sx*.1,3.3,-7.0,0,side=sx)
for (x,z) in [(0,5.6),(-1.3,-.2),(1.3,-.2)]:
    cyl('leg',.07,.9,(x,-1.3,z),3,8,(math.pi/2,0,0));cyl('whl',.27,.2,(x,-1.75,z),4,14,(0,math.pi/2,0))
R['jet']=export('jet')
# ===== AVION À HÉLICE (aile haute) =====
reset()
prof=[(3.6,.0),(3.55,.45),(3.3,.62),(2.4,.7),(.5,.74),(-1.0,.66),(-2.4,.42),(-3.6,.2),(-4.0,0)]
lathe(prof,16,'fus',0,yc=lambda z:max(0,(-z-.5))*.07,sx=.9)
lathe([(3.62,.48),(3.2,.62)],16,'cowl',4,sx=.9)
lathe([(2.2,.72),(-2.6,.42)],16,'stripe',1,sy=.13,sx=.91);bpy.data.objects['stripe'].location=(0,-.18,0)
box('wind',(1.0,.3,.75),(0,.6,2.0),2,(-.55,0,0))
for sx in (-1,1):box('sidew',(.04,.45,1.4),(sx*.66,.45,.9),2)
for sx in (-1,1):
    wing('wing',1.6,1.2,5.2,.2,.13,sx*.2,1.0,1.2,1 if False else 0,dih=.02,side=sx)
    cyl('strut',.05,1.5,(sx*1.15,.3,1.0),3,6,(math.pi/2,0,-sx*.75))
    wing('stab',1.0,.7,1.8,.4,.1,sx*.1,.45,-3.4,0,side=sx)
    cyl('leg',.05,.8,(sx*.85,-.85,1.0),3,6,(math.pi/2,0,sx*.5))
    sph('pant',.32,(sx*1.1,-1.15,1.0),0,(.6,.7,1.3),12);cyl('whl',.28,.16,(sx*1.1,-1.2,1.0),4,14,(0,math.pi/2,0))
    box('tip',(.08,.05,1.0),(sx*5.4,1.1,1.1),1)
wing('fin',1.3,.7,1.4,.8,.1,0,.5,-3.3,1,vert=True)
cyl('nwhl',.22,.14,(0,-1.2,3.0),4,12,(0,math.pi/2,0));cyl('nleg',.05,.7,(0,-.8,3.0),3,6,(math.pi/2,0,0))
cyl('spin',.18,.4,(0,0,3.85),3,12,r2=0)
R['prop']=export('prop')
# ===== AVION DE VOLTIGE (aile basse, verrière bulle) =====
reset()
prof=[(3.3,0),(3.2,.4),(2.9,.58),(1.8,.66),(.2,.66),(-1.2,.5),(-2.6,.28),(-3.4,.08),(-3.5,0)]
lathe(prof,18,'fus',0,yc=lambda z:max(0,(-z-.4))*.05)
lathe([(3.32,.42),(2.7,.6)],18,'cowl',1)
sph('canopy',.5,(0,.6,.2),2,(.85,.75,2.0),16)
for sx in (-1,1):
    wing('wing',1.7,1.0,3.8,.25,.15,sx*.3,-.35,.9,0,dih=.04,side=sx)
    box('stripeW',(.06,.02,1.0),(sx*2.5,-.24+2.5*.04,.85),1)
    wing('stab',.9,.6,1.4,.3,.1,sx*.1,.05,-3.0,1,side=sx)
    cyl('leg',.05,.75,(sx*.9,-.75,1.4),3,6,(math.pi/2,0,sx*.35));sph('pant',.27,(sx*1.05,-1.08,1.4),1,(.6,.7,1.3),12)
wing('fin',1.1,.6,1.2,.7,.1,0,.3,-2.9,1,vert=True)
cyl('spin',.16,.35,(0,0,3.5),1,12,r2=0)
R['stunt']=export('stunt')
# ===== HÉLICOPTÈRE =====
reset()
prof=[(2.6,0),(2.5,.45),(2.2,.85),(1.5,1.12),(.4,1.2),(-.8,1.12),(-1.6,.85),(-2.1,.5),(-2.3,0)]
lathe(prof,24,'pod',0,yc=lambda z:-max(0,z-1.2)*.12)
sph('glass',1.0,(0,.28,1.25),2,(1.06,.82,1.3),20)
lathe([(.9,1.22),(-1.2,1.15)],24,'stripe',1,sy=.18);bpy.data.objects['stripe'].location=(0,-.35,0)
lathe([(-1.8,.42),(-5.8,.16)],12,'boom',0,yc=lambda z:.25+(-z-1.8)*.03)
wing('fin',1.1,.6,1.5,.8,.12,0,.45,-5.6,1,vert=True)
for sx in (-1,1):wing('hstab',.6,.4,.9,.2,.1,sx*.1,.35,-4.6,0,side=sx)
cyl('mast',.12,.7,(0,1.45,.1),3,10,(math.pi/2,0,0))
cyl('hub',.32,.22,(0,1.85,.1),4,14,(math.pi/2,0,0))
box('engine',(1.0,.45,1.6),(0,1.15,-.6),3)
cyl('exh',.16,.5,(.3,1.25,-1.5),4,10)
cyl('thub',.12,.2,(.2,.75,-5.85),4,10,(0,math.pi/2,0))
for sx in (-1,1):
    cyl('skid',.07,3.2,(sx*.95,-1.35,.1),4,8)
    cyl('skt',.07,.5,(sx*.95,-1.25,1.85),4,8,(-.6,0,0))
    for z in (-.7,.9):cyl('sst',.05,.75,(sx*.85,-1.0,z),4,6,(math.pi/2,0,sx*.25))
    box('door',(.04,.8,.9),(sx*1.18,.0,.0),4)
cyl('light',.09,.05,(0,-1.0,1.6),5,8,(math.pi/2,0,0))
R['heli']=export('heli')
json.dump(R,open(OUT+'aircraft.json','w'));print('tailles',{k:len(json.dumps(v))//1024 for k,v in R.items()},'Ko')
