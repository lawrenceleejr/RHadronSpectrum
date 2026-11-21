"""Blender (>= 4.x / 5.x, Cycles) scene: a static gluino (adjoint Wilson line) on a 2+1D lattice slab.

blender -b -P rhadron_scene.py -- --variant gluelump|rmeson|rbaryon --out out.png [--samples 256 --res 2400 1600]
"""
import math
import sys

import bpy
from mathutils import Vector

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
opts = {"variant": "gluelump", "out": "/tmp/rhadron.png", "samples": "256", "res": ["2400", "1600"]}
i = 0
while i < len(argv):
    k = argv[i].lstrip("-")
    if k == "res":
        opts["res"] = argv[i + 1:i + 3]
        i += 3
    else:
        opts[k] = argv[i + 1]
        i += 2

# ---------------------------------------------------------------- reset
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.render.engine = "CYCLES"
scene.cycles.samples = int(opts["samples"])
scene.cycles.use_denoising = True
scene.render.resolution_x, scene.render.resolution_y = int(opts["res"][0]), int(opts["res"][1])
scene.render.film_transparent = False
scene.view_settings.view_transform = "AgX" if "AgX" in [v.identifier for v in
    bpy.types.ColorManagedViewSettings.bl_rna.properties["view_transform"].enum_items] else "Filmic"
scene.view_settings.look = "None"

N, T, A = 7, 9, 1.0  # spatial sites per side, time slices, spacing
C = (N - 1) / 2 * A
T0, T1 = 1, T - 2     # source / sink time slices of the correlator


def mat_principled(name, color, rough=0.4, metal=0.0, emit=None, strength=0.0, alpha=1.0, transmission=0.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes.get("Principled BSDF")
    b.inputs["Base Color"].default_value = (*color, 1)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    if "Transmission Weight" in b.inputs:
        b.inputs["Transmission Weight"].default_value = transmission
    if emit is not None:
        key = "Emission Color" if "Emission Color" in b.inputs else "Emission"
        b.inputs[key].default_value = (*emit, 1)
        b.inputs["Emission Strength"].default_value = strength
    b.inputs["Alpha"].default_value = alpha
    return m


def curve(points, radius, mat, name="curve", smooth=False, cyclic=False, res=24):
    cd = bpy.data.curves.new(name, "CURVE")
    cd.dimensions = "3D"
    cd.bevel_depth = radius
    cd.bevel_resolution = 6
    cd.resolution_u = res
    sp = cd.splines.new("NURBS" if smooth else "POLY")
    sp.points.add(len(points) - 1)
    for p, xyz in zip(sp.points, points):
        p.co = (*xyz, 1)
    sp.use_cyclic_u = cyclic
    if smooth:
        sp.order_u = 4
        sp.use_endpoint_u = not cyclic
    ob = bpy.data.objects.new(name, cd)
    ob.data.materials.append(mat)
    scene.collection.objects.link(ob)
    return ob


def multi_poly(segments, radius, mat, name):
    cd = bpy.data.curves.new(name, "CURVE")
    cd.dimensions = "3D"
    cd.bevel_depth = radius
    cd.bevel_resolution = 2
    for a, b in segments:
        sp = cd.splines.new("POLY")
        sp.points.add(1)
        sp.points[0].co = (*a, 1)
        sp.points[1].co = (*b, 1)
    ob = bpy.data.objects.new(name, cd)
    ob.data.materials.append(mat)
    scene.collection.objects.link(ob)
    return ob


def site(i, j, t):
    return (i * A - C, j * A - C, t * A)


# ---------------------------------------------------------------- lattice slab
m_link = mat_principled("link", (0.16, 0.17, 0.20), rough=0.7)
m_site = mat_principled("site", (0.32, 0.34, 0.40), rough=0.4)
segs = []
for i in range(N):
    for j in range(N):
        for t in range(T):
            p = site(i, j, t)
            if i + 1 < N:
                segs.append((p, site(i + 1, j, t)))
            if j + 1 < N:
                segs.append((p, site(i, j + 1, t)))
            if t + 1 < T:
                segs.append((p, site(i, j, t + 1)))
multi_poly(segs, 0.007, m_link, "links")
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.03, segments=16, ring_count=8)
proto = bpy.context.active_object
proto.data.materials.append(m_site)
for i in range(N):
    for j in range(N):
        for t in range(T):
            ob = proto.copy()
            ob.location = site(i, j, t)
            scene.collection.objects.link(ob)
bpy.data.objects.remove(proto)

# ---------------------------------------------------------------- static adjoint line (two twisted strands)
cx = site(3, 3, 0)[:2]
m_gold = mat_principled("gold", (1.0, 0.70, 0.25), rough=0.22, metal=1.0, emit=(1.0, 0.62, 0.18), strength=1.2)
m_amber = mat_principled("amber", (0.95, 0.50, 0.12), rough=0.25, metal=1.0, emit=(1.0, 0.45, 0.10), strength=1.0)
for k, mat in enumerate((m_gold, m_amber)):
    pts = []
    for s in range(0, 161):
        z = T0 * A + (T1 - T0) * A * s / 160
        ph = 2 * math.pi * 2.5 * s / 160 + k * math.pi
        pts.append((cx[0] + 0.085 * math.cos(ph), cx[1] + 0.085 * math.sin(ph), z))
    curve(pts, 0.045, mat, name=f"adj{k}", smooth=True, res=4)

