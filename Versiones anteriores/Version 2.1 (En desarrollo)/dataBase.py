import sqlite3

base = sqlite3.connect('/database')

cursor = base.cursor()

print 'La base de datos se abrio correctamente'

cursor.execute('''DROP TABLE EMPRESA''')

print 'la tabla de datos se elimino correctamente'

cursor.execute(''' CREATE TABLE EMPRESA (
        ID INT PRIMARY KEY NOT NULL,
        NOMBRE TEXT NOT NULL,
        EDAD INT NOT NULL,
        DIRECCION CHAR(50),
        SALARIO REAL
        )
''')

print u'tabla creada con exito'

cursor.execute('''
    INSERT INTO EMPRESA(ID,NOMBRE,EDAD,DIRECCION,SALARIO)
    VALUES(1,'Pablo',32,'Montevideo',20000.00)
''')


cursor.execute('''
    INSERT INTO EMPRESA(ID,NOMBRE,EDAD,DIRECCION,SALARIO)
    VALUES(2,'Raul',23,'Buenos Aires',30000.00)
''')


cursor.execute('''
    INSERT INTO EMPRESA(ID,NOMBRE,EDAD,DIRECCION,SALARIO)
    VALUES(3,'Carlos',12,'Cordona',50000.00)
''')
base.commit()

print 'se guardo la base de datos'

base.close()

base = sqlite3.connect('/database')
cursor = base.cursor()

print 'la base de datos se abrio correctamente'

cursor.execute("SELECT id, nombre, direccion, salario from EMPRESA")

for i in cursor:
    print 'id = ', i[0]
    print 'nombre = ', i[1]
    print 'direccion = ', i[2]
    print 'salario = ', i[3]
    print '\n'

print 'operacion satisfactoria'

base.close()
