#PROGRAMA PARA SISTEMA DE ENRUTAMIENTO RED FISICA

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
			getStats(url,jData)
	else:
		#Funcion para verificar mensaje de error en el GET
		response.raise_for_status()

#FUNCION 2: OBTIENE ESTADISTICAS DE RED EN FORMATO JSON
def getStats(url, datos):
	global tx
	for i in datos["node-connector"]:
        #Tx almacena estadisticas de paquetes transmitidos: bytes transmitidos
		tx = int(i["opendaylight-port-statistics:flow-capable-node-connector-statistics"]["packets"]["transmitted"])

#FUNCION 3: CALCULA EL PORCENTAJE DE UN VALOR
def porcentaje(porcentaje,valor):
	return (porcentaje * valor) / 100
	
#FUNCION 4: ELIMINA LOS FLUJOS CREADOS EN EL SWITCH
def delete_flujos(ip,port):
	
	global ip_origen, ip_surrogate1, ip_surrogate2, ip_client1, ip_client2, ip_client3, ip_client4, ip_client5
	global port_origen, port_surrogate1, port_surrogate2, port_client1, port_client2, port_client3, port_client4, port_client5
	
	ip_server = ip
	port_server = port
	
	name = "Flujo1"
	port_client = port_client1
	ip_client = ip_client1
	flujo1 = '\'<?xml version="1.0" encoding="UTF-8" standalone="no"?> <flow xmlns="urn:opendaylight:flow:inventory"> <priority>32769</priority> <flow-name>'+ name +'</flow-name> <match> <in-port>'+ port_client +'</in-port> <ipv4-destination>'+ ip_server +'/32</ipv4-destination> <ipv4-source>'+ ip_client +'/32</ipv4-source> <ethernet-match><ethernet-type><type>2048</type></ethernet-type></ethernet-match> </match> <id>1</id> <table_id>1</table_id> <instructions> <instruction> <order>0</order> <apply-actions> <action> <order>0</order> <output-action> <output-node-connector>'+ port_server +'</output-node-connector> </output-action> </action> </apply-actions> </instruction> </instructions> </flow>\''
	flowURL1 = "http://localhost:8181/restconf/config/opendaylight-inventory:nodes/node/openflow:444361092207433/table/1/flow/1"
	command = 'curl --user \"admin\":\"admin\" -H \"Accept: application/xml\" -H \"Content-type: application/xml\" -X DELETE ' + flowURL1
	systemCommand(command)
	
	
	name = "Flujo2"
	flowURL2 = "http://localhost:8181/restconf/config/opendaylight-inventory:nodes/node/openflow:444361092207433/table/1/flow/2"
	flujo2 = '\'<?xml version="1.0" encoding="UTF-8" standalone="no"?> <flow xmlns="urn:opendaylight:flow:inventory"> <priority>32769</priority> <flow-name>'+ name +'</flow-name> <match> <in-port>'+ port_server +'</in-port> <ipv4-destination>'+ ip_client +'/32</ipv4-destination> <ipv4-source>'+ip_server +'/32</ipv4-source> <ethernet-match><ethernet-type><type>2048</type></ethernet-type></ethernet-match> </match> <id>2</id> <table_id>1</table_id> <instructions> <instruction> <order>0</order> <apply-actions> <action> <order>0</order> <output-action> <output-node-connector>'+ port_client +'</output-node-connector> </output-action> </action> </apply-actions> </instruction> </instructions> </flow>\''
	command = 'curl --user \"admin\":\"admin\" -H \"Accept: application/xml\" -H \"Content-type: application/xml\" -X DELETE ' + flowURL2
	systemCommand(command)
	
	
	name = "Flujo3"
	port_client = port_client2
	ip_client = ip_client2
	flujo1 = '\'<?xml version="1.0" encoding="UTF-8" standalone="no"?> <flow xmlns="urn:opendaylight:flow:inventory"> <priority>32769</priority> <flow-name>'+ name +'</flow-name> <match> <in-port>'+ port_client +'</in-port> <ipv4-destination>'+ ip_server +'/32</ipv4-destination> <ipv4-source>'+ ip_client +'/32</ipv4-source> <ethernet-match><ethernet-type><type>2048</type></ethernet-type></ethernet-match> </match> <id>1</id> <table_id>1</table_id> <instructions> <instruction> <order>0</order> <apply-actions> <action> <order>0</order> <output-action> <output-node-connector>'+ port_server +'</output-node-connector> </output-action> </action> </apply-actions> </instruction> </instructions> </flow>\''
	flowURL3 = "http://localhost:8181/restconf/config/opendaylight-inventory:nodes/node/openflow:444361092207433/table/1/flow/1"
	command = 'curl --user \"admin\":\"admin\" -H \"Accept: application/xml\" -H \"Content-type: application/xml\" -X DELETE ' + flowURL3
	systemCommand(command)
	
	
	name = "Flujo4"
	flowURL4 = "http://localhost:8181/restconf/config/opendaylight-inventory:nodes/node/openflow:444361092207433/table/1/flow/2"
	flujo2 = '\'<?xml version="1.0" encoding="UTF-8" standalone="no"?> <flow xmlns="urn:opendaylight:flow:inventory"> <priority>32769</priority> <flow-name>'+ name +'</flow-name> <match> <in-port>'+ port_server +'</in-port> <ipv4-destination>'+ ip_client +'/32</ipv4-destination> <ipv4-source>'+ip_server +'/32</ipv4-source> <ethernet-match><ethernet-type><type>2048</type></ethernet-type></ethernet-match> </match> <id>2</id> <table_id>1</table_id> <instructions> <instruction> <order>0</order> <apply-actions> <action> <order>0</order> <output-action> <output-node-connector>'+ port_client +'</output-node-connector> </output-action> </action> </apply-actions> </instruction> </instructions> </flow>\''
	command = 'curl --user \"admin\":\"admin\" -H \"Accept: application/xml\" -H \"Content-type: application/xml\" -X DELETE ' + flowURL4
	systemCommand(command)
	
	
	
	name = "Flujo5"
	port_client = port_client3
	ip_client = ip_client3
	flujo1 = '\'<?xml version="1.0" encoding="UTF-8" standalone="no"?> <flow xmlns="urn:opendaylight:flow:inventory"> <priority>32769</priority> <flow-name>'+ name +'</flow-name> <match> <in-port>'+ port_client +'</in-port> <ipv4-destination>'+ ip_server +'/32</ipv4-destination> <ipv4-source>'+ ip_client +'/32</ipv4-source> <ethernet-match><ethernet-type><type>2048</type></ethernet-type></ethernet-match> </match> <id>1</id> <table_id>1</table_id> <instructions> <instruction> <order>0</order> <apply-actions> <action> <order>0</order> <output-action> <output-node-connector>'+ port_server +'</output-node-connector> </output-action> </action> </apply-actions> </instruction> </instructions> </flow>\''
	flowURL5 = "http://localhost:8181/restconf/config/opendaylight-inventory:nodes/node/openflow:444361092207433/table/1/flow/1"
	command = 'curl --user \"admin\":\"admin\" -H \"Accept: application/xml\" -H \"Content-type: application/xml\" -X DELETE ' + flowURL5
	systemCommand(command)
	
	
	name = "Flujo6"
	flowURL6 = "http://localhost:8181/restconf/config/opendaylight-inventory:nodes/node/openflow:444361092207433/table/1/flow/2"
	flujo2 = '\'<?xml version="1.0" encoding="UTF-8" standalone="no"?> <flow xmlns="urn:opendaylight:flow:inventory"> <priority>32769</priority> <flow-name>'+ name +'</flow-name> <match> <in-port>'+ port_server +'</in-port> <ipv4-destination>'+ ip_client +'/32</ipv4-destination> <ipv4-source>'+ip_server +'/32</ipv4-source> <ethernet-match><ethernet-type><type>2048</type></ethernet-type></ethernet-match> </match> <id>2</id> <table_id>1</table_id> <instructions> <instruction> <order>0</order> <apply-actions> <action> <order>0</order> <output-action> <output-node-connector>'+ port_client +'</output-node-connector> </output-action> </action> </apply-actions> </instruction> </instructions> </flow>\''
	command = 'curl --user \"admin\":\"admin\" -H \"Accept: application/xml\" -H \"Content-type: application/xml\" -X DELETE ' + flowURL6
	systemCommand(command)
	
	
	
	
	name = "Flujo7"
	port_client = port_client4
	ip_client = ip_client4
	flujo1 = '\'<?xml version="1.0" encoding="UTF-8" standalone="no"?> <flow xmlns="urn:opendaylight:flow:inventory"> <priority>32769</priority> <flow-name>'+ name +'</flow-name> <match> <in-port>'+ port_client +'</in-port> <ipv4-destination>'+ ip_server +'/32</ipv4-destination> <ipv4-source>'+ ip_client +'/32</ipv4-source> <ethernet-match><ethernet-type><type>2048</type></ethernet-type></ethernet-match> </match> <id>1</id> <table_id>1</table_id> <instructions> <instruction> <order>0</order> <apply-actions> <action> <order>0</order> <output-action> <output-node-connector>'+ port_server +'</output-node-connector> </output-action> </action> </apply-actions> </instruction> </instructions> </flow>\''
	flowURL7 = "http://localhost:8181/restconf/config/opendaylight-inventory:nodes/node/openflow:444361092207433/table/1/flow/1"
	command = 'curl --user \"admin\":\"admin\" -H \"Accept: application/xml\" -H \"Content-type: application/xml\" -X DELETE ' + flowURL7
	systemCommand(command)
	
	
	name = "Flujo8"
	flowURL8 = "http://localhost:8181/restconf/config/opendaylight-inventory:nodes/node/openflow:444361092207433/table/1/flow/2"
	flujo2 = '\'<?xml version="1.0" encoding="UTF-8" standalone="no"?> <flow xmlns="urn:opendaylight:flow:inventory"> <priority>32769</priority> <flow-name>'+ name +'</flow-name> <match> <in-port>'+ port_server +'</in-port> <ipv4-destination>'+ ip_client +'/32</ipv4-destination> <ipv4-source>'+ip_server +'/32</ipv4-source> <ethernet-match><ethernet-type><type>2048</type></ethernet-type></ethernet-match> </match> <id>2</id> <table_id>1</table_id> <instructions> <instruction> <order>0</order> <apply-actions> <action> <order>0</order> <output-action> <output-node-connector>'+ port_client +'</output-node-connector> </output-action> </action> </apply-actions> </instruction> </instructions> </flow>\''
	command = 'curl --user \"admin\":\"admin\" -H \"Accept: application/xml\" -H \"Content-type: application/xml\" -X DELETE ' + flowURL8
	systemCommand(command)
	
	
	
	
	name = "Flujo9"
	port_client = port_client5
	ip_client = ip_client5
	flujo1 = '\'<?xml version="1.0" encoding="UTF-8" standalone="no"?> <flow xmlns="urn:opendaylight:flow:inventory"> <priority>32769</priority> <flow-name>'+ name +'</flow-name> <match> <in-port>'+ port_client +'</in-port> <ipv4-destination>'+ ip_server +'/32</ipv4-destination> <ipv4-source>'+ ip_client +'/32</ipv4-source> <ethernet-match><ethernet-type><type>2048</type></ethernet-type></ethernet-match> </match> <id>1</id> <table_id>1</table_id> <instructions> <instruction> <order>0</order> <apply-actions> <action> <order>0</order> <output-action> <output-node-connector>'+ port_server +'</output-node-connector> </output-action> </action> </apply-actions> </instruction> </instructions> </flow>\''
	flowURL9 = "http://localhost:8181/restconf/config/opendaylight-inventory:nodes/node/openflow:444361092207433/table/1/flow/1"
	command = 'curl --user \"admin\":\"admin\" -H \"Accept: application/xml\" -H \"Content-type: application/xml\" -X DELETE ' + flowURL9
	systemCommand(command)
	
	
	name = "Flujo10"
	flowURL10 = "http://localhost:8181/restconf/config/opendaylight-inventory:nodes/node/openflow:444361092207433/table/1/flow/2"
	flujo2 = '\'<?xml version="1.0" encoding="UTF-8" standalone="no"?> <flow xmlns="urn:opendaylight:flow:inventory"> <priority>32769</priority> <flow-name>'+ name +'</flow-name> <match> <in-port>'+ port_server +'</in-port> <ipv4-destination>'+ ip_client +'/32</ipv4-destination> <ipv4-source>'+ip_server +'/32</ipv4-source> <ethernet-match><ethernet-type><type>2048</type></ethernet-type></ethernet-match> </match> <id>2</id> <table_id>1</table_id> <instructions> <instruction> <order>0</order> <apply-actions> <action> <order>0</order> <output-action> <output-node-connector>'+ port_client +'</output-node-connector> </output-action> </action> </apply-actions> </instruction> </instructions> </flow>\''
	command = 'curl --user \"admin\":\"admin\" -H \"Accept: application/xml\" -H \"Content-type: application/xml\" -X DELETE ' + flowURL10
	systemCommand(command)
	
