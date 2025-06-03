import FreeCAD as App
import FreeCADGui as Gui
import Part, math
from FreeCAD import Base

# ─── New document ──────────────────────────────────────────────────────────────
doc = App.newDocument("Torange")

# ─── Parameters you probably don't want to touch ───────────────────────────────
INCH            = 25.4               # mm per inch
interior_angles = [72, 108] * 2      # rhombus angles [72°,108°]×2
n_sides         = 4
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

# ─── 1) Walk the perimeter to get 2D profile ───────────────────────────────────
verts = [Base.Vector(-side/2, 0, 0)]
direction = 144
for angle in interior_angles:
    last = verts[-1]
    rad  = math.radians(direction)
    step = Base.Vector(side * math.cos(rad),
                       side * math.sin(rad),
                       0)
    verts.append(last.add(step))
    # turn inward by (180 - interior)
    direction -= (180 - angle)


# drop the duplicated last point
verts = verts[:-1]

# ─── 2) Re-center on origin ───────────────────────────────────────────────────
cx = sum(v.x for v in verts) / n_sides
cy = sum(v.y for v in verts) / n_sides
verts = [Base.Vector(v.x - cx, v.y - cy, 0) for v in verts]

# ─── 3) Build & extrude the tile face ──────────────────────────────────────────
wire      = Part.makePolygon(verts + [verts[0]])
face      = Part.Face(wire)
tile_solid = face.extrude(Base.Vector(0, 0, THICK - RECESS))
tile_obj   = doc.addObject("Part::Feature", "UncutTile")
tile_obj.Shape = tile_solid


def make_prism(L, rot, base, half1=False, half2=False):
    # choose the “cut angle” on each end
    ANG1 = ANG*0.5 if half1 else ANG
    ANG2 = ANG*0.5 if half2 else ANG

    # correctly compute both betas
    β1  = math.radians(ANG1)
    β2  = math.radians(ANG2)

    hw  = WIDTH/2
    C1  = (L/2)*math.cos(β1)
    C2  = (L/2)*math.cos(β2)

    # now corner X’s for y = ±hw
    x1 = ( C2 +  hw*math.sin(β2)) / math.cos(β2)
    x2 = ( C2 -  hw*math.sin(β2)) / math.cos(β2)
    x3 = (-C1 +  hw*math.sin(β1)) / math.cos(β1)
    x4 = (-C1 -  hw*math.sin(β1)) / math.cos(β1)

    verts = [
      Base.Vector(x1, -hw, 0),
      Base.Vector(x2, +hw, 0),
      Base.Vector(x3, +hw, 0),
      Base.Vector(x4, -hw, 0),
    ]

    wire  = Part.makePolygon(verts + [verts[0]])
    face  = Part.Face(wire)
    prism = face.extrude(Base.Vector(0, 0, RECESS+EMBEDDING))

    prism.rotate(Base.Vector(0,0,0), Base.Vector(0,0,1), rot)
    prism.translate(Base.Vector(*base))
    return prism


#L1_x = 0.5*side*math.cos(math.radians(36))  # Half of one side X distance
#L1_y = 0.5*(side*math.sin(math.radians(36))) # Origin to halfway down side Y distance
L1= side*math.sin(math.radians(36)) # Length of longer lines (meeting edges on both ends)
L2 = 0.5*side*math.cos(math.radians(36))/math.cos(math.radians(18))
#Length of line at which midpoints touch
#L2_m= math.sqrt(L2_x*L2_x+L2_y*L2_y) # Length of shorter lines (meeting edges on one end)
#Extend line so edges touch
#L2 = L2_m + (0.5*WIDTH/math.cos(math.radians(36)))*math.sin(math.radians(54))/math.sin(math.radians(72))

