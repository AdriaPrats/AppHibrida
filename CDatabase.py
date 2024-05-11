import pymysql.cursors
import datetime

class carros(object):
    def __init__(self):
        self.host = "localhost"

    def conectaDB(self):
        #Conexion a la BBDD del servidor mySQL
        self.db = pymysql.connect(host=self.host,
                                     user='root',
                                     db='rentacarro',
                                     charset='utf8mb4',
                                     autocommit=True,
                                     cursorclass=pymysql.cursors.DictCursor)
        self.cursor=self.db.cursor()

    def desconectaDB(self):
        self.db.close()

    def cargaCarros(self):
        self.conectaDB()
        sql="SELECT * from carros"
        self.cursor.execute(sql)
        ResQuery=self.cursor.fetchall()
        self.desconectaDB()
        return ResQuery

    def cargaReserves(self):
        self.conectaDB()
        sql="select r.idcarro,c.nom,r.iniciReserva,r.finalReserva,r.usuario from reservas r,carros c WHERE c.id=r.idcarro;"
        self.cursor.execute(sql)
        ResQuery=self.cursor.fetchall()
        self.desconectaDB()
        return ResQuery

    def novaReserva(self,reserva):
        self.conectaDB()
        sql="INSERT INTO reservas VALUES ("+reserva['carro']+",'"+reserva['iniciReserva'].strftime("%Y-%m-%d %H:00:00")
        sql+="','"+reserva['finalReserva'].strftime("%Y-%m-%d %H:00:00")+"','"+reserva['nom']+"');"
        self.cursor.execute(sql)
        ResQuery=self.cursor.fetchall()
        self.desconectaDB()
        return ResQuery
    
    def comprovaReserva(self,reserva):
        self.conectaDB()
        sql="SELECT iniciReserva,finalReserva from reservas WHERE idcarro="+reserva['carro']
        self.cursor.execute(sql)
        ResQuery=self.cursor.fetchall()
        flagCorrecto=True
        for r in ResQuery:
            if reserva['iniciReserva']>r['finalReserva'] or reserva['finalReserva']<r['iniciReserva']:
                pass
            else:
                flagCorrecto=False
        self.desconectaDB()
        return flagCorrecto

    def costReserva(self,reserva):
        self.conectaDB()
        sql="SELECT preu from carros WHERE id="+reserva['carro']
        self.cursor.execute(sql)
        ResQuery=self.cursor.fetchone()
        print(ResQuery['preu'])
        difDies=(reserva['finalReserva']-reserva['iniciReserva']).days
        if reserva['finalReserva'].hour>reserva['iniciReserva'].hour:
            difDies+=1
        print(difDies)
        retornar=ResQuery['preu']*difDies
        self.desconectaDB()
        return retornar

    def nouCarro(self,carro):
        #primer hem de comprovar si es una modificacio o un carro nou, miram si id existeix
        self.conectaDB()
        sql="SELECT count(*) from carros WHERE id="+str(carro['id'])
        self.cursor.execute(sql)
        ResQuery=self.cursor.fetchone()
        print(ResQuery['count(*)'])
        if ResQuery['count(*)']==0:
            #es un insert
            sql="INSERT INTO carros values("+str(carro['id'])+",'"+carro['nom']+"','"+carro['clase']+"',"
            sql=sql+str(carro['preu'])+",'"+carro['descripcio']+"','carro1.png');"
        else:
            sql="UPDATE carros SET nom='"+carro['nom']+"', clase='"+carro['clase']+"', preu="
            sql+=str(carro['preu'])+" , descripcio='"+carro['descripcio']+"' WHERE id="+carro['id']+";"
        self.cursor.execute(sql)
        self.desconectaDB()        

    def eliminaCarro(self,id):
        self.conectaDB()
        sql="DELETE from carros WHERE id="+str(id)
        self.cursor.execute(sql)
        self.desconectaDB()        
