import FreeCAD as App
import FreeCADGui as Gui
import Part, math
from FreeCAD import Base

# ─── New document ──────────────────────────────────────────────────────────────
doc = App.newDocument("SormehDan")

# ─── Parameters you probably don't want to touch ───────────────────────────────
INCH            = 25.4               # mm per inch
interior_angles = [72, 72, 216] * 2   # bow-tie hexagon pattern
n_sides         = 6
ANG       = 36.0             # end-cut angle from perpendicular

# ─── Parameters ────────────────────────────────────────────────────────────────
side            = 2.0 * INCH        # 2″ side length
THICK           = 0.3 * INCH        # tile thickness
RECESS          = 0.05 * INCH       # 1 mm recess
EMBEDDING       = 0.05 * INCH       # Embedding of lines into tile
WIDTH           = 0.25  * INCH      # groove width
MOLD_BUFFER     = 0.25 * INCH       # Min. thickness of mold
LINE_COLOR      = (171, 133, 70)     # rgb in decimal vector
TILE_COLOR      = (94, 140, 125)     # rgb in decimal vector

# ─── 1) Walk around the edges to get the 2D profile ───────────────────────────
verts = [Base.Vector(-side/2, 0, 0)]
direction = 18
for angle in interior_angles:
    last = verts[-1]
    rad = math.radians(direction)
    step = Base.Vector(side * math.cos(rad), side * math.sin(rad), 0)
    verts.append(last.add(step))
    direction -= (180 - angle)
    

verts = verts[:-1]  # drop duplicate final point

# ─── 2) Re-center the polygon at the origin ────────────────────────────────────
cx = sum(v.x for v in verts) / n_sides
cy = sum(v.y for v in verts) / n_sides
verts = [Base.Vector(v.x - cx, v.y - cy, 0) for v in verts]

# ─── 3) Extrude the 2D face into a 3D tile ────────────────────────────────────
poly_wire  = Part.makePolygon(verts + [verts[0]])
poly_face  = Part.Face(poly_wire)
tile_solid = poly_face.extrude(Base.Vector(0, 0, THICK-RECESS))
tile_obj   = doc.addObject("Part::Feature", "SormehDanTile")
tile_obj.Shape = tile_solid

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


L1_x = 0.5*side*math.cos(math.radians(18))  # Half of one side X distance
L1_y = 0.5*(side-side*math.sin(math.radians(18))) # Origin to halfway down side Y distance
L2_y = L1_y#*math.sin(math.radians(36))/math.sin(math.radians(72))
L2_x = L2_y*math.cos(math.radians(72))/math.sin(math.radians(72))
L1= math.sqrt(L1_x*L1_x+L1_y*L1_y) # Length of longer lines (meeting edges on both ends)
#Length of line at which midpoints touch
L2_m= math.sqrt(L2_x*L2_x+L2_y*L2_y) # Length of shorter lines (meeting edges on one end)
#Extend line so edges touch
L2 = L2_m + (0.5*WIDTH/math.cos(math.radians(36)))*math.sin(math.radians(54))/math.sin(math.radians(72))

#Adjust the line midpoint because we made it longer
dx = (L2 - L2_m) * math.cos(math.radians(72))/2
dy = (L2 - L2_m) * math.sin(math.radians(72))/2
p1 = make_prism(L1,144,(-1.5*L1_x,-0.5*L1_y,0))
p2 = make_prism(L1,36,(-1.5*L1_x,0.5*L1_y,0))
p3 = make_prism(L2, -108, (-L1_x + 0.5*L2_x + dx, -0.5*L1_y + dy, 0))
p4 = make_prism(L2,-72,(-L1_x + 0.5*L2_x + dx,0.5*L1_y-dy,0))

def mirror_prism(prism):
    shp = prism.copy()
    # mirror by scaling X by -1:
    mirror_mat = Base.Matrix()
    mirror_mat.A11 = -1  # flip X
    shp.transformShape(mirror_mat)
    return shp

# Create mirrored prisms
p5 = mirror_prism(p4)  # mirror of p4
p6 = mirror_prism(p3)  # mirror of p3
p7 = mirror_prism(p2)  # mirror of p2
p8 = mirror_prism(p1)  # mirror of p1


#The two sets of lines are not contiguous so we have to make two separate fusions
shapes1 = [p1,p2,p3,p4]
shapes2 = [p5,p6,p7,p8]

fused1 = shapes1[0]
for s in shapes1[1:]:
    fused1 = fused1.fuse(s)


fused1 = fused1.removeSplitter()

fused2 = shapes2[0]
for s in shapes2[1:]:
    fused2 = fused2.fuse(s)