#FUNCION 5: CREA LOS FLUJOS EN EL SWITCH
def crear_flujos(ip,port):
	
	ip_server = ip
	port_server = port
	
	name = "Flujo1"
	port_client = port_client1
	ip_client = ip_client1
	flujo1 = '\'<?xml version="1.0" encoding="UTF-8" standalone="no"?> <flow xmlns="urn:opendaylight:flow:inventory"> <priority>32769</priority> <flow-name>'+ name +'</flow-name> <match> <in-port>'+ port_client +'</in-port> <ipv4-destination>'+ ip_server +'/32</ipv4-destination> <ipv4-source>'+ ip_client +'/32</ipv4-source> <ethernet-match><ethernet-type><type>2048</type></ethernet-type></ethernet-match> </match> <id>1</id> <table_id>1</table_id> <instructions> <instruction> <order>0</order> <apply-actions> <action> <order>0</order> <output-action> <output-node-connector>'+ port_server +'</output-node-connector> </output-action> </action> </apply-actions> </instruction> </instructions> </flow>\''
	flowURL1 = "http://localhost:8181/restconf/config/opendaylight-inventory:nodes/node/openflow:444361092207433/table/1/flow/1"
	command = 'curl --user "admin":"admin" -H "Accept: application/xml" -H "Content-type: application/xml" -X PUT ' + flowURL1 + ' -d ' + flujo1
	systemCommand(command)
	
	
	name = "Flujo2"
	flowURL2 = "http://localhost:8181/restconf/config/opendaylight-inventory:nodes/node/openflow:444361092207433/table/1/flow/2"
	flujo2 = '\'<?xml version="1.0" encoding="UTF-8" standalone="no"?> <flow xmlns="urn:opendaylight:flow:inventory"> <priority>32769</priority> <flow-name>'+ name +'</flow-name> <match> <in-port>'+ port_server +'</in-port> <ipv4-destination>'+ ip_client +'/32</ipv4-destination> <ipv4-source>'+ip_server +'/32</ipv4-source> <ethernet-match><ethernet-type><type>2048</type></ethernet-type></ethernet-match> </match> <id>2</id> <table_id>1</table_id> <instructions> <instruction> <order>0</order> <apply-actions> <action> <order>0</order> <output-action> <output-node-connector>'+ port_client +'</output-node-connector> </output-action> </action> </apply-actions> </instruction> </instructions> </flow>\''
	command = 'curl --user "admin":"admin" -H "Accept: application/xml" -H "Content-type: application/xml" -X PUT ' + flowURL2 + ' -d ' + flujo2
	systemCommand(command)
	
	
	name = "Flujo3"
	port_client = port_client2
	ip_client = ip_client2
	flujo1 = '\'<?xml version="1.0" encoding="UTF-8" standalone="no"?> <flow xmlns="urn:opendaylight:flow:inventory"> <priority>32769</priority> <flow-name>'+ name +'</flow-name> <match> <in-port>'+ port_client +'</in-port> <ipv4-destination>'+ ip_server +'/32</ipv4-destination> <ipv4-source>'+ ip_client +'/32</ipv4-source> <ethernet-match><ethernet-type><type>2048</type></ethernet-type></ethernet-match> </match> <id>1</id> <table_id>1</table_id> <instructions> <instruction> <order>0</order> <apply-actions> <action> <order>0</order> <output-action> <output-node-connector>'+ port_server +'</output-node-connector> </output-action> </action> </apply-actions> </instruction> </instructions> </flow>\''
	flowURL3 = "http://localhost:8181/restconf/config/opendaylight-inventory:nodes/node/openflow:444361092207433/table/1/flow/1"
	command = 'curl --user "admin":"admin" -H "Accept: application/xml" -H "Content-type: application/xml" -X PUT ' + flowURL3 + ' -d ' + flujo1
	systemCommand(command)
	
	
	name = "Flujo4"
	flowURL4 = "http://localhost:8181/restconf/config/opendaylight-inventory:nodes/node/openflow:444361092207433/table/1/flow/2"
	flujo2 = '\'<?xml version="1.0" encoding="UTF-8" standalone="no"?> <flow xmlns="urn:opendaylight:flow:inventory"> <priority>32769</priority> <flow-name>'+ name +'</flow-name> <match> <in-port>'+ port_server +'</in-port> <ipv4-destination>'+ ip_client +'/32</ipv4-destination> <ipv4-source>'+ip_server +'/32</ipv4-source> <ethernet-match><ethernet-type><type>2048</type></ethernet-type></ethernet-match> </match> <id>2</id> <table_id>1</table_id> <instructions> <instruction> <order>0</order> <apply-actions> <action> <order>0</order> <output-action> <output-node-connector>'+ port_client +'</output-node-connector> </output-action> </action> </apply-actions> </instruction> </instructions> </flow>\''
	command = 'curl --user "admin":"admin" -H "Accept: application/xml" -H "Content-type: application/xml" -X PUT ' + flowURL4 + ' -d ' + flujo2
	systemCommand(command)
	
	
	
	name = "Flujo5"
	port_client = port_client3
	ip_client = ip_client3
	flujo1 = '\'<?xml version="1.0" encoding="UTF-8" standalone="no"?> <flow xmlns="urn:opendaylight:flow:inventory"> <priority>32769</priority> <flow-name>'+ name +'</flow-name> <match> <in-port>'+ port_client +'</in-port> <ipv4-destination>'+ ip_server +'/32</ipv4-destination> <ipv4-source>'+ ip_client +'/32</ipv4-source> <ethernet-match><ethernet-type><type>2048</type></ethernet-type></ethernet-match> </match> <id>1</id> <table_id>1</table_id> <instructions> <instruction> <order>0</order> <apply-actions> <action> <order>0</order> <output-action> <output-node-connector>'+ port_server +'</output-node-connector> </output-action> </action> </apply-actions> </instruction> </instructions> </flow>\''
	flowURL5 = "http://localhost:8181/restconf/config/opendaylight-inventory:nodes/node/openflow:444361092207433/table/1/flow/1"
	command = 'curl --user "admin":"admin" -H "Accept: application/xml" -H "Content-type: application/xml" -X PUT ' + flowURL5 + ' -d ' + flujo1
	systemCommand(command)
	
	
	name = "Flujo6"
	flowURL6 = "http://localhost:8181/restconf/config/opendaylight-inventory:nodes/node/openflow:444361092207433/table/1/flow/2"
	flujo2 = '\'<?xml version="1.0" encoding="UTF-8" standalone="no"?> <flow xmlns="urn:opendaylight:flow:inventory"> <priority>32769</priority> <flow-name>'+ name +'</flow-name> <match> <in-port>'+ port_server +'</in-port> <ipv4-destination>'+ ip_client +'/32</ipv4-destination> <ipv4-source>'+ip_server +'/32</ipv4-source> <ethernet-match><ethernet-type><type>2048</type></ethernet-type></ethernet-match> </match> <id>2</id> <table_id>1</table_id> <instructions> <instruction> <order>0</order> <apply-actions> <action> <order>0</order> <output-action> <output-node-connector>'+ port_client +'</output-node-connector> </output-action> </action> </apply-actions> </instruction> </instructions> </flow>\''
	command = 'curl --user "admin":"admin" -H "Accept: application/xml" -H "Content-type: application/xml" -X PUT ' + flowURL6 + ' -d ' + flujo2
	systemCommand(command)
	
	
	
	name = "Flujo7"
	port_client = port_client4
	ip_client = ip_client4
	flujo1 = '\'<?xml version="1.0" encoding="UTF-8" standalone="no"?> <flow xmlns="urn:opendaylight:flow:inventory"> <priority>32769</priority> <flow-name>'+ name +'</flow-name> <match> <in-port>'+ port_client +'</in-port> <ipv4-destination>'+ ip_server +'/32</ipv4-destination> <ipv4-source>'+ ip_client +'/32</ipv4-source> <ethernet-match><ethernet-type><type>2048</type></ethernet-type></ethernet-match> </match> <id>1</id> <table_id>1</table_id> <instructions> <instruction> <order>0</order> <apply-actions> <action> <order>0</order> <output-action> <output-node-connector>'+ port_server +'</output-node-connector> </output-action> </action> </apply-actions> </instruction> </instructions> </flow>\''
	flowURL7 = "http://localhost:8181/restconf/config/opendaylight-inventory:nodes/node/openflow:444361092207433/table/1/flow/1"
	command = 'curl --user "admin":"admin" -H "Accept: application/xml" -H "Content-type: application/xml" -X PUT ' + flowURL7 + ' -d ' + flujo1
	systemCommand(command)
	
	name = "Flujo8"
	flowURL8 = "http://localhost:8181/restconf/config/opendaylight-inventory:nodes/node/openflow:444361092207433/table/1/flow/2"
	flujo2 = '\'<?xml version="1.0" encoding="UTF-8" standalone="no"?> <flow xmlns="urn:opendaylight:flow:inventory"> <priority>32769</priority> <flow-name>'+ name +'</flow-name> <match> <in-port>'+ port_server +'</in-port> <ipv4-destination>'+ ip_client +'/32</ipv4-destination> <ipv4-source>'+ip_server +'/32</ipv4-source> <ethernet-match><ethernet-type><type>2048</type></ethernet-type></ethernet-match> </match> <id>2</id> <table_id>1</table_id> <instructions> <instruction> <order>0</order> <apply-actions> <action> <order>0</order> <output-action> <output-node-connector>'+ port_client +'</output-node-connector> </output-action> </action> </apply-actions> </instruction> </instructions> </flow>\''
	command = 'curl --user "admin":"admin" -H "Accept: application/xml" -H "Content-type: application/xml" -X PUT ' + flowURL8 + ' -d ' + flujo2
	systemCommand(command)
	
	
	name = "Flujo9"
	port_client = port_client5
	ip_client = ip_client5
	flujo1 = '\'<?xml version="1.0" encoding="UTF-8" standalone="no"?> <flow xmlns="urn:opendaylight:flow:inventory"> <priority>32769</priority> <flow-name>'+ name +'</flow-name> <match> <in-port>'+ port_client +'</in-port> <ipv4-destination>'+ ip_server +'/32</ipv4-destination> <ipv4-source>'+ ip_client +'/32</ipv4-source> <ethernet-match><ethernet-type><type>2048</type></ethernet-type></ethernet-match> </match> <id>1</id> <table_id>1</table_id> <instructions> <instruction> <order>0</order> <apply-actions> <action> <order>0</order> <output-action> <output-node-connector>'+ port_server +'</output-node-connector> </output-action> </action> </apply-actions> </instruction> </instructions> </flow>\''
	flowURL9 = "http://localhost:8181/restconf/config/opendaylight-inventory:nodes/node/openflow:444361092207433/table/1/flow/1"
	command = 'curl --user "admin":"admin" -H "Accept: application/xml" -H "Content-type: application/xml" -X PUT ' + flowURL9 + ' -d ' + flujo1
	systemCommand(command)
	
	name = "Flujo10"
	flowURL10 = "http://localhost:8181/restconf/config/opendaylight-inventory:nodes/node/openflow:444361092207433/table/1/flow/2"
	flujo2 = '\'<?xml version="1.0" encoding="UTF-8" standalone="no"?> <flow xmlns="urn:opendaylight:flow:inventory"> <priority>32769</priority> <flow-name>'+ name +'</flow-name> <match> <in-port>'+ port_server +'</in-port> <ipv4-destination>'+ ip_client +'/32</ipv4-destination> <ipv4-source>'+ip_server +'/32</ipv4-source> <ethernet-match><ethernet-type><type>2048</type></ethernet-type></ethernet-match> </match> <id>2</id> <table_id>1</table_id> <instructions> <instruction> <order>0</order> <apply-actions> <action> <order>0</order> <output-action> <output-node-connector>'+ port_client +'</output-node-connector> </output-action> </action> </apply-actions> </instruction> </instructions> </flow>\''
	command = 'curl --user "admin":"admin" -H "Accept: application/xml" -H "Content-type: application/xml" -X PUT ' + flowURL10 + ' -d ' + flujo2
	systemCommand(command)

