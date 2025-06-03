import FreeCAD as App
import FreeCADGui as Gui
import Part, math
from FreeCAD import Base

# ─── New document ──────────────────────────────────────────────────────────────
doc = App.newDocument("Tabl")

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

# ─── Compute circumradius and diameter ─────────────────────────────────────────
n_sides   = 10                 # decagon
decagon_radius         = side / (2 * math.sin(math.pi / n_sides))
diameter  = 2 * decagon_radius
apothem = side / (2 * math.tan(math.pi / n_sides))
#L = 2*apothem*math.sin(math.radians(54))

start_angle = math.pi/2 + math.pi/n_sides
verts = []
for i in range(n_sides):
    θ = start_angle + 2 * math.pi * i / n_sides
    verts.append(Base.Vector(decagon_radius * math.cos(θ), decagon_radius * math.sin(θ), 0))

# ─── Build the face and add it as a feature ─────────────────────────────────────
wire = Part.makePolygon(verts + [verts[0]])
face = Part.Face(wire)
# Make this 1 mm thinner so the line always shows through
dec_solid = face.extrude(Base.Vector(0, 0, THICK-RECESS))
dec_obj   = doc.addObject("Part::Feature", "RawBaseTile")
dec_obj.Shape = dec_solid

#apothem = side / (2 * math.tan(math.pi/5))

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

#L = 0.25*side/math.cos(math.radians(54))
#apothem = side / (2 * math.tan(math.pi / n_sides))
#L = 2*apothem*math.sin(math.radians(54))
L = 0.5*apothem/math.cos(math.radians(36))


p1 = make_prism(L,126,(-L*math.cos(math.radians(54))/2 , -apothem+0.5*L*math.sin(math.radians(54)) , 0),half2=True)
p2 = make_prism(L,162,(-apothem*math.cos(math.radians(18)) + 0.5*L*math.cos(math.radians(18)) , -apothem*math.sin(math.radians(18)) -0.5*L*math.sin(math.radians(18)) , 0),half1=True)
p3 = make_prism(L,54,(-apothem*math.cos(math.radians(18)) + 0.5*L*math.cos(math.radians(54)) , -apothem*math.sin(math.radians(18)) +0.5*L*math.sin(math.radians(54)) , 0),half2=True)
p4 = make_prism(L,90,(-apothem*math.cos(math.radians(54)) + 0.5*L*math.cos(math.radians(90)) , apothem*math.sin(math.radians(54)) -0.5*L*math.sin(math.radians(90)) , 0),half1=True)
p5 = make_prism(L,-18,(-apothem*math.cos(math.radians(54)) + 0.5*L*math.cos(math.radians(18)) , apothem*math.sin(math.radians(54)) -0.5*L*math.sin(math.radians(18)) , 0),half2=True)
p6 = make_prism(L,18,(apothem*math.cos(math.radians(54)) - 0.5*L*math.cos(math.radians(18)) , apothem*math.sin(math.radians(54)) -0.5*L*math.sin(math.radians(18)) , 0),half1=True)
p7 = make_prism(L,-90,(apothem*math.cos(math.radians(54)) - 0.5*L*math.cos(math.radians(90)) , apothem*math.sin(math.radians(54)) -0.5*L*math.sin(math.radians(90)) , 0),half2=True)
p8 = make_prism(L,-54,(apothem*math.cos(math.radians(18)) - 0.5*L*math.cos(math.radians(54)) , -apothem*math.sin(math.radians(18)) +0.5*L*math.sin(math.radians(54)) , 0),half1=True)
p9 = make_prism(L,-162,(apothem*math.cos(math.radians(18)) - 0.5*L*math.cos(math.radians(18)) , -apothem*math.sin(math.radians(18)) -0.5*L*math.sin(math.radians(18)) , 0),half2=True)
p10 = make_prism(L,-126,(L*math.cos(math.radians(54))/2 , -apothem+0.5*L*math.sin(math.radians(54)) , 0),half1=True)

