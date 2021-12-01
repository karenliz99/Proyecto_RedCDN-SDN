#PROGRAMA PARA SISTEMA DE ENRUTAMIENTO RED SIMULADA

#LIBRERIAS
import requests #importa libreria para HTTP
from requests.auth import HTTPBasicAuth
import json #modulo para formato json
import unicodedata
from subprocess import Popen, PIPE
import time #modulo funciones de tiempo
import networkx as nx #instancia para graficos
from sys import exit

#FUNCIONES

#FUNCION 1: REALIZAR SOLICITUD GET Y LEER DATOS EN FORMATO JSON
def getResponse(url,informacion):

	#Utiliza contrasena y usuario 'admin' para autenticacion
	response = requests.get(url, auth=HTTPBasicAuth('admin', 'admin'))

	#Si el GET fue exitoso:
	if(response.ok):
		#jData almacena el contenido de respuesta del GET
		#json.loads codifica en un objeto de python el contenido
		jData = json.loads(response.content)
		if(informacion=="topology"):
			topologyInformation(jData)
		elif(informacion=="statistics"):
			getStats(jData)
	else:
		#Funcion para verificar mensaje de error en el GET
		response.raise_for_status()

#FUNCION 2: OBTIENE INFORMACIÓN DE TOPOLOGIA DE RED EN FORMATO JSON
def topologyInformation(datos):
	
    global switch
    global deviceMAC
    global deviceIP
    global hostPorts
    global linkPorts
    global G
    global cost
    
    for i in datos["network-topology"]["topology"]:
		
		if "node" in i:
			for j in i["node"]:
				
                #Direcciones MAC e IP de los dispositivos
				if "host-tracker-service:addresses" in j:
					for k in j["host-tracker-service:addresses"]:
						#Codifica las cadenas en ascii e ignora los errores
						ip = k["ip"].encode('ascii','ignore')
						mac = k["mac"].encode('ascii','ignore')

						deviceMAC[ip] = mac #almacena la dir MAC en la dir IP correspondiente
						deviceIP[mac] = ip #almacena la dir IP en la dir MAC correspondiente

				#Enlaces entre Switchs y Hosts
				if "host-tracker-service:attachment-points" in j:
					for k in j["host-tracker-service:attachment-points"]:
						mac = k["corresponding-tp"].encode('ascii','ignore') #Codifica las cadenas en ascii e ignora los errores
						mac = mac.split(":",1)[1] #Separa la cadena en caracteres
						ip = deviceIP[mac]
						temp = k["tp-id"].encode('ascii','ignore')
						switchID = temp.split(":")
						port = switchID[2]
						hostPorts[ip] = port  #almacena puerto del switch al que esta conectado el host.
						switchID = switchID[0] + ":" + switchID[1]  #almacena Dir IP : IDSwitch
						switch[ip] = switchID
    
    #Enlaces entre switchs
    for i in datos["network-topology"]["topology"]:
		if "link" in i:
			for j in i["link"]:
				if "host" not in j['link-id']:
                    #Codifica las cadenas en ascii e ignora los errores
					src = j["link-id"].encode('ascii','ignore').split(":")
					srcPort = src[2]
					dst = j["destination"]["dest-tp"].encode('ascii','ignore').split(":")
					dstPort = dst[2]
					srcToDst = src[1] + "::" + dst[1]
					linkPorts[srcToDst] = srcPort + "::" + dstPort
                    #almacena IDSwitchOrigen::IDSwitchDestino : PuertoSwitchOrigen::PuertoSwitchDestino
					G.add_edge((int)(src[1]),(int)(dst[1]))
                    #utiliza funcion de libreria nx para anadir los enlaces