#FUNCION 6: PERMITE EJECUTAR COMANDOS EN CMD
def systemCommand(cmd):
	terminalProcess = Popen(cmd, stdout=PIPE, stderr=PIPE, shell=True)
	terminalOutput,stderr = terminalProcess.communicate()

#PROGRAMA PRINCIPAL

#CREACIÓN DE VARIABLES GLOBALES
global servidor_origen, surrogate_1, surrogate_2
global cost_origen, cost_1, cost_2	
global ip_origen, ip_surrogate1, ip_surrogate2, ip_client1, ip_client2, ip_client3, ip_client4, ip_client5
global port_origen, port_surrogate1, port_surrogate2, port_client1, port_client2, port_client3, port_client4, port_client5

#INICIALIZACIÓN DE VARIABLES CON INFORMACION DE RED
servidor_origen = ""
surrogate_1 = ""
surrogate_2 = ""
ip_origen = "50.0.0.3"
ip_surrogate1 = "50.0.0.4"
ip_surrogate2 = "50.0.0.5"
port_origen = "8"
port_surrogate1 = "9"
port_surrogate2 = "10"
port_client1 = "11"
port_client2 = "12"
port_client3 = "13"
port_client4 = "14"
port_client5 = "15"
ip_client1 = "50.0.0.6"
ip_client2 = "50.0.0.7"
ip_client3 = "50.0.0.8"
ip_client4 = "50.0.0.9"
ip_client5 = "50.0.0.10"

