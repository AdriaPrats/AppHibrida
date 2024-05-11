from flask import Flask, render_template, request, session, redirect, url_for
import numpy as np
import datetime
import urllib.request, json
from CDatabase import carros

app = Flask(__name__)
app.config['SECRET_KEY'] = 'mysecretkey'



def DisplayAvancat(LlistaReserves,LlistaCarros,dataIni,dataFin):
	#Generam una estructura de dades tipus diccionari de matrius, per poderla mostrar
	#adequadament al template
	#{'carro':[reservadia1,reservadia2,reservadia3...],'carro2':...}
	DiccionariFinal={}
	#primer generam una llista de dies, per poder ordenar les reserves
	llistaDies=[dataIni]
	arrayBuit=['']
	while llistaDies[-1]<dataFin:
		llistaDies.append(llistaDies[-1]+datetime.timedelta(days=1))
		arrayBuit.append('')
	#Generam el diccionari "buit"
	for carro in LlistaCarros:
		DiccionariFinal[carro['nom']]=arrayBuit.copy()
	print(DiccionariFinal)
	#modificam els valors mirant la llista de reserves
	for r in LlistaReserves:
		print(r)
		for i,d in enumerate(llistaDies):
			if r['iniciReserva']<=d.replace(tzinfo=None) and r['finalReserva']>=d.replace(tzinfo=None):
				DiccionariFinal[r['nom']][i]=r['usuario']
	print(DiccionariFinal)
	return DiccionariFinal

def ComprovaReserva(NovaReserva):

	missatgeRetorn=0
	#data inicial antiga
	if NovaReserva['iniciReserva']<datetime.datetime.now():
		missatgeRetorn="No pots reservar per un dia anterior al d'avui"
	#data final menor que la inicial
	if NovaReserva['iniciReserva']>NovaReserva['finalReserva']:
		missatgeRetorn="Has indicat una data de retorn inferior a la data d'inici"
	#carro ja reservat		
	if missatgeRetorn==0:
		if carros().comprovaReserva(NovaReserva)==False:
			missatgeRetorn="No pots reservar el carro pel dia selecionat, ja es troba reservat"
	return missatgeRetorn

def defineDias():
	dias=[]
	for i in range(0,7):
		dias.append((session['primerDia']+datetime.timedelta(days=i)).strftime("%d-%m-%Y"))
	print(dias)
	return dias

@app.route('/')
@app.route('/llista')
def llista():
	carrosList=carros().cargaCarros()
	for c in carrosList:
		c['img']="../static/"+c['img']
	if not session.get("primerDia"):
		session['primerDia']=datetime.datetime.today()
		defineDias()
	#carregam els carros del fitxer json
	return render_template('carros.html',carros=carrosList)

@app.route('/reservar')
def reservar():
	carrosList=carros().cargaCarros()
	for c in carrosList:
		c['img']="../static/"+c['img']
	return render_template('carros2.html',carros=carrosList)

@app.route('/novareserva')
def novareserva():
	carrosList=carros().cargaCarros()
	for c in carrosList:
		c['img']="../static/"+c['img']
	nomCompost=request.args.get('nom')+" "+request.args.get('llinatges')
	iniciReserva=datetime.datetime.strptime(request.args.get("diareserva"),"%d-%m-%Y")
	iniciReserva+=datetime.timedelta(hours=int(request.args.get("horareserva")))
	finalReserva=datetime.datetime.strptime(request.args.get("diaretorno"),"%d-%m-%Y")
	finalReserva+=datetime.timedelta(hours=int(request.args.get("horaretorno")))
	ReservaActual={'nom':nomCompost,'iniciReserva':iniciReserva,'finalReserva':finalReserva,'carro':request.args.get('carroreserva')}
	alertaComprova=ComprovaReserva(ReservaActual)
	if alertaComprova==0:
		carros().novaReserva(ReservaActual)
		cost=carros().costReserva(ReservaActual)
		return render_template('carros2.html',carros=carrosList,success=cost)
	else:
		return render_template('carros2.html',carros=carrosList,alerta=alertaComprova)


# This page will have the sign up form
@app.route('/reserves')
def reserves():
	carrosList=carros().cargaCarros()
	for c in carrosList:
		c['img']="../static/"+c['img']
	avancat=DisplayAvancat(carros().cargaReserves(),carrosList,session['primerDia'],session['primerDia']+datetime.timedelta(days=6))
	return render_template('carros3.html',avancat=avancat,carros=carrosList,dias=defineDias())

@app.route('/augmentasetmana')
def augmentasetmana():
	session['primerDia']=session['primerDia']+datetime.timedelta(days=7)
	return redirect(url_for('reserves'))

@app.route('/restasetmana')
def restasetmana():
	session['primerDia']=session['primerDia']-datetime.timedelta(days=7)
	return redirect(url_for('reserves'))

# This page will have the sign up form
@app.route('/intranet')
def intranet():
	carrosList=carros().cargaCarros()
	for c in carrosList:
		c['img']="../static/"+c['img']
		c['actualiza']=0
	return render_template('carros4.html',carros=carrosList)

#PENDENT
@app.route('/borracarro')
def borracarro():
	id= request.args.get('id')
	carros().eliminaCarro(id)
	return redirect(url_for('intranet'))

@app.route('/editacarro')
def editacarro():
	id=request.args.get('id')
	print(id)
	carrosList=carros().cargaCarros()
	clasesCarro=['basic','1cavall','2cavalls']
	for c in carrosList:
		c['img']="../static/"+c['img']
		if int(c['id'])==int(id):
			c['actualiza']=1
		else:
			c['actualiza']=0
	print(carrosList)
	return render_template('carros4.html',carros=carrosList,clases=clasesCarro)

@app.route('/afegeixcarro')
def afegeixcarro():
	id=0
	carrosList=carros().cargaCarros()
	clasesCarro=['basic','1cavall','2cavalls']
	for c in carrosList:
		c['img']="../static/"+c['img']
		c['actualiza']=0
		if c['id']>id:
			id=c['id']
	id+=1
	carrosList.append({'id':id,'actualiza':1})
	return render_template('carros4.html',carros=carrosList,clases=clasesCarro)

@app.route('/guardacarro')
def guardacarro():
	nouCarro={'id':request.args.get('id'),'nom':request.args.get('nom'),'descripcio':request.args.get('descripcio'),
	   'clase':request.args.get('clase'),'preu':request.args.get('preu')}
	carros().nouCarro(nouCarro)
	return redirect(url_for('intranet'))

if __name__ == '__main__':
	app.run(debug=True)
