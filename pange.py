import FreeCAD as App
import FreeCADGui as Gui
import Part, math
from FreeCAD import Base

# ─── New document ──────────────────────────────────────────────────────────────
doc = App.newDocument("Pange")

# ─── Parameters you probably don't want to touch ───────────────────────────────
INCH       = 25.4               # mm per inch
n_sides    = 5                  # regular pentagon
ANG       = 36.0             # end-cut angle from perpendicular

# ─── Parameters ────────────────────────────────────────────────────────────────
side            = 2.0 * INCH        # 2″ side length
THICK           = 0.3 * INCH        # tile thickness
RECESS          = 0.05 * INCH       # 1 mm recess
EMBEDDING       = 0.05 * INCH       # Embedding of lines into tile
WIDTH           = 0.25  * INCH      # groove width
MOLD_BUFFER     = 0.25 * INCH       # Min. thickness of mold
LINE_COLOR = (171, 133, 70)     # rgb in decimal vector
TILE_COLOR = (94, 140, 125)     # rgb (decimal)

# ─── Compute circumradius ──────────────────────────────────────────────────────
R = side / (2 * math.sin(math.pi / n_sides))

# ─── Build pentagon vertices with bottom edge horizontal ──────────────────────
# original flat‐top start: π/2 + π/5 ; add π to flip it
start_angle = math.pi/2 + math.pi/n_sides + math.pi
verts = []
for i in range(n_sides):
    θ = start_angle + 2*math.pi*i/n_sides
    verts.append(Base.Vector(R * math.cos(θ),
                             R * math.sin(θ),
                             0))

# ─── 2D wire & face, then extrude with recess ──────────────────────────────────
wire       = Part.makePolygon(verts + [verts[0]])
face       = Part.Face(wire)
tile_solid = face.extrude(Base.Vector(0, 0, THICK - RECESS))

# ─── Create and display the flipped tile feature ───────────────────────────────
tile_obj = doc.addObject("Part::Feature", "PangeTile_Flipped")
tile_obj.Shape = tile_solid
tile_obj.ViewObject.ShapeColor = (
    TILE_COLOR[0]/255,
    TILE_COLOR[1]/255,
    TILE_COLOR[2]/255
)

apothem = side / (2 * math.tan(math.pi/5))

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

# The line from the midpoint and the (imaginary) line from the corner to the
# center where the actual line ends form a symmetric triangle with inner angles
# of 54 degrees.  So the length of the line is just the length it takes for the 
# line to cover half of the horizontal distance of the side.

L = 0.25*side/math.cos(math.radians(54))

p1 = make_prism(L,126,(-0.125*side , -apothem+0.5*L*math.sin(math.radians(54)) , 0),half2=True)
p2 = make_prism(L,162,(-apothem*math.cos(math.radians(18)) + 0.5*L*math.cos(math.radians(18)) , -apothem*math.sin(math.radians(18)) -0.5*L*math.sin(math.radians(18)) , 0),half1=True)
p3 = make_prism(L,54,(-apothem*math.cos(math.radians(18)) + 0.5*L*math.cos(math.radians(54)) , -apothem*math.sin(math.radians(18)) +0.5*L*math.sin(math.radians(54)) , 0),half2=True)
p4 = make_prism(L,90,(-apothem*math.cos(math.radians(54)) + 0.5*L*math.cos(math.radians(90)) , apothem*math.sin(math.radians(54)) -0.5*L*math.sin(math.radians(90)) , 0),half1=True)
p5 = make_prism(L,-18,(-apothem*math.cos(math.radians(54)) + 0.5*L*math.cos(math.radians(18)) , apothem*math.sin(math.radians(54)) -0.5*L*math.sin(math.radians(18)) , 0),half2=True)
p6 = make_prism(L,18,(apothem*math.cos(math.radians(54)) - 0.5*L*math.cos(math.radians(18)) , apothem*math.sin(math.radians(54)) -0.5*L*math.sin(math.radians(18)) , 0),half1=True)
p7 = make_prism(L,-90,(apothem*math.cos(math.radians(54)) - 0.5*L*math.cos(math.radians(90)) , apothem*math.sin(math.radians(54)) -0.5*L*math.sin(math.radians(90)) , 0),half2=True)
p8 = make_prism(L,-54,(apothem*math.cos(math.radians(18)) - 0.5*L*math.cos(math.radians(54)) , -apothem*math.sin(math.radians(18)) +0.5*L*math.sin(math.radians(54)) , 0),half1=True)
p9 = make_prism(L,-162,(apothem*math.cos(math.radians(18)) - 0.5*L*math.cos(math.radians(18)) , -apothem*math.sin(math.radians(18)) -0.5*L*math.sin(math.radians(18)) , 0),half2=True)
p10 = make_prism(L,-126,(0.125*side , -apothem+0.5*L*math.sin(math.radians(54)) , 0),half1=True)

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
tile_cut = doc.addObject("Part::Cut", "BaseTile")
tile_cut.Base = tile_obj
tile_cut.Tool = cut_feature_copy
tile_cut.ViewObject.ShapeColor = (TILE_COLOR[0]/255, TILE_COLOR[1]/255, TILE_COLOR[2]/255)

# 2) Make a compound of the cut result and the cutter itself
group = doc.addObject("App::DocumentObjectGroup", "Pange")

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
# ─── Compute circumradius ──────────────────────────────────────────────────────
mold_R = mold_side / (2 * math.sin(math.pi / n_sides))

# ─── Build pentagon vertices with bottom edge horizontal ──────────────────────
# original flat‐top start: π/2 + π/5 ; add π to flip it
start_angle = math.pi/2 + math.pi/n_sides + math.pi
mold_verts = []
for i in range(n_sides):
    θ = start_angle + 2*math.pi*i/n_sides
    mold_verts.append(Base.Vector(mold_R * math.cos(θ),
                             mold_R * math.sin(θ),
                             0))

# ─── 2D wire & face, then extrude with recess ──────────────────────────────────
mold_wire       = Part.makePolygon(mold_verts + [mold_verts[0]])
mold_face       = Part.Face(mold_wire)
mold_solid = mold_face.extrude(Base.Vector(0, 0, THICK  + MOLD_BUFFER))
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




# ─── Final recompute & fit view ───────────────────────────────────────────────
doc.recompute()
Gui.SendMsgToActiveView("ViewFit")