#FUNCION 3: OBTIENE ESTADISTICAS DE RED EN FORMATO JSON
def getStats(datos):
	print "\nCalculando costo\n"
	global cost
	txRate = 0
	for i in datos["node-connector"]:
        #Tx almacena estadisticas de paquetes transmitidos: bytes transmitidos
		tx = int(i["opendaylight-port-statistics:flow-capable-node-connector-statistics"]["packets"]["transmitted"])
		#Rx almacena estadisticas de paquetes recibidos: bytes recibidos
        rx = int(i["opendaylight-port-statistics:flow-capable-node-connector-statistics"]["packets"]["received"])
        txRate = tx + rx #bytes transmitidos y recibidos
		

	time.sleep(2)

	response = requests.get(stats, auth=HTTPBasicAuth('admin', 'admin')) #Get con url para estadisticas
	tempJSON = ""
	if(response.ok):
		tempJSON = json.loads(response.content) #almacena contenido de respuesta

	for i in tempJSON["node-connector"]:
		tx = int(i["opendaylight-port-statistics:flow-capable-node-connector-statistics"]["packets"]["transmitted"])
		rx = int(i["opendaylight-port-statistics:flow-capable-node-connector-statistics"]["packets"]["received"])
		cost = cost + tx + rx - txRate #diferencia entre bytes recibidos y transmitidos entre solicitudes

#FUNCION 4: PERMITE EJECUTAR COMANDOS EN CMD
def systemCommand(cmd):
	terminalProcess = Popen(cmd, stdout=PIPE, stderr=PIPE, shell=True)
	terminalOutput,stderr = terminalProcess.communicate()

#FUNCION 5: CREA LOS FLUJOS EN EL SWITCH
def crear_flujos(bestPath):

	bestPath = bestPath.split("::")

	for currentNode in range(0, len(bestPath)-1):
		if (currentNode==0):
			inport = hostPorts[h2]
			srcNode = bestPath[currentNode]
			dstNode = bestPath[currentNode+1]
			outport = linkPorts[srcNode + "::" + dstNode]
			outport = outport[0]
		else:
			prevNode = bestPath[currentNode-1]
			#print prevNode
			srcNode = bestPath[currentNode]
			#print srcNode
			dstNode = bestPath[currentNode+1]
			inport = linkPorts[prevNode + "::" + srcNode]
			inport = inport.split("::")[1]
			outport = linkPorts[srcNode + "::" + dstNode]
			outport = outport.split("::")[0]
			
		flujo1='\'<?xml version="1.0" encoding="UTF-8" standalone="no"?><flow xmlns="urn:opendaylight:flow:inventory"><priority>32767</priority><flow-name>Flujo 1</flow-name><match><in-port>' + str(inport) +'</in-port><ipv4-destination>'+ h1 +'/32</ipv4-destination><ipv4-source>'+ h2 +'/32</ipv4-source><ethernet-match><ethernet-type><type>2048</type></ethernet-type></ethernet-match></match><id>1</id><table_id>0</table_id><instructions><instruction><order>0</order><apply-actions><action><order>0</order><output-action><output-node-connector>' + str(outport) +'</output-node-connector></output-action></action> </apply-actions></instruction></instructions></flow>\''
		flujo2='\'<?xml version="1.0" encoding="UTF-8" standalone="no"?><flow xmlns="urn:opendaylight:flow:inventory"><priority>32767</priority><flow-name>Flujo 2</flow-name><match><in-port>' + str(outport) +'</in-port><ipv4-destination>'+ h2 +'/32</ipv4-destination><ipv4-source>'+ h1 +'/32</ipv4-source><ethernet-match><ethernet-type><type>2048</type></ethernet-type></ethernet-match></match><id>2</id><table_id>0</table_id><instructions><instruction><order>0</order><apply-actions><action><order>0</order><output-action><output-node-connector>' + str(inport) +'</output-node-connector></output-action></action></apply-actions></instruction></instructions></flow>\''		
		
		flowURL = "http://127.0.0.1:8181/restconf/config/opendaylight-inventory:nodes/node/openflow:"+ bestPath[currentNode] +"/table/0/flow/1"
		command = 'curl --user "admin":"admin" -H "Accept: application/xml" -H "Content-type: application/xml" -X PUT ' + flowURL + ' -d ' + flujo1
		systemCommand(command)
		print flowURL
		print "\nCreando flujos\n"

		flowURL = "http://127.0.0.1:8181/restconf/config/opendaylight-inventory:nodes/node/openflow:"+ bestPath[currentNode] +"/table/0/flow/2"
		command = 'curl --user "admin":"admin" -H "Accept: application/xml" -H "Content-type: application/xml" -X PUT ' + flowURL + ' -d ' + flujo2
		systemCommand(command)
		print flowURL
		print "\nCreando flujos\n"

	srcNode = bestPath[-1]
	prevNode = bestPath[-2]
	inport = linkPorts[prevNode + "::" + srcNode]
	inport = inport.split("::")[1]
	outport = hostPorts[h1]
	
	flujo1='\'<?xml version="1.0" encoding="UTF-8" standalone="no"?><flow xmlns="urn:opendaylight:flow:inventory"><priority>32767</priority><flow-name>Flujo 1</flow-name><match><in-port>' + str(inport) +'</in-port><ipv4-destination>'+ h1 +'/32</ipv4-destination><ipv4-source>'+ h2 +'/32</ipv4-source><ethernet-match><ethernet-type><type>2048</type></ethernet-type></ethernet-match></match><id>1</id><table_id>0</table_id><instructions><instruction><order>0</order><apply-actions><action><order>0</order><output-action><output-node-connector>' + str(outport) +'</output-node-connector></output-action></action> </apply-actions></instruction></instructions></flow>\''
	flujo2='\'<?xml version="1.0" encoding="UTF-8" standalone="no"?><flow xmlns="urn:opendaylight:flow:inventory"><priority>32767</priority><flow-name>Flujo 2</flow-name><match><in-port>' + str(outport) +'</in-port><ipv4-destination>'+ h2 +'/32</ipv4-destination><ipv4-source>'+ h1 +'/32</ipv4-source><ethernet-match><ethernet-type><type>2048</type></ethernet-type></ethernet-match></match><id>1</id><table_id>0</table_id><instructions><instruction><order>0</order><apply-actions><action><order>0</order><output-action><output-node-connector>' + str(inport) +'</output-node-connector></output-action></action></apply-actions></instruction></instructions></flow>\''		
	flowURL = "http://127.0.0.1:8181/restconf/config/opendaylight-inventory:nodes/node/openflow:"+ bestPath[-1] +"/table/0/flow/1"
	command = 'curl --user \"admin\":\"admin\" -H \"Accept: application/xml\" -H \"Content-type: application/xml\" -X PUT ' + flowURL + ' -d ' + flujo1
	systemCommand(command)
	print flowURL
	print "\nCreando flujos\n"

	flowURL = "http://127.0.0.1:8181/restconf/config/opendaylight-inventory:nodes/node/openflow:"+ bestPath[-1] +"/table/0/flow/2"
	command = 'curl --user "admin":"admin" -H "Accept: application/xml" -H "Content-type: application/xml" -X PUT ' + flowURL + ' -d ' + flujo2
	systemCommand(command)
	print flowURL
	print "\nCreando flujos\n"