#URL PARA SOLICITUD DE ESTADISTICAS
servidor_origen = "http://localhost:8181/restconf/operational/opendaylight-inventory:nodes/node/openflow:444361092207433/node-connector/openflow:444361092207433:8"
surrogate_1 = "http://localhost:8181/restconf/operational/opendaylight-inventory:nodes/node/openflow:444361092207433/node-connector/openflow:444361092207433:9"
surrogate_2 = "http://localhost:8181/restconf/operational/opendaylight-inventory:nodes/node/openflow:444361092207433/node-connector/openflow:444361092207433:10"

#CICLO PRINCIPAL
flag = True
while flag: 

	#SOLICITUD DE ESTADISTICAS EN LOS SERVIDORES
	getResponse(servidor_origen,"statistics")
	tx_origen=tx
	print "\nPaquetes transmitidos Servidor Origen\n"
	print tx_origen
	getResponse(surrogate_1,"statistics")
	tx_1=tx
	print "\nPaquetes transmitidos Surrogate 1\n"
	print tx_1
	getResponse(surrogate_2,"statistics")
	tx_2=tx
	print "\nPaquetes transmitidos SUrrogate 2\n"
	print tx_2
	
	#CALCULO DEL PORCENTAJE
	p_origen = porcentaje(5,tx_origen)
	p_1 = porcentaje(5,tx_1)
	p_2 = porcentaje(5,tx_2)
	
	#EJECUCION DE BALANCEO CON CRITERIO DEL 5%
	if tx_origen > p_1:
		delete_flujos(ip_origen, port_origen)
		crear_flujos(ip_surrogate1, port_surrogate1)
		print "\nSe aumenta prioridad para trafico a Surrogate 1\n"
		time.sleep(5)
		
	if tx_1 > p_2:
		delete_flujos(ip_surrogate1, port_surrogate1)
		crear_flujos(ip_surrogate2, port_surrogate2)
		print "\nSe aumenta prioridad para trafico a Surrogate 2\n"
		time.sleep(5)
		
	if tx_2 > p_origen:
		delete_flujos(ip_surrogate2, port_surrogate2)
		crear_flujos(ip_origen, port_origen)
		print "\nSe aumenta prioridad para trafico a Servidor Origen\n"
		time.sleep(5)
		


