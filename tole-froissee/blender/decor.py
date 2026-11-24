# Décor de SMASHR modélisé avec Blender (repère du jeu : Y en haut, Z vers l'avant)
# Chaque objet utilise des « emplacements de couleur » m0..m7 ; le jeu choisit les vraies couleurs.
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
R={}
# ================= ARBRES =================
reset();cyl(.26,.13,2.9,(0,1.45,0),0,9);seg((0,2.2,0),(.75,3.2,.3),.07,0,6);seg((0,2.5,0),(-.6,3.4,-.35),.06,0,6);seg((0,2.0,0),(.1,3.0,-.7),.06,0,6);R['trunk']=export('trunk')
reset()
for i,(x,y,z,r) in enumerate([(0,3.95,0,1.75),(1.05,3.35,.45,1.15),(-.95,3.5,-.5,1.1),(.3,4.85,-.2,1.15),(-.45,3.05,.85,.95),(.55,3.1,-.9,.9)]):ico(r,(x,y,z),i%3,1,(1,.92,1),.13,i)
R['crown']=export('crown')
reset()
for i,(y,r,h) in enumerate([(1.9,1.95,2.1),(3.1,1.6,1.9),(4.2,1.2,1.7),(5.2,.75,1.5)]):
    o=cyl(r,0.05,h,(0,y,0),i%2,9,UP,False);o.rotation_euler=(0,i*.35,0)
cyl(.2,.14,1.2,(0,.6,0),2,7);R['pine']=export('pine')
# ================= LAMPADAIRE =================
reset();cyl(.22,.18,.5,(0,.25,0),0,10);cyl(.12,.07,6.6,(0,3.8,0),0,10);sph(.11,(0,7.1,0),0)
pts=[(0,6.9,0),(.45,7.12,0),(1.0,7.18,0),(1.5,7.12,0),(1.8,7.0,0)]
for a,b in zip(pts,pts[1:]):seg(a,b,.05,0,6)
cyl(.16,.1,.5,(0,.9,0),0,10)
R['lamp']=export('lamp')
reset();o=box((.78,.16,.36),(1.8,6.95,0),0,bv=.05);box((.62,.03,.26),(1.8,6.86,0),1);R['lamphead']=export('lamphead')
# ================= MAISONS DU DÉCOR (9 x 4.2 x 8, façade vers +z) =================
def windows(front,back,side,y=2.4,ww=1.3,wh=1.2):
    for x in front:box((ww+.2,wh+.2,.12),(x,y,4.03),2);box((ww,wh,.06),(x,y,4.06),3);box((ww+.3,.1,.2),(x,y-wh/2-.12,4.08),2)
    for x in back:box((ww+.2,wh+.2,.12),(x,y,-4.03),2);box((ww,wh,.06),(x,y,-4.06),3)
    for z in side:
        for sx in (-1,1):box((.12,wh+.2,ww+.2),(sx*4.53,y,z),2,bv=.02);box((.06,wh,ww),(sx*4.56,y,z),3)
def gable(h0,h1,ov):
    W,D=4.5+ov,4+ov
    poly([(-W,h0,-D),(W,h0,-D),(W,h1,0),(-W,h1,0)],[(0,1,2,3)],1);poly([(-W,h0,D),(-W,h1,0),(W,h1,0),(W,h0,D)],[(0,1,2,3)],1)
    poly([(-4.5,h0,-4),(-4.5,h0,4),(-4.5,h1-.4,0)],[(0,1,2)],0);poly([(4.5,h0,4),(4.5,h0,-4),(4.5,h1-.4,0)],[(0,1,2)],0)
    poly([(-W,h0-.05,-D),(-W,h0-.05,D),(W,h0-.05,D),(W,h0-.05,-D)],[(3,2,1,0)],6)