#FUNCION 6: ELIMINA LOS FLUJOS CREADOS EN EL SWITCH
def delete_flujos(bestPath):

	bestPath = bestPath.split("::")

	for currentNode in range(0, len(bestPath)-1):
		if (currentNode==0):
			inport = hostPorts[h2]
			srcNode = bestPath[currentNode]
			dstNode = bestPath[currentNode+1]
			outport = linkPorts[srcNode + "::" + dstNode]
			outport = outport[0]
		else:
			prevNode = bestPath[currentNode-1]
			#print prevNode
			srcNode = bestPath[currentNode]
			#print srcNode
			dstNode = bestPath[currentNode+1]
			inport = linkPorts[prevNode + "::" + srcNode]
			inport = inport.split("::")[1]
			outport = linkPorts[srcNode + "::" + dstNode]
			outport = outport.split("::")[0]
			
		flujo1='\'<?xml version="1.0" encoding="UTF-8" standalone="no"?><flow xmlns="urn:opendaylight:flow:inventory"><priority>32767</priority><flow-name>Flujo 1</flow-name><match><in-port>' + str(inport) +'</in-port><ipv4-destination>'+ h1 +'/32</ipv4-destination><ipv4-source>'+ h2 +'/32</ipv4-source><ethernet-match><ethernet-type><type>2048</type></ethernet-type></ethernet-match></match><id>1</id><table_id>0</table_id><instructions><instruction><order>0</order><apply-actions><action><order>0</order><output-action><output-node-connector>' + str(outport) +'</output-node-connector></output-action></action> </apply-actions></instruction></instructions></flow>\''
		flujo2='\'<?xml version="1.0" encoding="UTF-8" standalone="no"?><flow xmlns="urn:opendaylight:flow:inventory"><priority>32767</priority><flow-name>Flujo 2</flow-name><match><in-port>' + str(outport) +'</in-port><ipv4-destination>'+ h2 +'/32</ipv4-destination><ipv4-source>'+ h1 +'/32</ipv4-source><ethernet-match><ethernet-type><type>2048</type></ethernet-type></ethernet-match></match><id>2</id><table_id>0</table_id><instructions><instruction><order>0</order><apply-actions><action><order>0</order><output-action><output-node-connector>' + str(inport) +'</output-node-connector></output-action></action></apply-actions></instruction></instructions></flow>\''		
		
		flowURL = "http://127.0.0.1:8181/restconf/config/opendaylight-inventory:nodes/node/openflow:"+ bestPath[currentNode] +"/table/0/flow/1"
		command = 'curl --user "admin":"admin" -H "Accept: application/xml" -H "Content-type: application/xml" -X DELETE ' + flowURL
		systemCommand(command)
		print "\nEliminando flujos\n"

		flowURL = "http://127.0.0.1:8181/restconf/config/opendaylight-inventory:nodes/node/openflow:"+ bestPath[currentNode] +"/table/0/flow/2"
		command = 'curl --user "admin":"admin" -H "Accept: application/xml" -H "Content-type: application/xml" -X DELETE ' + flowURL
		systemCommand(command)
		print "\nEliminando flujos\n"

	srcNode = bestPath[-1]
	prevNode = bestPath[-2]
	inport = linkPorts[prevNode + "::" + srcNode]
	inport = inport.split("::")[1]
	outport = hostPorts[h1]
	
	flujo1='\'<?xml version="1.0" encoding="UTF-8" standalone="no"?><flow xmlns="urn:opendaylight:flow:inventory"><priority>32767</priority><flow-name>Flujo 1</flow-name><match><in-port>' + str(inport) +'</in-port><ipv4-destination>'+ h1 +'/32</ipv4-destination><ipv4-source>'+ h2 +'/32</ipv4-source><ethernet-match><ethernet-type><type>2048</type></ethernet-type></ethernet-match></match><id>1</id><table_id>0</table_id><instructions><instruction><order>0</order><apply-actions><action><order>0</order><output-action><output-node-connector>' + str(outport) +'</output-node-connector></output-action></action> </apply-actions></instruction></instructions></flow>\''
	flujo2='\'<?xml version="1.0" encoding="UTF-8" standalone="no"?><flow xmlns="urn:opendaylight:flow:inventory"><priority>32767</priority><flow-name>Flujo 2</flow-name><match><in-port>' + str(outport) +'</in-port><ipv4-destination>'+ h2 +'/32</ipv4-destination><ipv4-source>'+ h1 +'/32</ipv4-source><ethernet-match><ethernet-type><type>2048</type></ethernet-type></ethernet-match></match><id>1</id><table_id>0</table_id><instructions><instruction><order>0</order><apply-actions><action><order>0</order><output-action><output-node-connector>' + str(inport) +'</output-node-connector></output-action></action></apply-actions></instruction></instructions></flow>\''		
	flowURL = "http://127.0.0.1:8181/restconf/config/opendaylight-inventory:nodes/node/openflow:"+ bestPath[-1] +"/table/0/flow/1"
	command = 'curl --user \"admin\":\"admin\" -H \"Accept: application/xml\" -H \"Content-type: application/xml\" -X DELETE ' + flowURL
	systemCommand(command)
	print "\nEliminando flujos\n"

	flowURL = "http://127.0.0.1:8181/restconf/config/opendaylight-inventory:nodes/node/openflow:"+ bestPath[-1] +"/table/0/flow/2"
	command = 'curl --user "admin":"admin" -H "Accept: application/xml" -H "Content-type: application/xml" -X DELETE ' + flowURL
	systemCommand(command)
	print "\nEliminando flujos\n"
	
