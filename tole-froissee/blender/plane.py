import bpy,bmesh,math,json,base64,struct
MAT=['body','livery','window','engine','dark','light']
bpy.ops.wm.read_factory_settings(use_empty=True)
def mat(i):
    m=bpy.data.materials.get(MAT[i]) or bpy.data.materials.new(MAT[i]);return m
def setm(o,i):o.data.materials.clear();o.data.materials.append(mat(i))
def link(me,name,mi):
    o=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(o);setm(o,mi);return o
def lathe_z(prof,segs,name,mi,ycurve=None):
    # profil (z, r) tourné autour de l'axe Z (avant = +Z) ; ycurve(z) relève le centre (queue relevée)
    bm=bmesh.new();rings=[]
    for (z,r) in prof:
        yc=ycurve(z) if ycurve else 0;ring=[]
        for k in range(segs):
            a=2*math.pi*k/segs;ring.append(bm.verts.new((r*math.cos(a),yc+r*math.sin(a)*1.04,z)))
        rings.append(ring)
    for j in range(len(rings)-1):
        for k in range(segs):bm.faces.new((rings[j][k],rings[j][(k+1)%segs],rings[j+1][(k+1)%segs],rings[j+1][k]))
    for ring,(z,r) in ((rings[0],prof[0]),(rings[-1],prof[-1])):
        if r>0.01:bm.faces.new(ring if ring is rings[-1] else list(reversed(ring)))
    me=bpy.data.meshes.new(name);bm.to_mesh(me);bm.free();o=link(me,name,mi)
    for p in me.polygons:p.use_smooth=True
    return o
def wing(name,root,tip,span,sweep,thick,x0,y0,z0,mi,dihedral=0.0,side=1):
    # aile trapézoïdale en flèche (épaisseur profilée simple)
    bm=bmesh.new();c=[]
    for (zc,ch,x,y) in [(z0,root,x0,y0),(z0-sweep,tip,x0+side*span,y0+span*dihedral)]:
        t=thick*ch
        c.append([bm.verts.new((x,y+tt,zc+zz)) for (zz,tt) in [(ch*.5,0),(ch*.15,t*.5),(-ch*.5,t*.08),(-ch*.5,-t*.08),(ch*.15,-t*.3)]])
    A,B=c
    for k in range(5):bm.faces.new((A[k],A[(k+1)%5],B[(k+1)%5],B[k]))
    bm.faces.new(list(reversed(A)));bm.faces.new(B)
    me=bpy.data.meshes.new(name);bm.to_mesh(me);bm.free();return link(me,name,mi)
def cyl(name,r,d,loc,mi,v=16,rot=(0,0,0)):
    bpy.ops.mesh.primitive_cylinder_add(vertices=v,radius=r,depth=d,location=loc,rotation=rot);o=bpy.context.active_object;o.name=name;setm(o,mi)
    for p in o.data.polygons:p.use_smooth=True
    return o
def boxo(name,s,loc,mi,rot=(0,0,0)):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc,rotation=rot);o=bpy.context.active_object;o.name=name;o.scale=s;bpy.ops.object.transform_apply(scale=True);setm(o,mi);return o
P=[]
# fuselage (longueur 30, rayon 1.6) : nez arrondi, queue relevée
prof=[(15.2,0.0),(15.0,.45),(14.4,.95),(13.4,1.32),(12,1.55),(10,1.62),(-8,1.62),(-10,1.5),(-12,1.15),(-13.6,.7),(-14.8,.25),(-15.1,0.0)]
P.append(lathe_z(prof,24,'fus',0,ycurve=lambda z:max(0,(-z-8))*.12))
# bande de livrée + hublots + cockpit
P.append(lathe_z([(11,1.635),(-9,1.635)],24,'stripe_tmp',1))
bpy.data.objects['stripe_tmp'].scale=(1,.18,1);bpy.data.objects['stripe_tmp'].location=(0,-.35,0)
for k in range(26):
    z=10-k*.72
    for sx in (-1,1):P.append(boxo('win',(.06,.32,.22),(sx*1.6,.42,z),2))
P.append(boxo('cockpit',(1.7,.35,.9),(0,.75,13.6),2,(-.35,0,0)))
# ailes, réacteurs, empennage
for sx in (-1,1):
    P.append(wing('wing',5.2,1.6,16,6,.12,sx*1.3,-.6,3,0,dihedral=.08,side=sx))
    P.append(cyl('eng',.85,3.6,(sx*5.5,-1.5,4.2),3,20,(0,0,0)))
    P.append(cyl('intake',.66,.12,(sx*5.5,-1.5,6.02),4,20,(0,0,0)))
    P.append(boxo('pylon',(.25,.9,2.2),(sx*5.5,-.9,3.6),0))
    P.append(wing('stab',2.6,1.1,5.6,2.2,.1,sx*.5,1.2,-12.6,0,dihedral=.05,side=sx))
    P.append(cyl('navl',.15,.15,(sx*17.3,-.6+16*.08,-2.8),5 if sx>0 else 1,8,(0,0,math.pi/2)))