reset();box((9,4.2,8),(0,2.1,0),0);box((9.2,.45,8.2),(0,.22,0),6);windows([-2.8,2.8],[-2.8,2.8],[0]);box((1.3,2.3,.14),(0,1.15,4.05),4);box((1.6,2.55,.1),(0,1.25,4.02),2);box((1.8,.2,.8),(0,.1,4.4),6)
gable(4.2,6.6,.45);box((.7,1.8,.7),(2.4,6.2,-1.6),5);box((.85,.12,.85),(2.4,7.1,-1.6),6);R['houseA']=export('houseA')
reset();box((9,4.2,8),(0,2.1,0),0);box((9.2,.45,8.2),(0,.22,0),6);windows([-3,3],[-2.5,2.5],[-1.8,1.8]);box((1.3,2.3,.14),(0,1.15,4.05),4);box((1.6,2.55,.1),(0,1.25,4.02),2)
box((4.4,.18,1.8),(0,3.1,4.9),1);[cyl(.1,.1,3,(x,1.5,5.6),2,8) for x in (-2,2)];box((4.6,.2,2),(0,.1,4.9),6)
W,D,H0,H1=5,4.5,4.2,6.1;poly([(-W,H0,-D),(W,H0,-D),(2.2,H1,0),(-2.2,H1,0)],[(0,1,2,3)],1);poly([(-W,H0,D),(-2.2,H1,0),(2.2,H1,0),(W,H0,D)],[(0,1,2,3)],1);poly([(-W,H0,-D),(-2.2,H1,0),(-W,H0,D)],[(0,1,2)],1);poly([(W,H0,D),(2.2,H1,0),(W,H0,-D)],[(0,1,2)],1)
box((.7,1.6,.7),(-2.2,5.8,1.2),5);R['houseB']=export('houseB')
reset();box((9,4.2,8),(0,2.1,0),0);box((9.2,.45,8.2),(0,.22,0),6);box((9.1,.12,8.1),(0,2.1,0),2);windows([-3,0,3],[-3,0,3],[-1.8,1.8],1.2,1.1,.9);windows([-3,0,3],[-3,0,3],[-1.8,1.8],3.2,1.1,.9)
box((1.2,1.9,.14),(1.5,.95,4.05),4);box((9.3,.5,8.3),(0,4.45,0),2);box((8.6,.1,7.6),(0,4.25,0),6);box((1.4,1,1.2),(-2.5,4.95,-1.5),6);R['houseC']=export('houseC')
# ================= TOITS ET RUE =================
reset();box((1.6,1,1.1),(0,.5,0),0,bv=.04);cyl(.38,.38,.08,(0,1.02,0),6,14);box((1.4,.05,.05),(0,.3,.56),6);R['ac']=export('ac')
reset();cyl(1.2,1.2,2.2,(0,3.3,0),4,16);cyl(1.3,.1,.9,(0,4.85,0),6,16);[seg((x,0,z),(x*.7,2.2,z*.7),.07,6,6) for x,z in ((1,1),(-1,1),(1,-1),(-1,-1))];[box((2.4,.08,.08),(0,1.2,s),6) for s in (-.85,.85)];R['tank']=export('tank')
reset();cyl(.06,.03,6,(0,3,0),6,6);[box((w,.05,.05),(0,y,0),6) for w,y in ((1.6,3.5),(1.1,4.5),(.7,5.3))];sph(.12,(0,6.05,0),7);box((.6,.4,.6),(0,.2,0),6);R['antenna']=export('antenna')
reset();[box((1.8,.06,.14),(0,.48,z),4,bv=.01) for z in (-.2,0,.2)];[box((1.8,.06,.12),(0,.75+i*.17,-.32),4,bv=.01) for i in range(2)];[box((.06,.48,.5),(x,.24,0),6) for x in (-.75,.75)];[box((.06,.6,.06),(x,.75,-.32),6) for x in (-.75,.75)];R['bench']=export('bench')
reset();cyl(.28,.25,.9,(0,.45,0),0,12);cyl(.31,.31,.06,(0,.92,0),6,12);R['bin']=export('bin')
# ================= MEUBLES DE LA MAISON =================
reset();box((2.4,.3,.9),(0,.3,0),0,bv=.05);box((1.15,.2,.75),(-.6,.55,.05),0,bv=.07);box((1.15,.2,.75),(.6,.55,.05),0,bv=.07);box((2.4,.6,.22),(0,.75,-.36),0,bv=.06);[box((.22,.62,.9),(x,.46,0),0,bv=.06) for x in (-1.2,1.2)];[cyl(.04,.03,.15,(x,.07,z),6,6) for x in (-1.05,1.05) for z in (-.35,.35)];R['sofa']=export('sofa')
reset();box((2.2,.35,2.6),(0,.25,0),4,bv=.03);box((2.1,.25,2.5),(0,.55,.0),2,bv=.06);box((2.12,.14,1.7),(0,.72,.4),0,bv=.06);[box((.75,.16,.45),(x,.75,-.95),2,bv=.07) for x in (-.5,.5)];box((2.3,1.1,.12),(0,.75,-1.3),4,bv=.03);R['bed']=export('bed')
reset();box((1,.45,.4),(0,.22,0),4,bv=.02);box((.95,.03,.36),(0,.46,0),6);box((1,.6,.06),(0,.9,-.05),6,bv=.01);box((.94,.54,.02),(0,.9,-.015),3);R['tv']=export('tv')
reset();box((7.4,.88,.7),(0,.44,0),2,bv=.01);box((7.5,.06,.75),(0,.91,0),6);[box((.02,.7,.02),(x,.45,.36),6) for x in [-3.0+i*.75 for i in range(9)]];box((.8,.04,.5),(1.5,.95,0),7);cyl(.12,.12,.02,(-1.8,.95,-.1),5,12);cyl(.12,.12,.02,(-1.2,.95,-.1),5,12);cyl(.12,.12,.02,(-1.8,.95,.15),5,12);box((7.4,.7,.35),(0,2.0,-.18),2,bv=.01);seg((1.5,.95,-.2),(1.5,1.25,-.05),.02,7,6);R['kitchen']=export('kitchen')
reset();box((.9,2,.8),(0,1,0),7,bv=.04);box((.9,.02,.82),(0,1.3,0),6);[box((.04,.4,.04),(.35,y,.42),6) for y in (.9,1.65)];R['fridge']=export('fridge')
reset();box((1.6,.07,1.1),(0,.78,0),4,bv=.02);[cyl(.035,.03,.75,(x,.38,z),4,6) for x in (-.7,.7) for z in (-.45,.45)];R['table']=export('table')
reset();box((.45,.06,.45),(0,.46,0),4,bv=.015);box((.45,.5,.05),(0,.72,-.2),4,bv=.015);[cyl(.025,.02,.45,(x,.22,z),4,6) for x in (-.18,.18) for z in (-.18,.18)];R['chair']=export('chair')
reset();cyl(.24,.18,.45,(0,.22,0),2,12);[ico(.2+.04*(i%3),(math.cos(i*1.3)*.22,.65+i*.08,math.sin(i*1.3)*.22),5,1,(.7,1.5,.7),.15,i) for i in range(7)];R['plant']=export('plant')
reset();cyl(.18,.2,.05,(0,.03,0),6,12);cyl(.025,.025,1.5,(0,.78,0),6,6);cyl(.3,.18,.35,(0,1.55,0),2,14);R['flamp']=export('flamp')
reset();box((1.6,2.2,.6),(0,1.1,0),4,bv=.02);box((.02,2.0,.02),(0,1.1,.31),6);[box((.03,.25,.03),(x,1.2,.32),7) for x in (-.08,.08)];R['wardrobe']=export('wardrobe')
reset();box((1.7,.6,.85),(0,.3,0),2,bv=.12);box((1.45,.05,.62),(0,.56,0),3);seg((.7,.6,0),(.75,.85,0),.03,7,6);R['bath']=export('bath')
reset();box((2.6,.18,1.5),(0,.78,0),4,bv=.03);box((2.3,.05,1.2),(0,.88,0),5);[box((.16,.7,.16),(x,.35,z),4,bv=.02) for x in (-1.1,1.1) for z in (-.6,.6)];R['pooltbl']=export('pooltbl')
reset();box((.8,.45,.7),(0,.3,0),0,bv=.06);box((.8,.7,.16),(0,.75,-.3),0,bv=.06);[box((.12,.5,.7),(x,.42,0),6,bv=.03) for x in (-.42,.42)];R['cseat']=export('cseat')
reset();box((.75,1.85,.7),(0,.92,0),0,bv=.03);box((.6,.45,.05),(0,1.42,.3),3);box((.72,.12,.35),(0,1.0,.4),6);[sph(.035,(x,1.08,.48),7) for x in (-.15,0,.15)];R['arcade']=export('arcade')
# ================= CABANE DE DÉPART (intérieur en rondins, 24 x 3.4 x 14) =================
reset()
for i in range(9):
    y=.19+i*.38;seg((-12,y,-7),(12,y,-7),.2,4 if i%2 else 5,8)
    for sx in (-1,1):seg((sx*12,y,-7),(sx*12,y,7),.2,4 if i%2 else 5,8)
