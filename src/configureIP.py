#!/usr/bin/python

# Librairies import
import os
import platform
import subprocess
import uuid

import src.check_user_input as checkUserInput

# Functions
def confirmation_address(address, what):
	answerConfirmation = ""
	confirmation = False

	if checkUserInput.question_and_verification("Confirmez-vous l'adresse " + address + " pour " + what + "\n[y]: Oui\n[n]: Non\nReponse: ") == "y":
		print("L'adresse " + address + " pour " + what + " a ete confirmee avec succes!")
		confirmation = True
	else:
		print("L'adresse n'a pas ete confirmee. Veuillez la changer!")

	return confirmation

def check_input(type, what):
	while True:
		try:
			userInput = input("Encodez l'adresse" + type + " pour " + what + ": ")
			arrayInput = userInput.split(".")
		except:
			print("Une erreur s'est produite!")
			arrayInput = []

		if len(arrayInput) == 4:
			for part in arrayInput:
				if len(part) > 3 or part == "" :
					print("L'adresse n'est pas conforme! Vide ou plus de 3 caracteres")
					correctInput = False
					break
				else:
					try:
						int(part)
						correctInput = True
					except:
						print("L'adresse n'est pas conforme! Pas un Int")
						correctInput = False
						break
		else:
			print("L'adresse n'est pas conforme!")
			correctInput = False

		if correctInput:
			confirmation = confirmation_address(userInput, what)

			if confirmation:
				return arrayInput

def confirme_dhcp_address(dhcpAddress, place, goodAddress, confirmation):
	if goodAddress:
		temp = ".".join(dhcpAddress)
		confirmation = confirmation_address(temp, "la " + place + " adresse du DHCP ")

	if goodAddress == False or confirmation == False:
		print("Veuillez encoder manuellement la " + place + " adresse du range DHCP!")
		dhcpAddress = check_input("", place + " client du range DHCP")

	return dhcpAddress

def check_first_dhcp(routerAddress):
	dhcpAddress = []

	for part in routerAddress:
		dhcpAddress.append(part)

	goodAddress = True
	confirmation = False

	if int(dhcpAddress[3]) < 255:
		dhcpAddress[3] = str(int(dhcpAddress[3]) + 1)
	elif int(dhcpAddress[2]) < 255:
		dhcpAddress[3] = str(0)
		dhcpAddress[2] = str(int(firstDhcpAddress[2]) + 1)
	elif int(dhcpAddress[1]) < 255:
		dhcpAddress[3] = str(0)
		dhcpAddress[2] = str(0)
		dhcpAddress[1] = str(int(dhcpAddress[1]) + 1)
	elif int(dhcpAddress[0]) < 255:
		dhcpAddress[3] = str(0)
		dhcpAddress[2] = str(0)
		dhcpAddress[1] = str(0)
		dhcpAddress[0] = str(int(dhcpAddress[0]) + 1)
	else:
		print("L'adresse ne peut pas etre calculee")
		goodAddress = False

	return confirme_dhcp_address(dhcpAddress, "permiere", goodAddress, confirmation)

def check_last_dhcp(routerAddress, mask):
	dhcpAddress = ["0","0","0","0"]
	goodAddress = True
	confirmation = False

	for i in range(3, -1, -1):
		if int(mask[i]) == 255:
			result = int(routerAddress[i])
		elif i != 3:
			result = int(routerAddress[i]) + 255 - int(mask[i])
		else:
			result = int(routerAddress[i]) + 255 - int(mask[i]) - 2

		if result > 255 and i != 0:
			dhcpAddress[i-1] = str(dhcpAddress[i-1] + 1)
			dhcpAddress[i] = str(result-256)
		elif result <= 255:
			dhcpAddress[i] = str(result)
		else:
			print("L'adresse ne peut pas etre calculee!")
			goodAddress = False
			break

	return confirme_dhcp_address(dhcpAddress, "derniere", goodAddress, confirmation)

