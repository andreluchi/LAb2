import struct 
import numpy

def color(r, g, b):
  return bytes([b, g, r])


# ===============================================================
# Loads an OBJ file
# ===============================================================


def try_int_minus1(s, base=10, val=None):
  try:
    return int(s, base) - 1
  except ValueError:
    return val


class Obj(object):
    def __init__(self, filename):
        with open(filename) as f:
            self.lines = f.read().splitlines()
        self.vertexes = []
        self.tvertexes = []
        self.normals = []
        self.faces = []
        self.read()

    def read(self):
        for line in self.lines:
            if line:
                try:
                    prefix, value = line.split(' ', 1)
                except:
                    prefix = ''
                if prefix == 'v':
                    self.vertexes.append(list(map(float, value.split(' '))))
                elif prefix == "vn":
                    self.normals.append(list(map(float, value.split(" "))))
                elif prefix == 'vt':
                    self.tvertexes.append(list(map(float, value.split(' '))))
                elif prefix == 'f':
                    self.faces.append([list(map(try_int_minus1, face.split('/'))) for face in value.split(' ')])