for x in range(-11,12,2):box((1.9,.06,13.8),(x,.0,0),4 if (x//2)%2 else 5)
for x in (-8,0,8):seg((x,3.3,-7),(x,3.3,7),.16,6,8)
for wx in (-8,0,8):box((3.4,1.8,.1),(wx,1.9,-6.85),2)
R['cabin']=export('cabin')

# ================= PALMIER =================
reset()
pts=[(0,0,0)]
for i in range(1,9):t=i/8;pts.append((0.9*t*t,8.5*t,0.15*t))
for i,(a,b) in enumerate(zip(pts,pts[1:])):seg(a,b,.24-.1*i/8,0 if i%2 else 1,8);sph(.27-.1*i/8,b,0 if i%2 else 1,(1,.5,1),8)
top=pts[-1]
for k in range(9):
    ang=k/9*2*math.pi;L=3.2+(k%3)*.4;fr=[]
    for j in range(6):
        u=j/5;d=L*u;fr.append((top[0]+math.cos(ang)*d,top[1]+.5*math.sin(u*math.pi*.6)-u*u*2.0,top[2]+math.sin(ang)*d))
    for j in range(5):
        a,b=fr[j],fr[j+1];w=.55*(1-j/6)+.1;nx,nz=-math.sin(ang)*w,math.cos(ang)*w
        poly([(a[0]+nx,a[1],a[2]+nz),(a[0]-nx,a[1],a[2]-nz),(b[0]-nx*.8,b[1],b[2]-nz*.8),(b[0]+nx*.8,b[1],b[2]+nz*.8)],[(0,1,2,3)],2+(k%2))
for k in range(4):sph(.16,(top[0]+math.cos(k*1.6)*.25,top[1]-.35,top[2]+math.sin(k*1.6)*.25),4)
R['palm']=export('palm')

# ================= DÉTAILS DE RUE =================
def plate(n,r,y,mi,rot=0):
    o=cyl(r,r,.05,(0,y,.06),mi,n,(math.pi/2,0,rot),False);return o
reset();cyl(.04,.04,2.6,(0,1.3,0),6,8);plate(8,.38,2.55,0,math.pi/8);plate(8,.32,2.55,2,math.pi/8);o=bpy.data.objects[-1];o.location.z=.09;R['sstop']=export('sstop')
reset();cyl(.04,.04,2.6,(0,1.3,0),6,8);poly([(-.42,2.75,.08),(.42,2.75,.08),(0,2.05,.08)],[(0,1,2)],0);poly([(-.3,2.68,.1),(.3,2.68,.1),(0,2.17,.1)],[(0,1,2)],2);R['syield']=export('syield')
reset();cyl(.04,.04,2.6,(0,1.3,0),6,8);plate(20,.34,2.5,0);plate(20,.27,2.5,2);o=bpy.data.objects[-1];o.location.z=.09;box((.08,.2,.02),(-.07,2.5,.12),3);box((.08,.2,.02),(.07,2.5,.12),3);R['sspeed']=export('sspeed')
reset();cyl(.38,.38,.03,(0,.015,0),6,16,UP,False);[box((.62,.005,.04),(0,.032,-.24+i*.12),3) for i in range(5)];R['manhole']=export('manhole')
reset();cyl(.13,.1,9,(0,4.5,0),4,8);box((1.8,.12,.12),(0,8.4,0),4);[cyl(.05,.05,.18,(x,8.55,0),2,6) for x in (-.75,-.25,.25,.75)];box((.4,.5,.3),(0,6.5,.18),6);R['upole']=export('upole')
reset();box((2.2,2.4,1.6),(0,1.2,0),0,bv=.04);box((2.5,.15,1.9),(0,2.5,0),1);box((1.9,1.0,.05),(0,1.5,.81),3);box((2.3,.12,.5),(0,1.0,1.0),4);[box((.25,.32,.02),(-.8+i*.4,1.65,.84),5) for i in range(5)];R['kiosk']=export('kiosk')
reset();[box((.08,1,.08),(x,.5,0),6) for x in (-.9,.9)];[box((2,.18,.05),(0,y,0),7 if i%2 else 2) for i,y in enumerate((.55,.85))];[box((.25,.18,.06),(-.75+k*.5,.85,.01),0) for k in range(4)];R['barrier']=export('barrier')
reset();cyl(.18,.03,.7,(0,.37,0),0,10);cyl(.15,.12,.08,(0,.38,0),2,10);box((.42,.04,.42),(0,.02,0),6);R['cone']=export('cone')

# ================= LOGEMENTS À ACHETER, VUS DE L'EXTÉRIEUR (façade vers +z) =================
def win(x,y,z,w,h,face=1):
    box((w+.2,h+.2,.1),(x,y,z+face*.05),2);box((w,h,.06),(x,y,z+face*.08),3)
def sidewin(x,y,z,w,h):
    box((.1,h+.2,w+.2),(x+(.05 if x>0 else -.05),y,z),2);box((.06,h,w),(x+(.08 if x>0 else -.08),y,z),3)
def roofgable(W,D,h0,h1,ov=.4):
    W,D=W/2+ov,D/2+ov
    poly([(-W,h0,-D),(W,h0,-D),(W,h1,0),(-W,h1,0)],[(0,1,2,3)],1);poly([(-W,h0,D),(-W,h1,0),(W,h1,0),(W,h0,D)],[(0,1,2,3)],1)
    poly([(-W+ov,h0,-D+ov),(-W+ov,h0,D-ov),(-W+ov,h1-.3,0)],[(0,1,2)],0);poly([(W-ov,h0,D-ov),(W-ov,h0,-D+ov),(W-ov,h1-.3,0)],[(0,1,2)],0)
# cabane en rondins
reset()
for i in range(8):
    y=.2+i*.38;seg((-3,y,2.5),(3,y,2.5),.2,4 if i%2 else 5,8);seg((-3,y,-2.5),(3,y,-2.5),.2,4 if i%2 else 5,8)
    seg((-3,y,-2.5),(-3,y,2.5),.2,4 if i%2 else 5,8);seg((3,y,-2.5),(3,y,2.5),.2,4 if i%2 else 5,8)
roofgable(6.4,5.4,3.1,4.9,.5);box((1,2,.12),(0,1,2.62),6);win(-1.7,1.7,2.55,1,.9);box((6.8,.15,2),(0,.08,3.6),4);[cyl(.1,.1,2.7,(x,1.35,4.4),4,6) for x in (-3,3)];box((7,.12,2.4),(0,2.8,3.7),1);box((.6,2.2,.6),(2,4.6,-.8),5)
R['p_cabane']=export('p_cabane')
# studio : petit immeuble de 3 étages
reset();box((10,9,10),(0,4.5,0),0);box((10.4,.4,10.4),(0,9.1,0),6)
for f in range(3):
    y=1.6+f*3
    for x in (-3,0,3):win(x,y,5,1.6,1.4)
    for z in (-2.5,2.5):sidewin(5,y,z,1.4,1.3);sidewin(-5,y,z,1.4,1.3)
    if f>0:box((2.4,.15,1.1),(-3,y-.85,5.55),6);box((2.4,.8,.06),(-3,y-.45,6.08),7)
box((2.4,.15,1.4),(3,2.9,5.7),6);box((1.4,2.2,.1),(3,1.1,5.05),3)
R['p_studio']=export('p_studio')
# T3 : immeuble de 4 étages avec balcons
reset();box((12,12.4,11),(0,6.2,0),0);box((12.4,.5,11.4),(0,12.5,0),2)
for f in range(4):
    y=1.7+f*3
    for x in (-4,-1.3,1.3,4):win(x,y,5.5,1.4,1.5)
    if f>0:
        for x in (-2.65,2.65):box((3.4,.15,1.3),(x,y-.9,6.2),2);box((3.4,.9,.05),(x,y-.45,6.85),7)
box((1.6,2.3,.1),(0,1.15,5.55),3);box((3,.2,1.6),(0,2.6,6.3),6)
R['p_t3']=export('p_t3')
# maison familiale avec garage
reset();box((11,4,9),(0,2,0),0);box((11.2,.4,9.2),(0,.2,0),6);roofgable(11,9,4,6.6,.5)
for x in (-3.2,3.2):win(x,2.3,4.5,1.4,1.3)
box((1.2,2.2,.12),(0,1.1,4.56),4);box((5,3,6),(8,1.5,0),0);box((4,2.4,.1),(8,1.2,3.04),2);[box((4,.04,.12),(8,.4+i*.5,3.1),6) for i in range(5)];box((5.4,.25,6.4),(8,3.1,0),1);box((.7,1.8,.7),(-3,6.3,-1.5),5)
R['p_maison']=export('p_maison')
# duplex moderne
reset();box((12,3.4,9),(0,1.7,0),0);box((9,3.2,8),(-1.5,5,-.5),2);box((12.2,.25,9.2),(0,3.45,0),6);box((9.2,.25,8.2),(-1.5,6.7,-.5),6)
box((7,2.6,.08),(-.5,1.6,4.55),3);box((5,2.4,.08),(-2,5,3.55),3);box((3,1,.05),(4.5,4,4.4),7);box((.05,1,4),(6,4,2.5),7)
[box((.12,3.4,.12),(x,1.7,4.6),6) for x in (-4,3)]
R['p_duplex']=export('p_duplex')
# villa avec piscine
reset();box((16,3.6,8),(0,1.8,-2),0);box((6,3.6,8),(5,1.8,4),0);box((16.6,.3,8.6),(0,3.75,-2),2);box((6.6,.3,8.6),(5,3.75,4),2)
box((9,2.8,.08),(-3.5,1.7,2.05),3);box((.08,2.8,6),(1.95,1.7,4),3);box((9,.1,5),(-3.5,.05,5.5),2);box((7,.12,3.4),(-3.5,.1,5.6),3)
[box((.15,.6,.15),(x,.3,8),6) for x in (-8,-5,-2)]
R['p_villa']=export('p_villa')
# penthouse : tour avec appartement vitré au sommet
reset();box((14,36,14),(0,18,0),0)
for f in range(11):
    y=2+f*3.2
    for x in (-4.5,-1.5,1.5,4.5):win(x,y,7,1.6,1.8)
box((13,4,13),(0,38,0),3);box((14.4,.4,14.4),(0,36.1,0),2);box((14.4,.4,14.4),(0,40.1,0),2);[ico(.9,(x,36.9,z),5,1,(1,1,1),.1,i) for i,(x,z) in enumerate(((-5,6),(5,6),(-5,-6),(5,-6)))]
box((3,3,.1),(0,1.6,7.05),3)
R['p_pent']=export('p_pent')
# manoir classique
reset();box((24,8,13),(0,4,0),0);box((24.4,.5,13.4),(0,.25,0),6);box((24.6,.4,13.6),(0,8.2,0),2)
W,D,H0,H1=12.8,7.2,8.2,11.5;poly([(-W,H0,-D),(W,H0,-D),(8,H1,0),(-8,H1,0)],[(0,1,2,3)],1);poly([(-W,H0,D),(-8,H1,0),(8,H1,0),(W,H0,D)],[(0,1,2,3)],1);poly([(-W,H0,-D),(-8,H1,0),(-W,H0,D)],[(0,1,2)],1);poly([(W,H0,D),(8,H1,0),(W,H0,-D)],[(0,1,2)],1)
for f in range(2):
    for x in (-10,-7,-4,4,7,10):win(x,2.3+f*3.6,6.5,1.2,2)
box((8,.5,3),(0,6.2,8),2);poly([(-4.2,6.45,9.6),(4.2,6.45,9.6),(0,8.4,9.6)],[(0,1,2)],2);[cyl(.32,.28,5.8,(x,3.2,9.2),2,12) for x in (-3.4,-1.15,1.15,3.4)];box((2,3.2,.1),(0,1.6,6.55),4);box((9,.3,3.5),(0,.15,8.2),2)
[box((.8,2.4,.8),(x,11.2,0),5) for x in (-6,6)]
R['p_manoir']=export('p_manoir')
# escalier intérieur (monte vers -z, 8 marches de 0,42 m) avec rampe
reset()
for i in range(8):box((1.2,.08,.46),(0,.21+i*.42,2.6-i*.48),4);box((1.2,.34,.04),(0,.04+i*.42,2.83-i*.48),2)
for sx in (-.62,.62):poly([(sx,0,2.85),(sx,0,-1),(sx,3.4,-1.05),(sx,3.6,-1.05),(sx,.3,2.85)],[(0,1,2,3,4)],6)
seg((-.62,1.1,2.85),(-.62,4.5,-1.05),.035,7,6);[cyl(.02,.02,1.0,(-.62,.7+i*.42,2.6-i*.48),7,5) for i in range(0,8,2)]
R['stairs']=export('stairs')
json.dump(R,open(OUT+'decor.json','w'),separators=(',',':'));print('taille',len(json.dumps(R))//1024,'Ko',{k:len(json.dumps(v))//1024 for k,v in R.items()})
