# Heightmap Generator by Travis Martin
import os.path
import time
from pathlib import Path
from PIL import Image

# Vertex object.
class Vertex:
	def __init__(self, x, y, z, identifier):
		if not isinstance(x, float):
			raise TypeError('x must be a float.')
		if not isinstance(y, float):
			raise TypeError('y must be a float.')
		if not isinstance(z, float):
			raise TypeError('z must be a float.')
		if not isinstance(identifier, int):
			raise TypeError('identifier must be an integer.')

		self.x = x # X in Blender.
		self.y = y # Z in Blender (height).
		self.z = z # Y in Blender.
		self.identifier = identifier

	def __str__(self):
		return '(' + str(self.x) + ', ' + str(self.y) + ', ' + str(self.z) + ') #' + str(self.identifier)

# Face object.
class Face:
	def __init__(self, vertices):
		if not isinstance(vertices, list):
			raise TypeError('vertices must be a list.')
		for vertex in vertices:
			if not isinstance(vertex, Vertex):
				raise TypeError('vertices must contain only Vertices.')

		self.vertices = vertices

	def __str__(self):
		return 'Face\tX: ' + str(self.minimum_x()) + ' - ' + str(self.maximum_x()) + '\tZ: ' + str(self.minimum_z()) + ' - ' + str(self.maximum_z())

	def maximum_x(self):
		value = self.vertices[0].x
		for vertex in self.vertices:
			if vertex.x > value:
				value = vertex.x
		return value

	def minimum_x(self):
		value = self.vertices[0].x
		for vertex in self.vertices:
			if vertex.x < value:
				value = vertex.x
		return value

	def maximum_z(self):
		value = self.vertices[0].z
		for vertex in self.vertices:
			if vertex.z > value:
				value = vertex.z
		return value

	def minimum_z(self):
		value = self.vertices[0].z
		for vertex in self.vertices:
			if vertex.z < value:
				value = vertex.z
		return value

	def height(self):
		total_height = 0
		for vertex in self.vertices:
			total_height += vertex.y
		return total_height / len(self.vertices)

# Dimension object.
class Dimension:
	def __init__(self, label):
		if not isinstance(label, str):
			raise TypeError('label must be a string.')

		self.label = label
		self.unique_values = []
		self.minimum_value = 0
		self.maximum_value = 0

	def __str__(self):
		return 'Dimension [' + self.label + ']\t' + str(len(self.unique_values)) + ' unique values from ' + str(self.minimum_value) + ' - ' + str(self.maximum_value) + ' (Span: ' + str(self.span()) + ')'

	def add_value(self, value):
		if not isinstance(value, float):
			raise TypeError('value must be a float.')

		if not value in self.unique_values:
			self.unique_values.append(value)
			if value < self.minimum_value:
				self.minimum_value = value
			if value > self.maximum_value:
				self.maximum_value = value

	def span(self):
		return self.maximum_value - self.minimum_value

