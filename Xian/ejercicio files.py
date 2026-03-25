#El ejercicio de files
#Abrimos el fichero en formato lectura (r)
F = open('airports.txt','r')
#Generamos el segundo fichero en formato escritura (w)
G = open('result.txt','w')
#Creamos la variable que contará las líneas erróneas
linea_ignorada = 0
#leemos la primera línea antes de empezar el bucle
Datos = F.readline()
while Datos != "":#Esto genera el bucle para cuando la variable datos no esté vacía
    # Creamos la matriz info que va a separar por los espacios
    info = Datos.split(" ")
    # separamos aeropuerto, latitud y longitud, para ello primero comprobamos si hay 3 elementos
    if len(info) == 3:
        aeropuerto = str(info[0])
        latitude = eval(info[1])
        longitude = eval(info[2])
        if longitude < 0:
            G.write(aeropuerto + "\n") #el \n sirve para saltar de fila cuando escribes en un fichero
    else:#si el formato no es correcto añade una al contador
        linea_ignorada += 1
    Datos = F.readline() #Esto es muy importante para saltar a la siguiente fila
F.close()
G.close()
print(linea_ignorada)