#PROGRAMA PRINCIPAL

#CREACIÓN DE VARIABLES
global h1,h2,h3
borrar = 0
ejecutar = 0

h1 = ""
h2 = ""
h3 = ""

#INICIALIZACIÓN DE VARIABLES IP ORIGEN/IP DESTINO
print "Ingrese Host 1: Cliente Origen"
h1 = int(input())
print "\nIngrese Host 2: Destino"
h2 = int(input())
print "\nIngrese Host 3: Vecino de Host 1"
h3 = int(input())

h1 = "10.0.0." + str(h1)
h2 = "10.0.0." + str(h2)
h3 = "10.0.0." + str(h3)

#CICLO PRINCIPAL
flag = True
while flag:

	#CREACIÓN E INICIALIZACIÓN DE VARIABLES

	global stats
	stats = ""
	global cost
	cost = 0

	G = nx.Graph() 
	switch = {}
	deviceMAC = {}
	deviceIP = {}
	switchLinks = {}
	hostPorts = {}
	path = {}
	linkPorts = {}
	finalLinkTX = {}	

	try:
 		#Llamado a funcion para obtener informacion de la topologia
		topology = "http://127.0.0.1:8181/restconf/operational/network-topology:network-topology"
		getResponse(topology,"topology")

		#Imprimir Dir MAC y Dir OP
		print "\nDirecciones IP y MAC de los dispositivos\n"
		print deviceMAC

		#Imprimir Conexiones Switch
		print "\nDispositivos Conectados a Cada Switch\n"
		print switch

		#Imprimir Puertos
		print "\nPuertos de Conexion entre Host y Switch\n"
		print hostPorts

		#Imprimir Enlaces entre Switchs
		print "\nConexiones entre Switchs\n"
		print linkPorts

		#Caminos
		print "\nTodos los Caminos\n"
		for path in nx.all_shortest_paths(G, source=int(switch[h2].split(":",1)[1]), target=int(switch[h1].split(":",1)[1]), weight=None):
			print path

		#Calculo de Costo
		tmp = ""
		for currentPath in nx.all_shortest_paths(G, source=int(switch[h2].split(":",1)[1]), target=int(switch[h1].split(":",1)[1]), weight=None):
			for node in range(0,len(currentPath)-1):
				tmp = tmp + str(currentPath[node]) + "::"
				key = str(currentPath[node])+ "::" + str(currentPath[node+1])
				port = linkPorts[key]
				port = port.split(":",1)[0]
				port = int(port)

                #Llamado a funcion para obtener estadisticas de la red
				stats = "http://localhost:8181/restconf/operational/opendaylight-inventory:nodes/node/openflow:"+str(currentPath[node])+"/node-connector/openflow:"+str(currentPath[node])+":"+str(port)
				getResponse(stats,"statistics")

			tmp = tmp + str(currentPath[len(currentPath)-1])
			tmp = tmp.strip("::") #Muestra los nodos del camino elegido
			finalLinkTX[tmp] = cost #Costo total del camino
			cost = 0
			tmp = ""

		print "\nCosto Final del Enlace\n"
		print finalLinkTX
		
		shortestPath = min(finalLinkTX, key=finalLinkTX.get) #Funcion para calcular la menor ruta
		print "\n\nMejor Camino: ",shortestPath
		
		#CREACIÓN DE FLUJOS
		print "Ingrese 1 si desea crear los flujos"
		crear = int(input())
		
		if (crear):
			crear_flujos(shortestPath)
			print "\nFLujos Completos\n"
		
		#BORRAR FLUJOS CREADOS
		print "Ingrese 1 si desea borrar los flujos"
		borrar = int(input())
		
		if (borrar):
			delete_flujos(shortestPath)

		#DETENER EJECUCION	
		print "Ingrese 1 si desea detener ejecucion"
		ejecutar = int(input())

		if (ejecutar):
			flag = False
		        
	except KeyboardInterrupt:
		break
		exit