#Adjust the line midpoint because we made it longer
#dx = (L2 - L2_m) * math.cos(math.radians(72))/2
#dy = (L2 - L2_m) * math.sin(math.radians(72))/2
p1 = make_prism(L1,90,(-0.5*side*math.cos(math.radians(36)) , 0 , 0))
p2 = make_prism(L2,-18,(-0.25*side*math.cos(math.radians(36)), 0.5*L1 - 0.5*L2*math.sin(math.radians(18)) ,0),half2=True)
p3 = make_prism(L2,18,(0.25*side*math.cos(math.radians(36)), 0.5*L1 - 0.5*L2*math.sin(math.radians(18)) ,0),half1=True)
p4 = make_prism(L1,-90,(0.5*side*math.cos(math.radians(36)) , 0 , 0))
p5 = make_prism(L2,162,(0.25*side*math.cos(math.radians(36)), -0.5*L1 + 0.5*L2*math.sin(math.radians(18)) ,0),half2=True)
p6 = make_prism(L2,198,(-0.25*side*math.cos(math.radians(36)), -0.5*L1 + 0.5*L2*math.sin(math.radians(18)) ,0),half1=True)

shapes = [p1,p2,p3,p4,p5,p6]

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
tile_cut = doc.addObject("Part::Cut", "BaseTile")
tile_cut.Base = tile_obj
tile_cut.Tool = cut_feature_copy
tile_cut.ViewObject.ShapeColor = (TILE_COLOR[0]/255, TILE_COLOR[1]/255, TILE_COLOR[2]/255)

# 2) Make a compound of the cut result and the cutter itself
group = doc.addObject("App::DocumentObjectGroup", "Torange")

# 2) Add both objects to it
group.addObject(tile_cut)
group.addObject(fused_obj)


# ─── Create a diamond-shaped mold from offset tile profile ─────────────────────

# Make copies of the tile and filigree
tile_copy = App.ActiveDocument.copyObject(tile_cut, False)
fused_copy = App.ActiveDocument.copyObject(fused_obj, False)

# Fuse the copies for clean subtraction
tile_fusion = doc.addObject("Part::MultiFuse", "TileFusion")
tile_fusion.Shapes = [tile_copy, fused_copy]

doc.recompute()  # Ensure bounding box and geometry are up to date

mold_side = side + MOLD_BUFFER
mold_verts = [Base.Vector(-mold_side/2, 0, 0)]
direction = 144
for angle in interior_angles:
    last = mold_verts[-1]
    rad  = math.radians(direction)
    step = Base.Vector(mold_side * math.cos(rad),
                       mold_side * math.sin(rad),
                       0)
    mold_verts.append(last.add(step))
    # turn inward by (180 - interior)
    direction -= (180 - angle)


# drop the duplicated last point
mold_verts = mold_verts[:-1]

# ─── 2) Re-center on origin ───────────────────────────────────────────────────
cx = sum(v.x for v in mold_verts) / n_sides
cy = sum(v.y for v in mold_verts) / n_sides
mold_verts = [Base.Vector(v.x - cx, v.y - cy, 0) for v in mold_verts]

# ─── 3) Build & extrude the tile face ──────────────────────────────────────────
mold_wire      = Part.makePolygon(mold_verts + [mold_verts[0]])
mold_face      = Part.Face(mold_wire)
mold_solid = mold_face.extrude(Base.Vector(0, 0, THICK+MOLD_BUFFER))
mold_outer_obj = doc.addObject("Part::Feature", "MoldOuter")
mold_outer_obj.Shape = mold_solid

# Cut the tile + filigree fusion from the mold shape
mold_cut_obj = doc.addObject("Part::Cut", "MoldWithCavity")
mold_cut_obj.Base = mold_outer_obj
mold_cut_obj.Tool = tile_fusion
mold_cut_obj.ViewObject.ShapeColor = (0.5, 0.5, 0.5)

# Flip vertically for printability
mold_cut_obj.Placement = App.Placement(
    Base.Vector(0, 0, 0),
    App.Rotation(Base.Vector(1, 0, 0), 180)
)

# Set visibility: show tile and filigree, hide mold
tile_cut.ViewObject.Visibility = True
fused_obj.ViewObject.Visibility = True
mold_cut_obj.ViewObject.Visibility = False


# ─── 5) Style & fit view ──────────────────────────────────────────────────────
#tile_obj.ViewObject.ShapeColor = (94/255, 140/255, 125/255)  # #5e8c7d
doc.recompute()
Gui.SendMsgToActiveView("ViewFit")

