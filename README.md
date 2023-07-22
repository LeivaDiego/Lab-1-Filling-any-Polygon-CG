# Lab-1-Filling-any-Polygon-CG
Implementacion de un algoritmo que rellena polígonos de más de 4 puntos

Se implemento una versino de scanLine fill

El metodo se llama glPolygonFill, al cual le entran los argumentos vertices y color.
  - vertices almacena el listado de vertices del que se compone el poligono
  - color almacena el color con el que se quiere rellenar el poligono

Ahora el metodo funciona encontrando el punto maximo y minimo de cada poligono en el eje Y
Se itera cada punto desde el minimo hasta el maximo, es decir el escaneo de cada linea horizontal.
Posteriormente por cada par de puntos dentro de este listado, se verifica si la linea horizontal se intersecta con algun segmento de linea del poligono. De ser asi, se realiza el calculo de la coordenada en x del punto a rellenar.
Una vez terminada toda esta iteracion de lineas horizontales, ya se cuenta con el listado de intersecciones, es decir con el listado de puntos dentro del poligono, se proceden a dibujar para rellenar el poligono.