# Progress bar object.
# Much credit to Benjamin Cordier.
class ProgressBar:
	fill = '█'
	unfill = '-'

	def __init__(self, total_size, description = '', precision = 1, length = 50):
		if not isinstance(total_size, int):
			raise TypeError('total_size must be an integer.')
		description = str(description)
		if not isinstance(precision, int):
			raise TypeError('precision must be an integer.')
		if not isinstance(length, int):
			raise TypeError('length must be an integer.')

		self.i = 0
		self.total_size = total_size
		self.description = description # Displayed before progress bar.
		self.start_time = time.time() # Time elapsed displays after progress bar.
		self.precision = precision # Number of decimals to display.
		self.length = length # Length of full progress bar.
		self.ended = False # Make sure the bar doesn't spam the console if it goes too long.

	def step(self, amount = 1):
		if not isinstance(amount, int):
			raise TypeError('amount must be an integer.')

		self.i += amount
		self.set_progress(self.i)

	def set_progress(self, progress):
		if not isinstance(progress, int):
			raise TypeError('progress must be an integer.')

		if self.ended:
			return
		self.i = progress
		percent = ("{0:." + str(self.precision) + "f}").format(100 * (self.i / float(self.total_size)))
		time_elapsed = ("{:." + str(self.precision) + "f}s").format(time.time() - self.start_time)
		filledLength = int(self.length * self.i // self.total_size)
		bar = ProgressBar.fill * filledLength + ProgressBar.unfill * (self.length - filledLength)
		print('\r%s |%s| %s%% %s' % (self.description, bar, percent, time_elapsed), end = "\r")
		if self.i >= self.total_size:
			self.end()

	def end(self):
		self.ended = True
		print()

# Log object.
class Log:
	# import time
	# from pathlib import Path
	def __init__(self, path = str(Path(__file__).parent.absolute()), file_name = 'log'):
		path = str(path)
		file_name = str(file_name)

		self.path = path + '\\' + file_name + '.txt'
		self.log = open(self.path, 'w')
		self.start_time = time.time()

	def write(self, text = ''):
		text = str(text)

		if text == '' or text == '\n' or text == '\r':
			self.log.write('\n')
		else:
			self.log.write('[' + ("{:.1f}s").format(time.time() - self.start_time) + ']\t' + text + '\n')

	def close(self):
		self.log.close()

# Make log file.
log = Log()
log.write()
log.write()

# Get model file.
file_path = ""
while True:
	query = input('Map file path: ')
	if not query.endswith('.obj'):
		print('Please specify a .obj file.')
		continue
	if not os.path.isfile(query):
		print('That file does not exist.')
		continue

	file_path = query
	break
log.write("OBJ file path: " + file_path)

# Get image scale information from the user.
hmap_width = 0
while True:
	query = input('Heightmap width: ')
	try:
		hmap_width = int(query)
		break
	except:
		print('Input must represent an integer.')
hmap_height = 0
while True:
	query = input('Heightmap height: ')
	try:
		hmap_height = int(query)
		break
	except:
		print('Input must represent an integer.')
log.write("Heightmap dimensions: " + str(hmap_width) + "x" + str(hmap_height))

# Get mirror type from user.
mirror_type = 0
while True:
	query = input('Mirror types:\n\t0: None\t\t\t1: Across X\t2: Across Y\n\t3:Across X and Y\t4: Across XY\nMirror type: ')
	try:
		mirror_type = int(query)
		break
	except:
		print('Input must represent an integer.')
log.write('Mirror type: ' + str(mirror_type))

# Get total vertices and faces.
total_vertices = 0
total_faces = 0
try:
	with open(file_path, 'r') as file:
		for line in file:
			if line.startswith('v '):
				total_vertices += 1
			elif line.startswith('f '):
				total_faces += 1
except Exception as error:
	print('Error counting vertices and faces [' + str(error) + '].')
log.write('Total vertices: ' + str(total_vertices))
log.write('Total faces: ' + str(total_faces))

# Get vertices.
vertices = {}
try:
	with open(file_path, 'r') as file:
		i = 0
		for line in file:
			line_parts = line.split()
			
			if line_parts[0] == 'v':
				i += 1
				line_parts.pop(0)
				vertex = Vertex(float(line_parts[0]), float(line_parts[1]), float(line_parts[2]), i)
				vertices[i] = vertex
except Exception as error:
	print('Error getting map file [' + str(error) + '].')

# Get faces.
faces = []
try:
	with open(file_path, 'r') as file:
		for line in file:
			line_parts = line.split()

			if line_parts[0] == 'f':
				line_parts.pop(0)
				face_vertices = []
				for part in line_parts:
					face_vertex = vertices[int(part.split('/')[0])]
					face_vertices.append(face_vertex)
					if face_vertex == None:
						raise Exception("Vertex not found.")
				face = Face(face_vertices)
				faces.append(face)
except Exception as error:
	print('Error getting map file [' + str(error) + '].')

# Create dimensions.
x_dim = Dimension('X')
y_dim = Dimension('Y')
z_dim = Dimension('Z')
for vertex in vertices.values():
	i += 1
	x_dim.add_value(float(vertex.x))
	y_dim.add_value(float(vertex.y))
	z_dim.add_value(float(vertex.z))
for dim in (x_dim, y_dim, z_dim):
	dim.unique_values.sort()
	log.write(dim)

# GC
del vertices

# Find coordinates to generate pixels from.
x_step = x_dim.span() / hmap_width
z_step = z_dim.span() / hmap_height
x_steps = []
for x in range(hmap_width):
	value = x_dim.minimum_value + (x * x_step)
	x_steps.append(value)
if mirror_type == 2 or mirror_type == 3 or mirror_type == 4:
	del x_steps[int(hmap_width / 2):]
z_steps = []
for z in range(hmap_height):
	value = z_dim.minimum_value + (z * z_step)
	z_steps.append(value)
if mirror_type == 1 or mirror_type == 3:
	del z_steps[int(hmap_height / 2):]

# Cut off excess faces.
if mirror_type == 1 or mirror_type == 3:
	faces = list(filter(lambda face: face.minimum_z() <= z_steps[-1], faces))
elif mirror_type == 2 or mirror_type == 3 or mirror_type == 4:
	faces = list(filter(lambda face: face.minimum_x() <= x_steps[-1], faces))
log.write('Relevant faces: ' + str(len(faces)))

# Get heights for color values.
y_step = y_dim.span() / 255;
height_to_color = {}
for value in range(256):
	height = y_dim.minimum_value + (y_step * value)
	height_to_color[height] = value

# GC
del x_dim
del y_dim
del z_dim

# Create image.
image = Image.new("RGB", (hmap_width, hmap_height), '#FF0000')

# Set pixel colors.
pixels = image.load()
x_pixel = -1
progress_bar = ProgressBar(len(x_steps), description = 'Progress:', precision = 0)
for x in x_steps:
	x_pixel += 1
	if x_pixel > hmap_width:
		print('Program attempted to exceed width boundary.')
		break

	z_pixel = -1
	for z in z_steps:
		z_pixel += 1
		if z_pixel > hmap_height:
			print('Program attempted to exceed height boundary.')
			break

		# Search for face that contains the specified coordinates.
		this_face = None
		for face in faces:
			if face.maximum_x() > x and face.minimum_x() < x and face.maximum_z() > z and face.minimum_z() < z:
				this_face = face
				break
		else:
			# Coordinates aren't covered by a face. Leave default color.
			continue
		this_color = 0
		for height in height_to_color:
			if height >= this_face.height():
				this_color = height_to_color[height]
				break

		# Color correct pixels.
		pixels[x_pixel, z_pixel] = (this_color, this_color, this_color)
		if mirror_type == 0:
			pass
		elif mirror_type == 1:
			pixels[x_pixel, -(z_pixel + 1)] = (this_color, this_color, this_color)
		elif mirror_type == 2:
			pixels[-(x_pixel + 1), z_pixel] = (this_color, this_color, this_color)
		elif mirror_type == 3:
			pixels[x_pixel, -(z_pixel + 1)] = (this_color, this_color, this_color)
			pixels[-(x_pixel + 1), z_pixel] = (this_color, this_color, this_color)
			pixels[-(x_pixel + 1), -(z_pixel + 1)] = (this_color, this_color, this_color)
		elif mirror_type == 4:
			pixels[-(x_pixel + 1), -(z_pixel + 1)] = (this_color, this_color, this_color)

	# Advance progress bar after each column.
	progress_bar.step()

# Save image.
output_path = str(Path(__file__).parent.absolute()) + '\\output.png'
image.save(output_path)
log.write('Heightmap saved to ' + output_path)

# Close log file.
log.close()