fin=wing('fin',4.2,1.6,6.5,3.2,.1,0,1.4,-11.5,1,side=1);fin.rotation_euler=(0,0,math.pi/2);fin.location=(0.0,0,0);P.append(fin)
# train d'atterrissage
for (x,z) in [(0,11.5),(-2.4,1.6),(2.4,1.6)]:
    P.append(cyl('leg',.12,1.6,(x,-2.2,z),4,8));P.append(cyl('wheel',.45,.35,(x,-3.0,z),4,16,(0,math.pi/2,0)))
bpy.ops.object.select_all(action='DESELECT')
for o in bpy.data.objects:o.select_set(True)
bpy.context.view_layer.objects.active=P[0];bpy.ops.object.transform_apply(location=True,rotation=True,scale=True);bpy.ops.object.join();ob=bpy.context.active_object
me=ob.data;me.calc_loop_triangles();verts={};PP=[];N=[];M=[];I=[]
for tri in me.loop_triangles:
    mi=MAT.index(me.materials[tri.material_index].name)
    for li in tri.loops:
        v=me.vertices[me.loops[li].vertex_index].co;n=me.corner_normals[li].vector
        key=(round(v.x,3),round(v.y,3),round(v.z,3),round(n.x,2),round(n.y,2),round(n.z,2),mi)
        if key not in verts:verts[key]=len(M);PP+=[v.x,v.y,v.z];N+=[n.x,n.y,n.z];M.append(mi)
        I.append(verts[key])
q=lambda arr,s,fmt,lim:base64.b64encode(struct.pack('<%d%s'%(len(arr),fmt),*[max(-lim,min(lim,int(round(x*s)))) for x in arr])).decode()
out={'p':q(PP,32767/18,'h',32767),'n':q(N,127,'b',127),'m':base64.b64encode(bytes(M)).decode(),'i':base64.b64encode(struct.pack('<%dH'%len(I),*I)).decode(),'s':18}
json.dump(out,open('plane.json','w'));print('avion',len(M),'sommets',len(I)//3,'triangles',len(json.dumps(out))//1024,'Ko')
bpy.ops.wm.save_as_mainfile(filepath='/tmp/claude-0/-home-user-Axooz-football-career/43582ba6-8900-5dca-9b3b-7b12d55a9676/scratchpad/blender/avion.blend')
# rendu de contrôle
cols={'body':(0.92,0.93,0.95,1),'livery':(0.08,0.25,0.65,1),'window':(0.02,0.03,0.05,1),'engine':(0.6,0.62,0.66,1),'dark':(0.05,0.05,0.06,1),'light':(0.1,0.9,0.2,1)}
for m in bpy.data.materials:
    m.use_nodes=True;b=m.node_tree.nodes.get('Principled BSDF');b.inputs['Base Color'].default_value=cols[m.name];b.inputs['Roughness'].default_value=.35
ob.rotation_euler=(math.pi/2,0,0);sc=bpy.context.scene;bpy.ops.object.empty_add(location=(0,0,0));tgt=bpy.context.active_object;bpy.ops.object.camera_add(location=(30,-34,16));cam=bpy.context.active_object;c=cam.constraints.new('TRACK_TO');c.target=tgt;c.track_axis='TRACK_NEGATIVE_Z';c.up_axis='UP_Y';sc.camera=cam;cam.data.lens=34
bpy.ops.object.light_add(type='SUN',location=(0,20,0),rotation=(math.radians(40),math.radians(20),0));bpy.context.active_object.data.energy=4
w=bpy.data.worlds.new('w');sc.world=w;w.use_nodes=True;w.node_tree.nodes['Background'].inputs[0].default_value=(0.45,0.6,0.8,1);w.node_tree.nodes['Background'].inputs[1].default_value=.8
sc.render.engine='CYCLES';sc.cycles.device='CPU';sc.cycles.samples=24;sc.render.resolution_x=1100;sc.render.resolution_y=560;sc.render.filepath='/tmp/claude-0/-home-user-Axooz-football-career/43582ba6-8900-5dca-9b3b-7b12d55a9676/scratchpad/blender/avion_blender.png'
bpy.ops.render.render(write_still=True);print('rendu ok')
