import struct
from collections import namedtuple

V2 = namedtuple('Point2', ['x','y'])

def char(c):
    # 1 byte
    return struct.pack('=c', c.encode('ascii'))

def word(w):
    # 2 bytes
    return struct.pack('=h', w)

def dword(d):
    # 4 bytes
    return struct.pack('=l', d)

def color(r,g,b):
    return bytes([int(b * 255),
                  int(g * 255),
                  int(r * 255)])


class Renderer(object):
    def __init__(self, width, height):
        self.width = width
        self.height = height

        self.glClearColor(0,0,0)
        self.glClear()

        self.glColor(1,1,1)

    def glClearColor(self, r,g,b):
        self.clearColor = color(r,g,b)


    def glColor(self, r,g,b):
        self.currColor = color(r,g,b)


    def glClear(self):
        self.pixels = [[self.clearColor for y in range(self.height)]
                       for x in range(self.width)] 

    def glPoint(self, x, y, clr = None):
        if(0 <= x < self.width) and (0 <= y < self.height):
            self.pixels[x][y] = clr or self.currColor


    def glLine(self, v0, v1, clr = None):

         x0 = int(v0[0])
         x1 = int(v1[0])
         y0 = int(v0[1])
         y1 = int(v1[1])

         # Si el punto 0 es igual al punto 1, solo dibujar un punto
         if x0 == x1 and y0 == y1:
             self.glPoint(x0,y0)
             return

         dy = abs(y1 - y0)
         dx = abs(x1 - x0)

         steep = dy > dx

         # Si la linea tiene pendiente mayor a 1 o menor a -1
         # intercambiamos las x por las y, y se dibuja la linea
         # de manera vertical en vez de horizontal
         if steep:
             x0, y0 = y0, x0
             x1, y1 = y1, x1

         # Si el punto inicial en x es mayor que el punto final en x
         # intercambiamos los puntos para siempre dibujar de
         # izquierda a derecha
         if x0 > x1:
             x0, x1 = x1, x0
             y0, y1 = y1, y0

         dy = abs(y1 - y0)
         dx = abs(x1 - x0)

         offset = 0
         limit = 0.5
         m = dy/dx
         y = y0

         for x in range (x0, x1 + 1):
             if steep:
                 # Dibujar de manera vertical
                 self.glPoint(y, x, clr or self.currColor)
             else:
                 # Dibujar de manera horizontal
                 self.glPoint(x, y, clr or self.currColor)
             
             offset += m

             if offset >= limit:
                 if y0 < y1:
                     y += 1
                 else:
                     y -= 1

                 limit += 1

    def glPolygon(self, vertices):
        for i in range(len(vertices)):
            # Dibuja una línea desde el punto actual al siguiente
            self.glLine(vertices[i], vertices[(i + 1) % len(vertices)])

    # Referencia de https://alienryderflex.com/polygon_fill/ metodo point in polygon 
    def glFillPolygon(self,vertices,color):
        top = 0
        bottom = self.height
        right = self.width
        left = 0
        pointX = []

        #  Cicla por cada linea de pixeles en la imagen
        for pixelY in range(top, bottom):
            # Construye la lista de puntos
            points = 0
            j = len(vertices) - 1
            for i in range(len(vertices)):
                if ((vertices[i].y < pixelY and vertices[j].y >= pixelY)
                or (vertices[j].y < pixelY and vertices[i].y >= pixelY)):
                    points += 1
                    pointX.append(int(vertices[i].x+(pixelY-vertices[i].y)/(vertices[j].y-vertices[i].y)*(vertices[j].x-vertices[i].x)))
                j = i

            #  Ordena los puntos con un Bubble sort
            i = 0
            while i < points-1:
                if pointX[i] > pointX[i+1]:
                    pointX[i], pointX[i+1] = pointX[i+1], pointX[i] # swap
                    if i: 
                        i -= 1
                else:
                    i += 1

            #  Rellena los pixeles que estan entre el par de puntos
            for i in range(0, points, 2):
                if pointX[i] >= right:
                    break
                if pointX[i+1] > left:
                    if pointX[i] < left:
                        pointX[i] = left
                    if pointX[i+1] > right:
                        pointX[i+1] = right
                    for pixelX in range(pointX[i], pointX[i+1]):
                        self.glColor(*color)
                        self.glPoint(pixelX, pixelY)


    def glFinish(self, filename):
        with open(filename, "wb") as file:
            # Header
            file.write(char("B"))
            file.write(char("M"))
            file.write(dword(14 + 40 + (self.width * self.height * 3)))
            file.write(dword(0))
            file.write(dword(14+40))

            # InfoHeader
            file.write(dword(40)) 
            file.write(dword(self.width))
            file.write(dword(self.height))
            file.write(word(1))
            file.write(word(24))
            file.write(dword(0)) 
            file.write(dword(self.width * self.height * 3))
            file.write(dword(0))
            file.write(dword(0))
            file.write(dword(0))
            file.write(dword(0))

            # Color table
            for y in range(self.height):
                for x in range(self.width):        
                    file.write(self.pixels[x][y])
