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

    """
    Dibuja y rellena un polígono en la imagen.
    Argumentos:
        vertices: Una lista de objetos V2 que representan los vértices del polígono.
        color: Un color opcional para el polígono. Si no se proporciona, se usa el color actual.
    Referencia de: https://hackernoon.com/computer-graphics-scan-line-polygon-fill-algorithm-3cb47283df6 SCAN LINE
    """
    
    def glPolygonFill(self, vertices, color=None):
        #Verifica si no se proporciono un color, se usa el color actual
        if color == None:
            color = self.currColor

        # Se encuentra el punto Y mas minimo y maximo
        minY = min(vertices, key=lambda x: x.y).y
        maxY = max(vertices, key=lambda x: x.y).y
    
        # Recorre de forma vertical cada linea del poligono
        for y in range(minY, maxY + 1):
        
            intersections = [] #almacena las intersecciones de esa linea horizontal con el poligono

            # Recorre cada tupla de vertices en el listado de vertices 
            for point in range(len(vertices)):
                v0 = vertices[point] #vertice actual
                v1 = vertices[(point + 1) % len(vertices)]#el siguiente vertice
                
                #Aseguramos que el vertice actual este sobre el siguiente vertice
                if v0.y < v1.y:
                    low = v0
                    high = v1
                else:
                    low = v1
                    high = v0
                
                # Si la linea se cruza con un segmento de linea
                if y >= low.y and y < high.y:
                    
                    #punto de interseccion en x
                    t = (y - low.y) / (high.y - low.y) # la proporcion del camino a seguir
                    x = low.x + t * (high.x - low.x) # Calcula la coordenada en x
                    intersections.append(x)

            # Ordena las intersecciones
            intersections.sort()
            
            # Dibuja los puntos entre la tupla de puntos de cada interseccion 
            for point in range(0, len(intersections) - 1, 2):
                x0 = int(intersections[point])
                x1 = int(intersections[point + 1])

                for x in range(x0, x1 + 1):
                    self.glColor(*color)
                    self.glPoint(x, y)


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