def configure_dhcp(routerAddress, mask):
	try:
		subprocess.run(["sudo update-rc.d dnsmasq enable"])
		subprocess.run(["sudo update-rc.d dnsmasq start"])
	except:
		print("L'activation du service DHCP a echoue")

	firstDhcpAddress = check_first_dhcp(routerAddress)
	lastDhcpAddress = check_last_dhcp(routerAddress, mask)

	# Prepare DHCP file
	line = "dhcp-range=" + '.'.join(firstDhcpAddress) + "," + '.'.join(lastDhcpAddress) + "," + '.'.join(mask) + ",12h"
	try:
		with open("~/tmp_config/51-dhcp-range.conf", "w") as file:
			file.write(line)
	except:
		print("Impossible d'enregistrer le fichier de configuration!")

def search_network_informations(routerAddress, mask, searchPath, filename):
	try:
		for root, dir, files in os.walk(searchPath):
			if filename in files:
				with open(os.path.join(root, filename), "r") as file:
					previousLine = ""
					toKeep = []
					for line in file:
						if "hwaddress ether" in line or ("iface eth0 inet6 static" in previousLine and "address" in line):
							toKeep.append(line)
						previousLine = line

				macAddress = (':'.join(['{:02x}'.format((uuid.getnode() >> element) & 0xff) for element in range(0,8*6,8)][::-1]))
				line = "# Wired adapter #1\nauto eth0\niface eth0 inet static\n"
				line += "\taddress " + '.'.join(routerAddress) + "\n"
				line += "\tnetmask " + '.'.join(mask) + "\n"
				line += "\thwaddress ether " + macAddress + "\n"
				line += "\tiface eth0 inet6 static\n"
				try:
					line += toKeep[1]
				except:
					line += "\taddress FDC8:1001:95B4:828A:213:5005:00D2:C302\n"
				line += "\tnetmask 64\n\n"
				line += "# Local loopback\n"
				line += "auto lo\n"
				line += "\tiface lo inet loopback"

				with open("~/tmp_config/interfaces_static", "w") as file:
					file.write(line)
				break
	except:
		print("Un probleme est survenu lors de la configuration des parametres du reseau")

def configure_ipv6():
	if checkUserInput.question_and_verification("Voulez-vous utiliser le prefixe IPV6 par defaut d'Evesa: \"FD05:A40B:6F6::/48" ?\n[y]: Oui\n\[n]: Non\nReponse: ") == "y":
		ipv6Prefixe = "FD05:A40B:6F6::/48" 
	else:
		while True:
			answer = input("Encodez le prefixe IPV6 sous la forme xxxx:xxxx:xxxx:xxxx:xxxx:xxxx/yy: ")
				
			if confirmation_address(answer, "le prefixe IPV6"):
				ipv6Prefixe = answer
				commandLine = "sudo netmgr -i iotr network_prefix set " + answer
				break
						    
	if "Core" not in platform.platform():
		try:
			commandLine = "sudo netmgr -i iotr network_prefix set " + ipv6Prefixe
			subprocess.run([commandLine])
		except:
			print("Le prefixe IPV6 n'a pas pu etre encode!")
	else:
		print("L'option pour Ubuntu Core n'a pas encore ete inseree!")
		
# Main function
def main():
	routerAddress = check_input(" ip", "le routeur")
	mask = check_input("", "le masque reseau")
	
	if checkUserInput.question_and_verification("Voulez-vous utiliser les adresses IPV6?\n[y]: Oui\n[n]: Non\nReponse: ") == "y":
		configure_ipv6()

	if checkUserInput.question_and_verification("Voulez-vous utiliser le service DHCP du routeur?\n[y]: Oui\n[n]: Non\nReponse: ") == "y":
		configure_dhcp(routerAddress, mask)
	else:
		subprocess.run(["sudo update-rc.d dnsmasq stop"])
		subprocess.run(["sudo update-rc.d dnsmasq disable"])

	search_network_informations(routerAddress, mask, "/var/snap/ssnmode", "interfaces_static")
