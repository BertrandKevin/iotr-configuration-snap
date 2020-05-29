#!/usr/bin/python

# Librairies import
import os
import platform
import subprocess
import socket
import sys

import src.check_user_input as checkUserInput
import src.configureIP as confIP
import src.configureNic as confNIC
import src.configureVPN as confVPN

# Functions
def configure_or_reset():
	answer = ""

	while answer != "1" and answer != "2":
		answer = input("Voulez-vous: \n" +
			"[1]: Effectuer une configuration particuliere\n" +
			"[2]: Effectuer un reset des parametres\n" +
			"Reponse: ")

	return answer

def configuration_program():
	# Check if the user want to configure the ip address of the router
	if checkUserInput.question_and_verification("Voulez-vous configurer l'adresse IP?\n[y]: Oui\n[n]: Non\nReponse: ") == "y":
		confIP.main()

	# Check if the user want to configure the NIC and if yes, if he want an auto configuration for the city of Paris or if he want a manual configuration
	if checkUserInput.question_and_verification("Voulez-vous configurer le NIC ?\n[y]: Oui\n[n]: Non\nReponse: ") =="y":
		if checkUserInput.question_and_verification("Voulez-vous realiser une configuration manuelle ?\n[y]: Oui\n[n]: Non, on configure automatiquement pour la ville de Paris\nReponse: ") == "y":
			confNIC.get_nic_settings()
		else:
			confNIC.set_nic_settings("fd05:a40b:b47d:7340::4", "1250")

	# Check if the user want to configure a VPN
	if checkUserInput.question_and_verification("Voulez-vous configurer le VPN ?\n[y]: Oui\n[n]: Non\nReponse: ") == "y":
		confVPN.install_snap_vpn()
		confVPN.configure_snap()
		
# Main program
def main():
	configurationOption = configure_or_reset()

	# 1 = Configuration by the user
	# 2 = Reset of the router
	if configurationOption == "1":
		configuration_program()
	elif configurationOption == "2":
		# Reset IP Addresses settings
		netmask = "255.255.255.0"
		routerAddress = "192.168.16.1"
		confIP.search_network_informations(routerAddress, netmask, "/var/snap/ssnmode", "interfaces_static")

		# Reset NIC settings
		aftr = "fd1e:d0d6:d81d:e070::76"
		countryCode = ""
    confNIC.set_nic_settings(aftr, countryCode)

main()