p11 = make_prism(L,54,(-L*math.cos(math.radians(54))/2 , apothem-0.5*L*math.sin(math.radians(54)) , 0),half1=True)
p12 = make_prism(L,18,(-apothem*math.cos(math.radians(18)) + 0.5*L*math.cos(math.radians(18)) , apothem*math.sin(math.radians(18)) +0.5*L*math.sin(math.radians(18)) , 0),half2=True)
p13 = make_prism(L,126,(-apothem*math.cos(math.radians(18)) + 0.5*L*math.cos(math.radians(54)) , apothem*math.sin(math.radians(18)) -0.5*L*math.sin(math.radians(54)) , 0),half1=True)
p14 = make_prism(L,90,(-apothem*math.cos(math.radians(54)) + 0.5*L*math.cos(math.radians(90)) , -apothem*math.sin(math.radians(54)) +0.5*L*math.sin(math.radians(90)) , 0),half2=True)
p15 = make_prism(L,198,(-apothem*math.cos(math.radians(54)) + 0.5*L*math.cos(math.radians(18)) , -apothem*math.sin(math.radians(54)) +0.5*L*math.sin(math.radians(18)) , 0),half1=True)
p16 = make_prism(L,162,(apothem*math.cos(math.radians(54)) - 0.5*L*math.cos(math.radians(18)) , -apothem*math.sin(math.radians(54)) +0.5*L*math.sin(math.radians(18)) , 0),half2=True)
p17 = make_prism(L,-90,(apothem*math.cos(math.radians(54)) - 0.5*L*math.cos(math.radians(90)) , -apothem*math.sin(math.radians(54)) +0.5*L*math.sin(math.radians(90)) , 0),half1=True)
p18 = make_prism(L,234,(apothem*math.cos(math.radians(18)) - 0.5*L*math.cos(math.radians(54)) , apothem*math.sin(math.radians(18)) -0.5*L*math.sin(math.radians(54)) , 0),half2=True)
p19 = make_prism(L,-18,(apothem*math.cos(math.radians(18)) - 0.5*L*math.cos(math.radians(18)) , apothem*math.sin(math.radians(18)) +0.5*L*math.sin(math.radians(18)) , 0),half1=True)
p20 = make_prism(L,-54,(L*math.cos(math.radians(54))/2 , apothem-0.5*L*math.sin(math.radians(54)) , 0),half2=True)



shapes = [p1,p2,p3,p4,p5,p6,p7,p8,p9,p10,p11,p12,p13,p14,p15,p16,p17,p18,p19,p20]

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
tile_cut.Base = dec_obj
tile_cut.Tool = cut_feature_copy
tile_cut.ViewObject.ShapeColor = (TILE_COLOR[0]/255, TILE_COLOR[1]/255, TILE_COLOR[2]/255)

# 2) Make a compound of the cut result and the cutter itself
group = doc.addObject("App::DocumentObjectGroup", "Tabl")

# 2) Add both objects to it
group.addObject(tile_cut)
group.addObject(fused_obj)

# ─── Create a cylindrical mold that includes tile and filigree ────────────────
mold_radius = decagon_radius + MOLD_BUFFER
mold_height = THICK + MOLD_BUFFER

# Create outer mold cylinder as a Part Feature
mold_outer = Part.makeCylinder(mold_radius, mold_height)
mold_outer_obj = doc.addObject("Part::Feature", "MoldOuter")
mold_outer_obj.Shape = mold_outer

# Fuse the tile and the filigree so that the cut works properly
tile_fusion = doc.addObject("Part::MultiFuse", "TileFusion")
tile_fusion.Shapes = [tile_cut, fused_obj]

# Create the cut: subtract tile + filigree from the cylinder
mold_cut_obj = doc.addObject("Part::Cut", "MoldWithCavity")
mold_cut_obj.Base = mold_outer_obj
mold_cut_obj.Tool = tile_fusion
mold_cut_obj.ViewObject.ShapeColor = (0.5, 0.5, 0.5)  # neutral gray

tile_cut.ViewObject.Visibility = True
fused_obj.ViewObject.Visibility = True
mold_cut_obj.ViewObject.Visibility = False

mold_cut_obj.Placement = App.Placement(
    Base.Vector(0, 0, 0),
    App.Rotation(Base.Vector(1, 0, 0), 180)
)

# ─── Final recompute & fit view ───────────────────────────────────────────────
doc.recompute()
Gui.SendMsgToActiveView("ViewFit")

