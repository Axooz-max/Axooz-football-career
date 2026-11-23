# Personnages 3D de SMASHR, modélisés avec Blender (repère du jeu : Y en haut, Z vers l'avant)
import bpy,bmesh,math,json,base64,struct
MAT=['top','skin','bot','shoe','dark','white']
OUT='/tmp/claude-0/-home-user-Axooz-football-career/43582ba6-8900-5dca-9b3b-7b12d55a9676/scratchpad/blender/'
def reset():bpy.ops.wm.read_factory_settings(use_empty=True)
def mat(i):return bpy.data.materials.get(MAT[i]) or bpy.data.materials.new(MAT[i])
def link(me,name,mi):
    o=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(o);o.data.materials.append(mat(mi));return o
def loft(rings,segs,name,mi,cap0=True,cap1=True,zoff=None):
    """rings : liste de (y, demi-largeur x, demi-profondeur z[, décalage z]) ; sections ovales empilées"""
    bm=bmesh.new();R=[]
    for r in rings:
        y,rx,rz=r[0],r[1],r[2];oz=r[3] if len(r)>3 else 0
        R.append([bm.verts.new((rx*math.cos(2*math.pi*k/segs),y,oz+rz*math.sin(2*math.pi*k/segs))) for k in range(segs)])
    for j in range(len(R)-1):
        for k in range(segs):
            a,b,c,d=R[j][k],R[j][(k+1)%segs],R[j+1][(k+1)%segs],R[j+1][k]
            bm.faces.new((a,d,c,b) if rings[j+1][0]>rings[j][0] else (a,b,c,d))
    up=rings[-1][0]>rings[0][0]
    if cap0 and rings[0][1]>.002:bm.faces.new(R[0] if up else list(reversed(R[0])))
    if cap1 and rings[-1][1]>.002:bm.faces.new(list(reversed(R[-1])) if up else R[-1])
    me=bpy.data.meshes.new(name);bm.normal_update();bm.to_mesh(me);bm.free();o=link(me,name,mi)
    for p in me.polygons:p.use_smooth=True
    return o
def sph(name,r,loc,mi,sc=(1,1,1),seg=14):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=seg,ring_count=max(6,seg//2),radius=r,location=loc);o=bpy.context.active_object;o.name=name;o.scale=sc;bpy.ops.object.transform_apply(scale=True);o.data.materials.append(mat(mi))
    for p in o.data.polygons:p.use_smooth=True
    return o
def box(name,s,loc,mi,rot=(0,0,0)):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc,rotation=rot);o=bpy.context.active_object;o.name=name;o.scale=s;bpy.ops.object.transform_apply(scale=True);o.data.materials.append(mat(mi));return o
def cone(name,r1,r2,d,loc,mi,rot=(0,0,0),v=10):
    bpy.ops.mesh.primitive_cone_add(vertices=v,radius1=r1,radius2=r2,depth=d,location=loc,rotation=rot);o=bpy.context.active_object;o.name=name;o.data.materials.append(mat(mi))
    for p in o.data.polygons:p.use_smooth=True
    return o
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
    print(key,len(M),'sommets',len(I)//3,'triangles');bpy.ops.wm.save_as_mainfile(filepath=OUT+'perso_'+key+'.blend');return out
R={}
# ===== TORSE (haut + bassin) =====
reset()
loft([(1.585,.0,.0),(1.575,.1,.07),(1.555,.19,.11),(1.5,.235,.135),(1.4,.25,.15,.005),(1.28,.24,.155,.01),(1.15,.22,.145,.005),(1.02,.205,.135),(.93,.2,.13)],22,'chest',0,cap0=False)
loft([(.98,.205,.134),(.9,.21,.14),(.82,.205,.135),(.78,.17,.11)],22,'pelvis',2)
# boutons et col
for k in range(3):sph('btn',.012,(0,1.36-k*.12,.158),4,seg=6)
R['torso']=export('torso')
# ===== TÊTE (cou + visage) =====
reset()
loft([(1.5,.065,.065),(1.6,.062,.062),(1.64,.07,.068)],12,'neck',1)
loft([(1.585,.0,.0),(1.6,.075,.08,.02),(1.64,.135,.15,.02),(1.7,.17,.19,.01),(1.78,.19,.205),(1.86,.185,.2),(1.92,.155,.17,-.005),(1.96,.105,.12,-.01),(1.985,.05,.06,-.01),(1.995,.0,.0)],20,'head',1)
cone('nose',.03,.008,.07,(0,1.765,.215),1,(math.pi/2,0,0),8)
for sx in (-1,1):
    sph('ear',.045,(sx*.19,1.78,-.01),1,(.45,1,.8),10)
    sph('eye',.036,(sx*.068,1.805,.188),5,(1,1,.55),10)
    sph('pupil',.02,(sx*.068,1.803,.205),4,(1,1,.45),8)
    box('brow',(.07,.016,.02),(sx*.07,1.858,.2),4,(0,0,-sx*.12))
box('mouth',(.08,.014,.014),(0,1.696,.192),4)
sph('chin',.06,(0,1.66,.12),1,(1.3,.8,.9),10)
R['head']=export('head')
# ===== BRAS (pivot à l'épaule) : manches longues et courtes =====
def arm(key,sleeve):
    reset();sph('shoulder',.085,(0,-.02,0),0,(1,1,1),12)
    rings=[(-.02,.08,.08),(-.12,.072,.075),(-.3,.06,.062),(-.33,.058,.06),(-.45,.054,.056),(-.58,.047,.05)]
    cut=[r for r in rings if r[0]>=sleeve];rest=[r for r in rings if r[0]<=sleeve]
    if sleeve>-.58:
        loft(cut+[(sleeve,cut[-1][1]+.004,cut[-1][2]+.004)],14,'sleeve',0)
        loft([(sleeve+.01,cut[-1][1]-.006,cut[-1][2]-.006)]+[(r[0],r[1]-.008,r[2]-.008) for r in rest if r[0]<sleeve],14,'forearm',1)
    else:loft(rings,14,'sleeve',0)
    sph('hand',.05,(0,-.655,.008),1,(.85,1.35,.65),12);cone('thumb',.018,.012,.07,(0,-.64,.05),1,(-.6,0,0),6)
    R[key]=export(key)
arm('armL',-.58);arm('armS',-.2)
# ===== JAMBES (pivot à la hanche) : pantalon et short =====
def leg(key,cut):
    reset();rings=[(0,.105,.11),(-.1,.1,.105),(-.25,.085,.09),(-.42,.068,.072),(-.55,.064,.068),(-.72,.05,.055),(-.79,.048,.052)]
    up=[r for r in rings if r[0]>=cut];lo=[r for r in rings if r[0]<=cut]
    if cut>-.79:
        loft(up+[(cut,up[-1][1]+.006,up[-1][2]+.006)],14,'pants',2)
        loft([(cut+.01,up[-1][1]-.012,up[-1][2]-.012)]+[(r[0],r[1]-.01,r[2]-.01) for r in lo if r[0]<cut],14,'shin',1)
    else:loft(rings,14,'pants',2)
    sph('shoe',.07,(0,-.815,.045),3,(1,.65,2.05),14);box('sole',(.13,.022,.3),(0,-.855,.045),4)
    R[key]=export(key)
leg('legL',-.79);leg('legS',-.38)
json.dump(R,open(OUT+'avatar.json','w'));print('tailles',{k:len(json.dumps(v))//1024 for k,v in R.items()},'Ko')
