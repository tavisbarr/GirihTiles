import FreeCAD as App
import FreeCADGui as Gui
import Part, math
from FreeCAD import Base

# ─── New document ──────────────────────────────────────────────────────────────
doc = App.newDocument("SheshBand")

# ─── Parameters you probably don't want to touch ───────────────────────────────
INCH            = 25.4               # mm per inch
interior_angles = [72, 144, 144] * 2  # Shesh Band angles
ANG       = 36.0             # end-cut angle from perpendicular
n_sides         = 6

# ─── Parameters ────────────────────────────────────────────────────────────────
side            = 2.2 * INCH         # 2″ side length
THICK           = 0.4 * INCH        # tile thickness
RECESS          = 0.1 * INCH        # 1 mm recess
EMBEDDING       = 0.04 * INCH        # Embedding of lines into tile
WIDTH           = 0.3  * INCH       # groove width
MOLD_BUFFER     = 0.25 * INCH        # Min. thickness of mold
LINE_COLOR      = (171, 133, 70)     # rgb in decimal vector
TILE_COLOR      = (94, 140, 125)     # rgb in decimal vector


# ─── 1) Build the hexagon profile by walking its edges ────────────────────────
verts = [Base.Vector(-side/2, 0, 0)]
direction = 144
for angle in interior_angles:
    last = verts[-1]
    rad = math.radians(direction)
    step = Base.Vector(side * math.cos(rad), side * math.sin(rad), 0)
    verts.append(last.add(step))
    direction -= (180 - angle)
    

verts = verts[:-1]  # drop duplicate final point

# compute centroid
cx = sum(v.x for v in verts) / n_sides
cy = sum(v.y for v in verts) / n_sides

# ─── 2) Create the tile solid (face extruded by THICK–RECESS) ────────────────
hex_wire  = Part.makePolygon(verts + [verts[0]])
hex_face  = Part.Face(hex_wire)
hex_solid = hex_face.extrude(Base.Vector(0, 0, THICK - RECESS))
hex_obj   = doc.addObject("Part::Feature", "SheshBandTile")
hex_obj.Shape = hex_solid
hex_obj.Placement = App.Placement(
    Base.Vector(0, -side*math.sin(math.radians(36)), 0),                # pivot at origin
    Base.Rotation(Base.Vector(0,0,0), 0)
)
hex_obj.ViewObject.ShapeColor = (TILE_COLOR[0]/255, TILE_COLOR[1]/255, TILE_COLOR[2]/255)

def make_prism(L, rot, base):
    """
    Create a trapezoidal prism (bar) of midpoint-to-midpoint length L,
    rotated counterclockwise by ANG degrees about Z, then the midpoint
    is translated from the origin by (x,y,z).
    """
    β  = math.radians(ANG)
    hw = WIDTH / 2
    C  = (L / 2) * math.cos(β)

    # Compute the four corner X-coordinates at y = ±hw
    x1 = ( C +  hw*math.sin(β)) / math.cos(β)
    x2 = ( C -  hw*math.sin(β)) / math.cos(β)
    x3 = (-C +  hw*math.sin(β)) / math.cos(β)
    x4 = (-C -  hw*math.sin(β)) / math.cos(β)

    v = [
        Base.Vector(x1, -hw, 0),
        Base.Vector(x2, +hw, 0),
        Base.Vector(x3, +hw, 0),
        Base.Vector(x4, -hw, 0),
    ]

    # Build and extrude the profile
    wire    = Part.makePolygon(v + [v[0]])
    face    = Part.Face(wire)
    prism   = face.extrude(Base.Vector(0, 0, RECESS+EMBEDDING))

    # Apply rotation about origin
    prism.rotate(
        Base.Vector(0, 0, 0),
        Base.Vector(0, 0, 1),
        rot
    )
    # Apply translation
    prism.translate(Base.Vector(*base))

    return prism

