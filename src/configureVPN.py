#!/usr/bin/python

import os
import platform

def install_snap_vpn():
	try:
		if "Core" not in platform.platform():
			os.system("sudo snap install ~/Configuration-Folder/easy-openvpn_8.snap --dangerous --devmode")
		else:
			os.system("sudo snap install ~/Configuration-Folder/easy-openvpn_2_3_10_5_armhf.snap --dangerous --devmode")
	except:
		print("Impossible d'installer le snap \"easy-openvpn\"!")

def configure_snap():
	while True:
		answer = input("Encodez le nom exacte du client VPN (ex: client1.ovpn) ou exit pour annuler: ")

		if answer == "exit":
			break
		else:
			filePath = ""
			for root, dir, files in os.walk("/"):
				if answer in files:
					filePath = os.path.joint(root, filename)
					break

			if filePath != "":
				write_openvpn_service(filepath)
			else:
				print("Aucun service VPN nome \"" + answer + "\" n'a ete trouve")


def write_openvpn_service(filepath):
	toWrite = "[Unit]\n"
	toWrite += "Description=Starts snap easy-openvpn as daemon at start-up\n"
	toWrite += "Requires=network-online.target\n"
	toWrite += "After=snap.itron-edge-edge-mode.service\n\n"
	toWrite += "[Service]\n"
	toWrite += "User=root\n"
	toWrite += "Group=root\n"
	toWrite += "Type=simple\n"
	toWrite += "Restart=always\n"
	toWrite += "ExecStart=/usr/bin/snap run easy-openvpn.connect-server " + filepath +"\n"
	toWrite += "TimeoutStopSec=180\n\n"
	toWrite += "[Install]\n"
	toWrite += "WantedBy=multi-user.target"

	with open("/etc/systemd/system/openvpn.service", "w") as file:
		file.write(toWrite)

	try:
		os.system("sudo chmod 644 /etc/systemd/system/openvpn.service")
		os.system("sudo systemctl enable openvpn")
	except:
		print("Impossible d'installer le service de demarrage!")