fused2 = fused2.removeSplitter()

fused_obj1 = App.ActiveDocument.addObject("Part::Feature", "Filigree1")
fused_obj1.Shape = fused1
fused_obj1.ViewObject.ShapeColor = (LINE_COLOR[0]/255, LINE_COLOR[1]/255,  LINE_COLOR[2]/255)
fused_obj1.Placement = App.Placement(
    Base.Vector(0, 0, THICK-RECESS-EMBEDDING),               
    Base.Rotation(Base.Vector(0,0,0), 0)
)
fused_obj2 = App.ActiveDocument.addObject("Part::Feature", "Filigree2")
fused_obj2.Shape = fused2
fused_obj2.ViewObject.ShapeColor = (LINE_COLOR[0]/255, LINE_COLOR[1]/255,  LINE_COLOR[2]/255)
fused_obj2.Placement = App.Placement(
    Base.Vector(0, 0, THICK-RECESS-EMBEDDING),               
    Base.Rotation(Base.Vector(0,0,0), 0)
)
cut_feature_copy1 = App.ActiveDocument.copyObject(fused_obj1, False)
cut_feature_copy2 = App.ActiveDocument.copyObject(fused_obj2, False)
#cutter_copy.Label = "ChainBooleanCut_Copy"
tile_cut1 = doc.addObject("Part::Cut", "BowtieMinusPattern1")
tile_cut1.Base = tile_obj
tile_cut1.Tool = cut_feature_copy1
#tile_cut1.ViewObject.ShapeColor = (TILE_COLOR[0]/255, TILE_COLOR[1]/255, TILE_COLOR[2]/255)

tile_cut2 = doc.addObject("Part::Cut", "BaseTile")
tile_cut2.Base = tile_cut1
tile_cut2.Tool = cut_feature_copy2
tile_cut2.ViewObject.ShapeColor = (TILE_COLOR[0]/255, TILE_COLOR[1]/255, TILE_COLOR[2]/255)


# 2) Make a compound of the cut result and the cutter itself
group = doc.addObject("App::DocumentObjectGroup", "SormehDan")

# 2) Add both objects to it
group.addObject(tile_cut2)
group.addObject(fused_obj1)
group.addObject(fused_obj2)

# ─── Create a rectangular mold box around the tile and both filigree layers ────

# Fuse the tile and both filigree elements
tile_fusion = doc.addObject("Part::MultiFuse", "TileFusion")
tile_fusion.Shapes = [App.ActiveDocument.copyObject(tile_cut2, False), App.ActiveDocument.copyObject(fused_obj1, False), App.ActiveDocument.copyObject(fused_obj2, False)]

# Recompute so that bounding box is accurate
doc.recompute()

bbox = tile_fusion.Shape.BoundBox
min_x, max_x = bbox.XMin, bbox.XMax
min_y, max_y = bbox.YMin, bbox.YMax
min_z, max_z = bbox.ZMin, bbox.ZMax

# Expand the bounding box by ¼″ in all directions
mold_x = (max_x - min_x) + 2 * MOLD_BUFFER
mold_y = (max_y - min_y) + 2 * MOLD_BUFFER
mold_z = (max_z - min_z) + MOLD_BUFFER  # Only one buffer on top (tile starts at z=0)

# Create and position the mold box
mold_box = Part.makeBox(mold_x, mold_y, mold_z)
mold_box.translate(Base.Vector(min_x - MOLD_BUFFER, min_y - MOLD_BUFFER, 0))

mold_outer_obj = doc.addObject("Part::Feature", "MoldOuter")
mold_outer_obj.Shape = mold_box

# Cut the fused tile + filigree from the box using Part::Cut
mold_cut_obj = doc.addObject("Part::Cut", "MoldWithCavity")
mold_cut_obj.Base = mold_outer_obj
mold_cut_obj.Tool = tile_fusion
mold_cut_obj.ViewObject.ShapeColor = (0.5, 0.5, 0.5)

# Flip mold vertically (rotate 180° around X axis)
mold_cut_obj.Placement = App.Placement(
    Base.Vector(0, 0, 0),
    App.Rotation(Base.Vector(1, 0, 0), 180)
)

# Set visibility: show tile and filigree, hide mold
tile_cut2.ViewObject.Visibility = True
fused_obj1.ViewObject.Visibility = True
fused_obj2.ViewObject.Visibility = True
mold_cut_obj.ViewObject.Visibility = False


# ─── Final recompute & auto-zoom ───────────────────────────────────────────────
doc.recompute()
Gui.SendMsgToActiveView("ViewFit")

