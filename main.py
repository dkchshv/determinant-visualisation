# the input file should be prepared by hand to avoid including unnecessary triangles

file_lines = open("input.txt").readlines()

class vector_point:
	x: float
	y: float
	z: float

	@property
	def magnitude(self):
		return (self.x**2 + self.y**2 + self.z**2)**0.5

	def __init__(self, *args):
		if len(args) == 3:
			self.x = args[0]
			self.y = args[1]
			self.z = args[2]
		elif len(args) == 1:
			self.x = args[0].x
			self.y = args[0].y
			self.z = args[0].z

	def __str__(self):
		return f"({self.x}, {self.y}, {self.z})"

	def __neg__(self):
		return vector_point(-self.x, -self.y, -self.z)

	def __add__(self, second: vector_point):
		return vector_point(
			self.x + second.x, 
			self.y + second.y, 
			self.z + second.z
		)

	def __sub__(self, second: vector_point):
		return self + (-second)

	def __mul__(self, second):
		return vector_point(
			self.x * second,
			self.y * second,
			self.z * second,
		)

	def __rmul__(self, second):
		return vector_point(
			self.x * second,
			self.y * second,
			self.z * second,
		)
	
	def __hash__(self):
		return hash((self.x, self.y, self.z))
	
	def __eq__(self, second):
		if not isinstance(second, vector_point):
			return False
		
		return (self.x == second.x) and (self.y == second.y) and (self.z == second.z)

################################################################################################################################

# setting up the basis vectors
A = vector_point(8, 3.2, 1.27)
B = vector_point(2.1, 8, 1.67)
C = vector_point(2.7, 2.05, 9.3)

#converting auxillary vectors from Desmos3D TeX format to Python
O = vector_point(0, 0, 0)
v1 = -C + vector_point(A.x + B.x + C.x, A.y + B.y + C.y, 0)
v2 = -(A + C) + vector_point(0, (A + B + C).y, 0)

################################################################################################################################

def prepare_stl_triangle(triangle, mass_center):
	triangle_pointA = triangle[0]
	triangle_pointB = triangle[1]
	triangle_pointC = triangle[2]

	triangle_vectorAB = triangle_pointB - triangle_pointA
	triangle_vectorAC = triangle_pointC - triangle_pointA

	vector_productABxAC = vector_point(
		triangle_vectorAB.y * triangle_vectorAC.z - triangle_vectorAC.y * triangle_vectorAB.z,
		triangle_vectorAC.x * triangle_vectorAB.z - triangle_vectorAB.x * triangle_vectorAC.z,
		triangle_vectorAB.x * triangle_vectorAC.y - triangle_vectorAC.x * triangle_vectorAB.y
	)

	normal = vector_productABxAC * (1 / vector_productABxAC.magnitude)

	outwards_direction = triangle_pointA - mass_center

	scalar_product = vector_productABxAC.x * outwards_direction.x + \
		vector_productABxAC.y * outwards_direction.y + \
		vector_productABxAC.z * outwards_direction.z

	# if order is wrong and should be fixed to match vector_productABxAC
	if scalar_product < 0:
		# changing order to match vector_productABxAC
		
		triangle = (triangle[1], triangle[0], triangle[2])
		
		# updating points of the triangle
		triangle_pointA = triangle[0]
		triangle_pointB = triangle[1]
		triangle_pointC = triangle[2]
		
		#negating normal to match correct outerwards direction
		normal = normal * (-1)

	return (
		f" facet normal {normal.x} {normal.y} {normal.z}\n"
		"  outer loop\n"
		f"   vertex {triangle_pointA.x} {triangle_pointA.y} {triangle_pointA.z}\n"
		f"   vertex {triangle_pointB.x} {triangle_pointB.y} {triangle_pointB.z}\n"
		f"   vertex {triangle_pointC.x} {triangle_pointC.y} {triangle_pointC.z}\n"
		"  endloop\n"
		" endfacet\n"
	)

def prepare_stl_file(solid_name, triangles_lines):
	return (
		f"solid {solid_name}\n"
		f"{triangles_lines}"
		f"endsolid {solid_name}"
	)

def get_mass_center(solid_vertecies):
	mass_center = O

	for v in solid_vertecies:
		mass_center += v

	mass_center *= 1 / len(solid_vertecies)

	return mass_center

def get_solid_verticies(solid_triangles):
	solid_vertecies = set()
	
	for triangle_i in set(current_solid_triangles):
		vertexA = triangle_i[0]
		vertexB = triangle_i[1]
		vertexC = triangle_i[2]
		
		solid_vertecies.add(vertexA)
		solid_vertecies.add(vertexB)
		solid_vertecies.add(vertexC)
	
	print(len(solid_vertecies), len(solid_triangles) * 3)
	
	return solid_vertecies

def get_stl_solid_ascii(solid_triangles, mass_center):
	triangles_lines = ""
			
	for triangle in current_solid_triangles:
		triangles_lines += prepare_stl_triangle(triangle, mass_center)
	
	return triangles_lines

solid_name = ""
current_solid_triangles = []
names = []

for line in file_lines:
	if ("Folder" in line):
		if (solid_name != ""):
			solid_vertecies = get_solid_verticies(current_solid_triangles)

			mass_center = get_mass_center(solid_vertecies)

			triangles_lines = get_stl_solid_ascii(current_solid_triangles, mass_center)

			with open(f"{solid_name}.stl", "w", encoding="utf-8") as new_solid_file:
				new_solid_file.write(prepare_stl_file(solid_name, triangles_lines))
			
			current_solid_triangles = []
			names.append(solid_name)

		solid_name = line.split(' ')[1].strip()
		print(f"\n============ FOLDER {solid_name} ============\n")

	if ("triangle" in line):
		line_backup = line
		# removing garbage
		line = line.replace("\\operatorname{triangle}", "")
		line = line.replace("\\left", "")
		line = line.replace("\\right", "")
		line = line.replace("\\", "")

		# forcing animation slider $m$ to 0 and preparing auxillary vectors to be executable by Python's `eval()`
		line = line.replace("m", "0*")
		line = line.replace("v_{1}", "v1")
		line = line.replace("v_{2}", "v2")

		# removing side parentheses and converting Desmos3D vectors to Python vectors, then bringing back side parentheses to get a touple as output
		line = line[1:len(line) - 2]
		line = line.replace("(", "vector_point(")
		
		# bringing back side parentheses
		line = '(' + line + ')'

		#getting Python-ready triangle - a touple of points
		triangle = eval(line)
		
		current_solid_triangles.append(triangle)
