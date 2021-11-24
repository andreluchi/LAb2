import random
import numpy
import struct
from obj import Obj
from collections import namedtuple
from math import sqrt

V2 = namedtuple("Point2", ["x", "y"])
V3 = namedtuple("Point3", ["x", "y", "z"])
jup = "jupiter"


def sum(v0, v1):
    """
    Input: 2 size 3 vectors
    Output: Size 3 vector with the per element sum
    """
    return V3(v0.x + v1.x, v0.y + v1.y, v0.z + v1.z)

def sub(v0, v1):
    return V3(v0.x - v1.x, v0.y - v1.y, v0.z - v1.z)
    """
    Input: 2 size 3 vectors
    Output: Size 3 vector with the per element substraction
    """
    
def mul(v0, k):
    """
    Input: 2 size 3 vectors
    Output: Size 3 vector with the per element multiplication
    """
    return V3(v0.x * k, v0.y * k, v0.z * k)

def dot(v0, v1):
    """
    Input: 2 size 3 vectors
    Output: Scalar with the dot product
    """
    return v0.x * v1.x + v0.y * v1.y + v0.z * v1.z

def cross(v1, v2):
    """
    Input: 2 size 3 vectors
    Output: Size 3 vector with the cross product
    """
    return V3(
        v1.y * v2.z - v1.z * v2.y,
        v1.z * v2.x - v1.x * v2.z,
        v1.x * v2.y - v1.y * v2.x,
    )

def length(v0):
    """
    Input: 1 size 3 vector
    Output: Scalar with the length of the vector
    """
    return (v0.x ** 2 + v0.y ** 2 + v0.z ** 2) ** 0.5

def norm(v0):
    """
    Input: 1 size 3 vector
    Output: Size 3 vector with the normal of the vector
    """
    v0length = length(v0)
    
    if not v0length:
        return V3(0, 0, 0)
    
    return V3(v0.x/v0length, v0.y/v0length, v0.z/v0length)
    
def bbox(*vertexes):
    """
    Input: n size 2 vectors
    Output: 2 size 2 vectors defining the smallest bounding rectangle possible
    """
    x0 = [vertex.x for vertex in vertexes]
    y0 = [vertex.y for vertex in vertexes]
    x0.sort()
    y0.sort()
    xmin = x0[0]
    xmax = x0[-1]
    ymin = y0[0]
    ymax = y0[-1]
    
    return xmin, xmax, ymin, ymax

def normalizeArray(c_arr):
    return [round(i * 255) for i in c_arr]

def barycentric(A, B, C, P):
    """
    Input: 3 size 2 vectors and a point
    Output: 3 barycentric coordinates of the point in relation to the triangle formed
            * returns -1, -1, -1 for degenerate triangles
    """
    bary = cross(
        V3(C.x - A.x, B.x - A.x, A.x - P.x),
        V3(C.y - A.y, B.y - A.y, A.y - P.y)
    )

    if abs(bary.z) < 1:
      
      return -1, -1, -1   # this triangle is degenerate, return anything outside

    return (
        1 - (bary.x + bary.y) / bary.z,
        bary.y / bary.z,
        bary.x / bary.z
  )

def char(c):
  """
  Input: requires a size 1 string
  Output: 1 byte of the ascii encoded char
  """
  return struct.pack('=c', c.encode('ascii'))

def word(w):
  """
  Input: requires a number such that (-0x7fff - 1) <= number <= 0x7fff
         ie. (-32768, 32767)
  Output: 2 bytes
  Example:
  >>> struct.pack('=h', 1)
  b'\x01\x00'
  """
  return struct.pack('=h', w)

def dword(d):
  """
  Input: requires a number such that -2147483648 <= number <= 2147483647
  Output: 4 bytes
  Example:
  >>> struct.pack('=l', 1)
  b'\x01\x00\x00\x00'
  """
  return struct.pack('=l', d)

def color(r, g, b):
  """
  Input: each parameter must be a number such that 0 <= number <= 255
         each number represents a color in rgb
  Output: 3 bytes
  Example:
  >>> bytes([0, 0, 255])
  b'\x00\x00\xff'
  """
  return bytes([int(b * 255), int(g * 255), int(r * 255)])