# source / sink markers: glowing discs
m_src = mat_principled("src", (1, 0.8, 0.5), emit=(1.0, 0.75, 0.4), strength=6.0)
for t in (T0, T1):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.11, location=(cx[0], cx[1], t * A))
    bpy.context.active_object.data.materials.append(m_src)

# ---------------------------------------------------------------- light degrees of freedom
variant = opts["variant"]
m_red = mat_principled("glue", (0.9, 0.1, 0.12), rough=0.3, emit=(1.0, 0.08, 0.10), strength=4.0)
m_blue = mat_principled("quark", (0.15, 0.4, 0.95), rough=0.3, emit=(0.15, 0.45, 1.0), strength=3.0)
m_green = mat_principled("quark3", (0.25, 0.75, 0.3), rough=0.3, emit=(0.2, 0.9, 0.35), strength=3.0)

if variant == "gluelump":
    # clover-like loop operators (traceless octet part) at source and sink
    for t in (T0, T1):
        z = t * A
        for (dx, dy) in ((1, 1), (-1, 1), (-1, -1), (1, -1)):
            loop = [(cx[0], cx[1], z), (cx[0] + dx * A, cx[1], z), (cx[0] + dx * A, cx[1] + dy * A, z),
                    (cx[0], cx[1] + dy * A, z), (cx[0], cx[1], z)]
            curve(loop, 0.03, m_red, name="loop")
    # volumetric gluon cloud around the line
    # gluon cloud: nested ellipsoids of constant low density -> smooth radial profile by overlap
    mv = bpy.data.materials.new("cloud")
    mv.use_nodes = True
    nt = mv.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    vol = nt.nodes.new("ShaderNodeVolumePrincipled")
    vol.inputs["Density"].default_value = 0.022
    vol.inputs["Color"].default_value = (1.0, 0.3, 0.3, 1)
    vol.inputs["Emission Color"].default_value = (1.0, 0.12, 0.1, 1)
    vol.inputs["Emission Strength"].default_value = 0.4
    nt.links.new(vol.outputs["Volume"], out.inputs["Volume"])
    zc = (T0 + T1) / 2 * A
    for k in range(8):
        f = 0.22 + 0.78 * k / 7
        bpy.ops.mesh.primitive_uv_sphere_add(radius=1.0, segments=48, ring_count=24, location=(cx[0], cx[1], zc))
        sh = bpy.context.active_object
        sh.scale = (1.35 * f, 1.35 * f, ((T1 - T0) * A / 2 + 0.2) * (0.55 + 0.45 * f))
        bpy.ops.object.shade_smooth()
        sh.data.materials.append(mv)
else:
    z0, z1 = T0 * A, T1 * A
    paths = [((1.6, 0.6), m_blue), ((-1.5, -0.9), m_blue)]
    if variant == "rbaryon":
        paths = [((1.7, 0.4), m_green), ((-0.6, 1.6), m_green), ((-1.2, -1.3), m_green)]
    for (ox, oy), mat in paths:
        pts = [(cx[0], cx[1], z0), (cx[0] + 0.5 * ox, cx[1] + 0.5 * oy, z0 + 0.8),
               (cx[0] + ox, cx[1] + oy, (z0 + z1) / 2 - 0.8), (cx[0] + 1.1 * ox, cx[1] + 1.1 * oy, (z0 + z1) / 2),
               (cx[0] + ox, cx[1] + oy, (z0 + z1) / 2 + 0.8), (cx[0] + 0.5 * ox, cx[1] + 0.5 * oy, z1 - 0.8),
               (cx[0], cx[1], z1)]
        curve(pts, 0.04, mat, name="quark", smooth=True)

# ---------------------------------------------------------------- lights, world, camera
world = bpy.data.worlds.new("w")
scene.world = world
world.use_nodes = True
bg = world.node_tree.nodes["Background"]
bg.inputs["Color"].default_value = (0.012, 0.013, 0.018, 1)
bg.inputs["Strength"].default_value = 1.0


def area(name, loc, size, energy, color):
    ld = bpy.data.lights.new(name, "AREA")
    ld.size = size
    ld.energy = energy
    ld.color = color
    ob = bpy.data.objects.new(name, ld)
    ob.location = loc
    scene.collection.objects.link(ob)
    d = Vector((cx[0], cx[1], (T0 + T1) / 2 * A)) - Vector(loc)
    ob.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()


area("key", (8, -6, 10), 6, 1800, (1.0, 0.95, 0.9))
area("rim", (-7, 7, 6), 5, 900, (0.6, 0.7, 1.0))
area("fill", (0, -10, 1), 8, 250, (1, 1, 1))

cam_d = bpy.data.cameras.new("cam")
cam_d.lens = 42
cam_d.dof.use_dof = True
cam_d.dof.aperture_fstop = 5.6
cam = bpy.data.objects.new("cam", cam_d)
scene.collection.objects.link(cam)
target = Vector((cx[0], cx[1], (T0 + T1) / 2 * A))
cam.location = target + Vector((12.5, -15.0, 6.5))
cam.rotation_euler = (target - cam.location).to_track_quat("-Z", "Y").to_euler()
cam_d.dof.focus_distance = (target - cam.location).length
scene.camera = cam

scene.render.filepath = opts["out"]
scene.render.image_settings.file_format = "PNG"
bpy.ops.render.render(write_still=True)
print("wrote", opts["out"])