L1=side*math.sin(math.radians(36))
p1 = make_prism(L1,90,(-0.5*(side+side*math.cos(math.radians(36))),0,0))
p2 = make_prism(L1,-18,(-0.5*(side+side*math.cos(math.radians(36)))+0.5*L1*(math.cos(math.radians(18))),0.5*L1*(1-math.sin(math.radians(18))),0))
p3 = make_prism(L1,54,(-0.5*L1*math.cos(math.radians(54)),L1-0.5*L1*math.sin(math.radians(54)),0))
p4 = make_prism(L1,-54,(0.5*L1*math.cos(math.radians(54)),L1-0.5*L1*math.sin(math.radians(54)),0))
p5 = make_prism(L1,18,(0.5*(side+side*math.cos(math.radians(36)))-0.5*L1*(math.cos(math.radians(18))),0.5*L1*(1-math.sin(math.radians(18))),0))
p6 = make_prism(L1,-90,(0.5*(side+side*math.cos(math.radians(36))),0,0))
p7 = make_prism(L1,162,(0.5*(side+side*math.cos(math.radians(36)))-0.5*L1*(math.cos(math.radians(18))),-0.5*L1*(1-math.sin(math.radians(18))),0))
p8 = make_prism(L1,-126,(0.5*L1*math.cos(math.radians(54)),-L1+0.5*L1*math.sin(math.radians(54)),0))
p9 = make_prism(L1,126,(-0.5*L1*math.cos(math.radians(54)),-L1+0.5*L1*math.sin(math.radians(54)),0))
p10 = make_prism(L1,198,(-0.5*(side+side*math.cos(math.radians(36)))+0.5*L1*(math.cos(math.radians(18))),-0.5*L1*(1-math.sin(math.radians(18))),0))


#p1 = make_prism(100,  30, (0,    0, 0))
#p2 = make_prism(100,  60, (0,    0, 0))
print(side*math.sin(math.radians(36)))
print(-0.5*(side+side*math.cos(math.radians(36))))

shapes = [p1,p2,p3,p4,p5,p6,p7,p8,p9,p10]

fused = shapes[0]
for s in shapes[1:]:
    fused = fused.fuse(s)

fused = fused.removeSplitter()
fused_obj = App.ActiveDocument.addObject("Part::Feature", "Filigree")
fused_obj.Shape = fused
fused_obj.ViewObject.ShapeColor = (LINE_COLOR[0]/255, LINE_COLOR[1]/255,  LINE_COLOR[2]/255)
fused_obj.Placement = App.Placement(
    Base.Vector(0, 0, THICK-RECESS-EMBEDDING),               
    Base.Rotation(Base.Vector(0,0,0), 0)
)



cut_feature_copy = App.ActiveDocument.copyObject(fused_obj, False)
cutter_copy.Label = "ChainBooleanCut_Copy"
hex_cut = doc.addObject("Part::Cut", "DecagonMinusPattern")
hex_cut.Base = hex_obj
hex_cut.Tool = cut_feature_copy
hex_cut.ViewObject.ShapeColor = (TILE_COLOR[0]/255, TILE_COLOR[1]/255, TILE_COLOR[2]/255)

# 2) Make a compound of the cut result and the cutter itself
group = doc.addObject("App::DocumentObjectGroup", "BaseTile")

# 2) Add both objects to it
group.addObject(hex_cut)
group.addObject(cut_feature)

# ─── Create a rectangular mold box around the tile and filigree ────────────────

# Get bounding box of full tile (base + filigree) via fusion
tile_fusion = doc.addObject("Part::MultiFuse", "TileFusion")
tile_fusion.Shapes = [App.ActiveDocument.copyObject(hex_cut, False), App.ActiveDocument.copyObject(fused_obj, False)]

# Recompute to allow bounding box calculation
doc.recompute()

bbox = tile_fusion.Shape.BoundBox
min_x, max_x = bbox.XMin, bbox.XMax
min_y, max_y = bbox.YMin, bbox.YMax
min_z, max_z = bbox.ZMin, bbox.ZMax

# Expand the bounding box by ¼″ in all directions
mold_x = (max_x - min_x) + 2 * MOLD_BUFFER
mold_y = (max_y - min_y) + 2 * MOLD_BUFFER
mold_z = (max_z - min_z) + MOLD_BUFFER  # mold base is at bottom, so only one buffer on top

# Position the cube so it fully contains the tile
cube = Part.makeBox(mold_x, mold_y, mold_z)
cube.translate(Base.Vector(min_x - MOLD_BUFFER, min_y - MOLD_BUFFER, 0))

mold_outer_obj = doc.addObject("Part::Feature", "MoldOuter")
mold_outer_obj.Shape = cube

# Cut the fused tile from the cube
mold_cut_obj = doc.addObject("Part::Cut", "MoldWithCavity")
mold_cut_obj.Base = mold_outer_obj
mold_cut_obj.Tool = tile_fusion
mold_cut_obj.ViewObject.ShapeColor = (0.5, 0.5, 0.5)  # neutral gray

# Rotate mold 180° around X-axis for better print orientation
mold_cut_obj.Placement = App.Placement(
    Base.Vector(0, 0, 0),
    App.Rotation(Base.Vector(1, 0, 0), 180)
)

# Set visibility
hex_cut.ViewObject.Visibility = True
fused_obj.ViewObject.Visibility = True
mold_cut_obj.ViewObject.Visibility = False


# ─── Final recompute & auto-zoom ───────────────────────────────────────────────
doc.recompute()
Gui.SendMsgToActiveView("ViewFit")