class Render(object):
    def __init__(self,width,height):
        self.framebuffer = []
        self.width = width
        self.height = height
        self.clear()
        self.viewport_x = 0
        self.viewport_y = 0
        self.viewport_width = 1000
        self.viewport_height = 1000
        
        self.zbuffer = [
            [-float('inf') for x in range(self.width)]
            for y in range(self.height)
        ]
        self.shape = None

    

    def clear(self):
        r, g, b = 0, 0, 0
        self.pixels = color(r, g, b)
        self.framebuffer = [
            [self.pixels for x in range(self.width)] for y in range(self.height)
        ]

    def glCreateWindow(self, width, height):
        self.height = height
        self.width = width
        self.framebuffer = []
        self.clear()
    
    def write(self, filename):
        writebmp(filename, self.width, self.height, self.pixels)
    
    def display(self, filename='out.bmp'):
        """
        Displays the image, a external library (wand) is used, but only for convenience during development
        """
        self.write(filename)

        try:
          from wand.image import Image
          from wand.display import display

          with Image(filename=filename) as image:
            display(image)
        except ImportError:
          pass
    
    def clear2(self, r=1, g=1, b=1):
        ncolor = normalizeArray([r, g, b])
        clearc = color(ncolor[0], ncolor[1], ncolor[2])

        self.framebuffer = [
            [clearc for x in range(self.width)] for y in range(self.height)
        ]

    def glViewport(self, x, y, width, height):
        self.viewport_x = x
        self.viewport_y = y
        self.viewport_height = height
        self.viewport_width = width

    def point(self, x, y, color):
        self.framebuffer[y][x] = color or self.draw_color

    def triangle(self, A, B, C):
        xmin, xmax, ymin, ymax = bbox(A, B, C)

        for x in range(xmin, xmax + 1):
            for y in range(ymin, ymax + 1):
                P = V2(x, y)
                w, v, u = barycentric(A, B, C, P)
                if w < 0 or v < 0 or u < 0:# 0 is actually a valid value! (it is on the edge)
                    continue

                z = A.z * u + B.z * v + C.z * w

                r, g, b = self.shader(
                    x, y
                )
                color_usado = color(r, g, b)
                if z > self.zbuffer[y][x]:
                    self.point(x, y, color_usado)
                    self.zbuffer[y][x] = z

    def radius(self,x,y):
        return int(sqrt(x*x + y*y))

    def shader(self, x=0, y=0):
        color_usado = 0, 0, 0
        shape_usado = self.shape

        r1, g1, b1 = 0, 0, 0
        r2, g2, b2 = 0, 0, 0
        percentage = 1

        if shape_usado == jup:
            if y >= 385 and y <= 435:
                r1, g1, b1 = (120, 150, 180)
                r2, g2, b2 = 146, 205, 232
                percentage = abs(y - 410)

            if (y > 335 and y < 385) or (y > 435 and y < 485):
                if y < 460 or y > 360:
                    r1, g1, b1 = 146, 205, 232
                    r2, g2, b2 = 166, 162, 174
                    percentage = abs(y - 410)

                    if y >= 460 or y <= 360:
                        r1, g1, b1 = 125, 155, 180
                        r2, g2, b2 = 166, 162, 174
                        if y < 460 or y > 360:
                            r1, g1, b1 = 166, 162, 174
                            r2, g2, b2 = 166, 162, 174
                            percentage = abs(y - 410)

                            if y >= 460 or y <= 360:
                                r1, g1, b1 = 166, 162, 174
                                r2, g2, b2 = 166, 162, 174

                if y >= 460 or y <= 360:
                    r1, g1, b1 = 125, 155, 180
                    r2, g2, b2 = 166, 162, 174
                    if y >= 460:
                        percentage = abs(y - 460)
                    else:
                        percentage = abs(y - 360)

            if (y <= 335 and y >= 270) or (y <= 550 and y >= 485):
                if y < 510 or y > 310:
                    r1, g1, b1 = 166, 162, 174
                    r2, g2, b2 = 146, 205, 232                    
                    if y <= 335:
                        percentage = abs(y - 360)
                    else:
                        percentage = abs(y - 460)

                if y >= 510 or y <= 310:
                    r1, g1, b1 = 146, 205, 232
                    r2, g2, b2 = 125, 155, 180
                    if y <= 310:
                        percentage = abs(y - 310)
                    else:
                        percentage = abs(y - 520)

            percentage = (percentage / 60)
            r = r1 + percentage * (r2 - r1)
            g = g1 + percentage * (g2 - g1)
            b = b1 + percentage * (b2 - b1)
            color_usado = r, g, b

            if (y % 40) in range(0, 14):
                r, g, b = color_usado
                r *= 0.98
                g *= 0.98
                b *= 0.98
                color_usado = r, g, b

        b, g, r = color_usado
        b /= 255
        g /= 255
        r /= 255

        intensity = 2

        if shape_usado == jup:
            intensity = ((self.radius(x - 120, y - 390) + 50) / 400)
            intensity = (1 - (intensity * 0.95) ** 4)

        b = b*intensity
        g = g * intensity
        r = r * intensity

        if intensity > 0:
            return r, g, b
        else:
            return 0, 0, 0

    def glLoad(self, filename, translate=[0, 0], scale=[1, 1], shape=None):
        model = Obj(filename)
        self.shape = shape

        for f in model.faces:
            vcount = len(f)

            if vcount == 3:
                f1 = f[0][0] - 1
                f2 = f[1][0] - 1
                f3 = f[2][0] - 1

                v1 = model.vertexes[f1]
                v2 = model.vertexes[f2]
                v3 = model.vertexes[f3]

                x1 = round((v1[0] * scale[0]) + translate[0])
                y1 = round((v1[1] * scale[1]) + translate[1])
                z1 = round((v1[2] * scale[2]) + translate[2])

                x2 = round((v2[0] * scale[0]) + translate[0])
                y2 = round((v2[1] * scale[1]) + translate[1])
                z2 = round((v2[2] * scale[2]) + translate[2])

                x3 = round((v3[0] * scale[0]) + translate[0])
                y3 = round((v3[1] * scale[1]) + translate[1])
                z3 = round((v3[2] * scale[2]) + translate[2])

                a = V3(x1, y1, z1)
                b = V3(x2, y2, z2)
                c = V3(x3, y3, z3)

                vn0 = model.normals[f[0][2] - 1]
                vn1 = model.normals[f[1][2] - 1]
                vn2 = model.normals[f[2][2] - 1]

                self.triangle(a, b, c)

            else:
                f1 = f[0][0] - 1
                f2 = f[1][0] - 1
                f3 = f[2][0] - 1
                f4 = f[3][0] - 1

                v1 = model.vertexes[f1]
                v2 = model.vertexes[f2]
                v3 = model.vertexes[f3]
                v4 = model.vertexes[f4]

                x1 = round((v1[0] * scale[0]) + translate[0])
                y1 = round((v1[1] * scale[1]) + translate[1])
                z1 = round((v1[2] * scale[2]) + translate[2])

                x2 = round((v2[0] * scale[0]) + translate[0])
                y2 = round((v2[1] * scale[1]) + translate[1])
                z2 = round((v2[2] * scale[2]) + translate[2])

                x3 = round((v3[0] * scale[0]) + translate[0])
                y3 = round((v3[1] * scale[1]) + translate[1])
                z3 = round((v3[2] * scale[2]) + translate[2])

                x4 = round((v4[0] * scale[0]) + translate[0])
                y4 = round((v4[1] * scale[1]) + translate[1])
                z4 = round((v4[2] * scale[2]) + translate[2])

                a = V3(x1, y1, z1)
                b = V3(x2, y2, z2)
                c = V3(x3, y3, z3)
                d = V3(x4, y4, z4)

                self.triangle(a, b, c)
                self.triangle(a, c, d)

    def glfinish(self, filename="out.bmp"):
        f = open(filename, "bw")
        
        # File header (14 bytes)
        f.write(char("B"))
        f.write(char("M"))
        f.write(dword(14 + 40 + self.width * self.height * 3))
        f.write(dword(0))
        f.write(dword(14 + 40))

        # Image header (40 bytes)
        f.write(dword(40))
        f.write(dword(self.width))
        f.write(dword(self.height))
        f.write(word(1))
        f.write(word(24))
        f.write(dword(0))
        f.write(dword(self.width * self.height * 3))
        f.write(dword(0))
        f.write(dword(0))
        f.write(dword(0))
        f.write(dword(0))

        # Pixel data (width x height x 3 pixels)
        for x in range(self.height):
            for y in range(self.width):
                f.write(self.framebuffer[x][y])
                
        f.close()


r = Render(700,700)
r.glCreateWindow(700,700)
r.glLoad("./sphere.obj", translate=(300, 395, 0), scale=(280, 280, 280), shape=jup)
r.glfinish(filename="Jupiter.bmp")