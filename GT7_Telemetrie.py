
import sys
import time
import signal
import socket
import struct
import datetime
import math
#import numpy as np
from datetime import datetime as dt
from datetime import timedelta as td
from salsa20 import Salsa20_xor


from PyQt5.uic import loadUi
from PyQt5 import QtWidgets, QtCore, QtGui, Qt
from PyQt5.QtCore import pyqtSlot, QThreadPool
from PyQt5.QtWidgets import QDialog, QApplication, QStackedWidget, QPushButton, QLineEdit, QMenuBar, QAction, qApp
from PyQt5.QtGui import QColor, QIcon
from pyqtgraph import PlotWidget, plot
import pyqtgraph as pg

#----------------------------------------------------------------------
global Verbindung
Verbindung = 0
global Schluss
Schluss = 0
global Continue
Continue = 0
#global Best_Graph_Choice
#Best_Graph_Choice = 0
prevlap = -1
prevBenz = 100
pktid = 0
pknt = 0

# ansi prefix
pref = "\033["

# ports for send and receive data
SendPort = 33739
ReceivePort = 33740

# ctrl-c handler
def handler(signum, frame):
	sys.stdout.write(f'{pref}?1049l')	# revert buffer
	sys.stdout.write(f'{pref}?25h')		# restore cursor
	sys.stdout.flush()
	exit(1)

# handle ctrl-c
signal.signal(signal.SIGINT, handler)

sys.stdout.write(f'{pref}?1049h')	# alt buffer
sys.stdout.write(f'{pref}?25l')		# hide cursor
#sys.stdout.flush()



def secondsToLaptime(seconds):
	remaining = seconds
	minutes = seconds // 60
	remaining = seconds % 60
	return '{:01.0f}:{:06.3f}'.format(minutes, remaining)


# data stream decoding
def salsa20_dec(dat):
	KEY = b'Simulator Interface Packet GT7 ver 0.0'
	# Seed IV is always located here
	oiv = dat[0x40:0x44]
	iv1 = int.from_bytes(oiv, byteorder='little')
	# Notice DEADBEAF, not DEADBEEF
	iv2 = iv1 ^ 0xDEADBEAF
	IV = bytearray()
	IV.extend(iv2.to_bytes(4, 'little'))
	IV.extend(iv1.to_bytes(4, 'little'))
	ddata = Salsa20_xor(dat, bytes(IV), KEY[0:32])
	magic = int.from_bytes(ddata[0:4], byteorder='little')
	if magic != 0x47375330:
		return bytearray(b'')
	return ddata

def update_Label(pknt):
	File = open("demofile.txt","r")
	DatenIP = File.read()


				# send heartbeat
	def send_hb(s):
		send_data = 'A'
		s.sendto(send_data.encode('utf-8'), (DatenIP, SendPort))

	def stoppProg():
		global Schluss
		Schluss = 1
		#ui.StoppButton.setText("continue")
		Continue = 1
		return Schluss, Continue
				


	if Schluss == 0 and Continue == 0:
		prevlap = -1
		prevBenz = 100
		#DatenIP = self.Input_IP.text()
		
				
		#Create a UDP socket and bind it
		s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		s.bind(('0.0.0.0', ReceivePort))
		s.settimeout(10)
		send_hb(s)
		BenzWarn = 0
		BenzLap = 0
		BenzDurch = 1
		BenzDurchList = [0]
		BenzDurchList.clear()
			
		TyreWear_FL = 100
		TyreWear_FR = 100
		TyreWear_RL = 100
		TyreWear_RR = 100
			
		DurchLap = 0
		DurchLapList = [0]
		DurchLapList.clear()
			
		curlapAfterBox = 1
		prevBenzLap = 0
		prevBenzLapSave = 0
		TriggerBenz = 0
		StintZahl = 1
		BoxenFlag = 1
		rpmMeterInit = 0
		rpmRevWarn = 1
		Fuel_actual = 0
		BenzinEst = 0
		RundenPackage = 0
		GraphCount = 0
				
		store_Graph_Brake = []
		store_Graph_Throttle = []
		store_Graph_Gesamt_Brake = []
		store_Graph_Gesamt_Throttle = []
		BesteBrake = []
		BesteThrottle = []
				
		ui.hour.clear()
				
		ui.hour = [0,0]
		Throttle_Graph = [0,0]
		Brake_Graph = [0,0]
		ui.actual_Brake_line.clear()
		ui.actual_Throttle_line.clear()


			#elif Schluss = 1 and Continue ==1:


#----------------------------------------   Beginn Schleife der Datenabfrage und GUI Updates   -----------------------------------------------------------

	while Schluss == 0:
			
		ui.StoppButton.clicked.connect(stoppProg)

		#Versuchen die Verbindung herzustellen
		for _ in range(2):

			try:
				data, address = s.recvfrom(4096)
				global Verbindung
				Verbindung = 1
			except TimeoutError:
						
				Verbindung = 0
				print("Retrying after TimeoutError" + str(Verbindung))
						

				#data, address = s.recvfrom(4096)
		try:
			ddata = salsa20_dec(data)
		except UnboundLocalError:
			print("IP ist nicht korrekt")
			break
				
		pknt = pknt + 1
		RundenPackage = RundenPackage + 0.01
			
		# Laptimes
		curlap = struct.unpack('h', ddata[0x74:0x74+2])[0]                                                  # aktuelle Runde
		bstlap = format(secondsToLaptime(struct.unpack('i', ddata[0x78:0x78+4])[0] / 1000))                #format beste Runde
		lstlap = format(secondsToLaptime(struct.unpack('i', ddata[0x7C:0x7C+4])[0] / 1000))                #format letzte Runde
		#print(int(float(format(struct.unpack('f', ddata[0x54:0x54+4])[0]))))
		if int(float(format(struct.unpack('f', ddata[0x54:0x54+4])[0]))) == 0:
			BoxenFlag = 2
		if curlap > 0:
			dt_now = dt.now()
			
			if curlap != prevlap:#          Reset der Rundenzeit bei Überquerung von Start/Ziel
				prevlap = curlap
				dt_start = dt_now
				RundenPackage = 0
				GraphCount = 0
						
						
				store_Graph_Gesamt_Brake.append(store_Graph_Brake)
				store_Graph_Gesamt_Throttle.append(store_Graph_Throttle)


				store_Graph_Brake = []
				store_Graph_Throttle = []


				ui.hour.clear()
				Throttle_Graph.clear()
				Brake_Graph.clear()
						
				ui.hour = list(0 for i in range(100))
				Throttle_Graph = list(0 for i in range(100))
				Brake_Graph = list(0 for i in range(100))
						
				ui.actual_Brake_line.clear()
				ui.actual_Throttle_line.clear()
				ui.Best_Brake_line.clear()
				ui.Best_Throttle_line.clear()
						
				if curlap > 1:                        
						
					BenzLap = 100 - struct.unpack('f', ddata[0x44:0x44+4])[0] - prevBenzLap          # Verbrauch letzte Runde    15   12   13     -23,5
							
								#print("Stopp Jetzt")
								
					if BoxenFlag == 2:
						print("Boxenstop")
						BoxenFlag = 1
						curlapAfterBox = curlap-1
						StintZahl = StintZahl + 1
						pass
							
					elif BoxenFlag == 1 :
						print("Outlap vorbei")
						BoxenFlag = 0
						prevBenzLap = BenzLap + prevBenzLapSave
						pass
								
							
					else:
						prevBenzLap = BenzLap + prevBenzLap
						prevBenzLapSave = prevBenzLap
						BenzDurchList.append(BenzLap)
						BenzDurch = math.fsum(BenzDurchList)/len(BenzDurchList)
							
						DurchLapList.append(struct.unpack('i', ddata[0x7C:0x7C+4])[0] / 1000)
						if StintZahl > 2:
							DurchLap = format(secondsToLaptime(math.fsum(DurchLapList)/(len(DurchLapList)-StintZahl)))
									
						DurchLap = format(secondsToLaptime(math.fsum(DurchLapList)/len(DurchLapList)))
				TableRunde = QtWidgets.QTableWidgetItem(str(curlap-1))
				TableTime = QtWidgets.QTableWidgetItem(str(lstlap))
				TableFuel = QtWidgets.QTableWidgetItem(str("{:.1f}".format(BenzLap)))
				ui.tableLaps.setRowCount(curlap-1)
				ui.tableLaps.setItem(curlap-2,0,TableRunde)
				ui.tableLaps.setItem(curlap-2,1,TableTime)
				ui.tableLaps.setItem(curlap-2,2,TableFuel)
			curLapTime = dt_now - dt_start
			curLapTime = '{:>9}'.format(secondsToLaptime(curLapTime.total_seconds()))
			
		else:
			curLapTime = 0
			
			
				#Auto - Werte und Throttle + Brake
		cgear = struct.unpack('B', ddata[0x90:0x90+1])[0] & 0b00001111
		if cgear < 1:
			cgear = 'R'
					
		Speed = "{:.0f}".format(3.6 * struct.unpack('f', ddata[0x4C:0x4C+4])[0]) 				# speed kph
		SpeedInt = 3.6 * struct.unpack('f', ddata[0x4C:0x4C+4])[0]
		rpm = "{:.0f}".format(struct.unpack('f', ddata[0x3C:0x3C+4])[0])     					# rpm
		Throttle = "{:.0f}".format(struct.unpack('B', ddata[0x91:0x91+1])[0] / 2.55)             # throttle
		Brake = "{:.0f}".format(struct.unpack('B', ddata[0x92:0x92+1])[0] / 2.55)				# brake
		rpmRevWarn = struct.unpack('H', ddata[0x88:0x88+2])[0]  				# rpm rev warning
				
				#Others (Anzahl Runden etc.)
		GesamtRunden = format(struct.unpack('h', ddata[0x76:0x76+2])[0])
		if GesamtRunden == "0":
			GesamtRunden = "∞"
		curPos = struct.unpack('h', ddata[0x84:0x84+2])[0]						# current position
		TotPos = struct.unpack('h', ddata[0x86:0x86+2])[0]						# total positions
		TagZeit = format(str(td(seconds=round(struct.unpack('i', ddata[0x80:0x80+4])[0] / 1000))))# time of day on track
				
				# Fuel Consumption
		fuelCapacity = struct.unpack('f', ddata[0x48:0x48+4])[0]
		Fuel_actual = str("{:.2f}".format(struct.unpack('f', ddata[0x44:0x44+4])[0]))
		BenzinEst = "{:.2f}".format(struct.unpack('f', ddata[0x44:0x44+4])[0] / BenzDurch)
		if BenzDurch == 1:
			BenzinEst = 0
				
				# Tyres
				
		TyreTempFL = struct.unpack('f', ddata[0x60:0x60+4])[0]					# tyre temp FL
		TyreTempFR = struct.unpack('f', ddata[0x64:0x64+4])[0]					# tyre temp FR
		TyreTempRL = struct.unpack('f', ddata[0x68:0x68+4])[0]					# tyre temp RL
		TyreTempRR = struct.unpack('f', ddata[0x6C:0x6C+4])[0]					# tyre temp RR
				
		TyreDiamFL = 2 * struct.unpack('f', ddata[0xB4:0xB4+4])[0]												# tyre diameter FL
		TyreDiamFR = 2 * struct.unpack('f', ddata[0xB8:0xB8+4])[0]												# tyre diameter FR
		TyreDiamRL = 2 * struct.unpack('f', ddata[0xBC:0xBC+4])[0]												# tyre diameter RL
		TyreDiamRR = 2 * struct.unpack('f', ddata[0xC0:0xC0+4])[0]												# tyre diameter RR
				#print(TyreDiamFL)
		TyreGeschwFL = abs(3.6 * TyreDiamFL * struct.unpack('f', ddata[0xA4:0xA4+4])[0]) / 2													# tyre speed FL
		TyreGeschwFR = abs(3.6 * TyreDiamFR * struct.unpack('f', ddata[0xA8:0xA8+4])[0]) / 2													# tyre speed FR
		TyreGeschwRL = abs(3.6 * TyreDiamRL * struct.unpack('f', ddata[0xAC:0xAC+4])[0]) / 2													# tyre speed RL
		TyreGeschwRR = abs(3.6 * TyreDiamRR * struct.unpack('f', ddata[0xB0:0xB0+4])[0]) / 2													# tyre speed RR
				
		TyreRevFL = struct.unpack('f', ddata[0xA4:0xA4+4])[0]
		TyreRevFR = struct.unpack('f', ddata[0xA8:0xA8+4])[0]
		TyreRevRL = struct.unpack('f', ddata[0xAC:0xAC+4])[0]
		TyreRevRR = struct.unpack('f', ddata[0xB0:0xB0+4])[0]
				
				
		if SpeedInt > 0:
			tyreSlipRatioFL = abs((TyreGeschwFL / SpeedInt)-1)
			tyreSlipRatioFR = abs((TyreGeschwFR / SpeedInt)-1)
			tyreSlipRatioRL = abs((TyreGeschwRL / SpeedInt)-1)
			tyreSlipRatioRR = abs((TyreGeschwRR / SpeedInt)-1)
		else:
			tyreSlipRatioFL = 0
			tyreSlipRatioFR = 0
			tyreSlipRatioRL = 0
			tyreSlipRatioRR = 0
				
		angVel_X = struct.unpack('f', ddata[0x2C:0x2C+4])[0]					# angular velocity X
		angVel_Y = struct.unpack('f', ddata[0x30:0x30+4])[0]					# angular velocity Y
		angVel_Z = struct.unpack('f', ddata[0x34:0x34+4])[0]


		ui.LCDSpeed.display(Speed)
		ui.LCDSpeed_2.display(cgear)
		ui.LCDSpeed_3.display(rpm)
				
					
		ui.BestLap.setText(str(bstlap))
		ui.LastLap.setText(str(lstlap))
		ui.curLap.setText(str(curLapTime))
		ui.averageLap.setText(str(DurchLap))
				
		ui.DurchBenzin.setText(str("{:.2f}".format(BenzDurch)))
		ui.BenzLastLap.setText(str("{:.2f}".format(BenzLap)))
		ui.BenzAktuell.setText(str(Fuel_actual))
		ui.BenzinEst.setText(str(BenzinEst))
				
		ui.Stint.setText(str(StintZahl))                              
		ui.PositionNr.setText(str(curPos) + " / " + str(TotPos))       
		ui.LapsNr.setText(str(curlap) + " / " + str(GesamtRunden))
		ui.Tageszeit.setText(str(TagZeit)) #TagZeit
				
				
		#print(format(struct.unpack('f', ddata[0x54:0x54+4])[0]))
		ui.BrakeBar.setValue(int(float(Brake)))
		#ui.BrakeBar_Text.setText(str(Brake))
		ui.ThrottleBar.setValue(int(float(Throttle)))
		#ui.ThrottleBar_Text.setText(str(Throttle))
		#ui.progressBar.setValue(int(float(rpm)))
		if rpmMeterInit == 0:
		#    ui.progressBar.setMaximum(int(float(rpmRevWarn)))
			rpmMeterInit = 1
				
				
				
				#rpm und rpmRevWarn             rpmMeterInit = Maximum gesetzt
				
		if float(rpm) > rpmRevWarn:
			rpmRevWarn = float(rpm)

		Intervall_RevWarn = rpmRevWarn / 11      #8500 / 9
		Intervall_RevAct = float(rpm) / Intervall_RevWarn  # 2500 / 944
		Intervall_modulo = float(rpm) % Intervall_RevWarn  # 612        944 * 2 - 2500
		#print(Intervall_RevWarn)

		if 2 < Intervall_RevAct <= 3:
			RPM1_außen = 0.28 / Intervall_RevWarn   #0.71 bis 1
			RPM1_außen = RPM1_außen * Intervall_modulo
			RPM1_außen = RPM1_außen + 0.71
			RPM1_innen = 254 / Intervall_RevWarn
			RPM1_innen = RPM1_innen * Intervall_modulo
			#print(RPM1_außen)
			#ui.RPM7.setStyleSheet("background-color: qradialgradient(spread:pad, cx:0.494413, cy:0.506, radius:0.543, fx:0.494413, fy:0.5, stop:0 rgba(0, 255, 14, 255), stop:0.27933 rgba(232, 255, 0, 255), stop:0.614525 rgba(71, 255, 0, 255), stop:0.709497 rgba(255, 235, 0, 255), stop:1 rgba(255, 0, 0, 0));")
			ui.RPM2.setStyleSheet("background-color: qradialgradient(spread:pad, cx:0.494413, cy:0.506, radius:0.543, fx:0.494413, fy:0.5, stop:0 rgba(0, 57, 255, 255), stop:0.27933 rgba(0, 255, 239, 0), stop:0.614525 rgba(0, 100, 255, 0), stop:0.709497 rgba(0, 255, 228, 0), stop:0.71 rgba(255, 0, 0, 0));\n")
			ui.RPM1.setStyleSheet("background-color: qradialgradient(spread:pad, cx:0.494413, cy:0.506, radius:0.543, fx:0.494413, fy:0.5, stop:0 rgba(0, 57, 255, 255), stop:0.27933 rgba(0, 255, 239, " + str(RPM1_innen) + "), stop:0.614525 rgba(0, 100, 255, " + str(RPM1_innen) + "), stop:0.709497 rgba(0, 255, 228, " + str(RPM1_innen) + "), stop:" + str(RPM1_außen) + " rgba(255, 0, 0, 0));\n")
		if 3 < Intervall_RevAct <= 4:
			RPM2_außen = 0.28 / Intervall_RevWarn   #0.71 bis 1
			RPM2_außen = RPM2_außen * Intervall_modulo
			RPM2_außen = RPM2_außen + 0.71
			RPM2_innen = 254 / Intervall_RevWarn
			RPM2_innen = RPM2_innen * Intervall_modulo
			#print(RPM2_außen)
			ui.RPM1.setStyleSheet("background-color: qradialgradient(spread:pad, cx:0.494413, cy:0.506, radius:0.543, fx:0.494413, fy:0.5, stop:0 rgba(0, 57, 255, 255), stop:0.27933 rgba(0, 255, 239, 255), stop:0.614525 rgba(0, 100, 255, 255), stop:0.709497 rgba(0, 255, 228, 255), stop:1 rgba(255, 0, 0, 0));\n")
			ui.RPM3.setStyleSheet("background-color: qradialgradient(spread:pad, cx:0.494413, cy:0.506, radius:0.543, fx:0.494413, fy:0.5, stop:0 rgba(0, 57, 255, 255), stop:0.27933 rgba(0, 255, 239, 0), stop:0.614525 rgba(0, 100, 255, 0), stop:0.709497 rgba(0, 255, 228, 0), stop:0.71 rgba(255, 0, 0, 0));\n")
			ui.RPM2.setStyleSheet("background-color: qradialgradient(spread:pad, cx:0.494413, cy:0.506, radius:0.543, fx:0.494413, fy:0.5, stop:0 rgba(0, 57, 255, 255), stop:0.27933 rgba(0, 255, 239, " + str(RPM2_innen) + "), stop:0.614525 rgba(0, 100, 255, " + str(RPM2_innen) + "), stop:0.709497 rgba(0, 255, 228, " + str(RPM2_innen) + "), stop:" + str(RPM2_außen) + " rgba(255, 0, 0, 0));\n"
"")
		if 4 < Intervall_RevAct <= 5:
			RPM3_außen = 0.28 / Intervall_RevWarn   #0.71 bis 1
			RPM3_außen = RPM3_außen * Intervall_modulo
			RPM3_außen = RPM3_außen + 0.71
			RPM3_innen = 254 / Intervall_RevWarn
			RPM3_innen = RPM3_innen * Intervall_modulo
			#print(RPM3_außen)
			ui.RPM2.setStyleSheet("background-color: qradialgradient(spread:pad, cx:0.494413, cy:0.506, radius:0.543, fx:0.494413, fy:0.5, stop:0 rgba(0, 57, 255, 255), stop:0.27933 rgba(0, 255, 239, 255), stop:0.614525 rgba(0, 100, 255, 255), stop:0.709497 rgba(0, 255, 228, 255), stop:1 rgba(255, 0, 0, 0));\n")
			ui.RPM4.setStyleSheet("background-color: qradialgradient(spread:pad, cx:0.494413, cy:0.506, radius:0.543, fx:0.494413, fy:0.5, stop:0 rgba(0, 255, 14, 255), stop:0.27933 rgba(232, 255, 0, 0), stop:0.614525 rgba(71, 255, 0, 0), stop:0.709497 rgba(255, 235, 0, 0), stop: 0.71 rgba(255, 0, 0, 0));")
			ui.RPM3.setStyleSheet("background-color: qradialgradient(spread:pad, cx:0.494413, cy:0.506, radius:0.543, fx:0.494413, fy:0.5, stop:0 rgba(0, 57, 255, 255), stop:0.27933 rgba(0, 255, 239, " + str(RPM3_innen) + "), stop:0.614525 rgba(0, 100, 255, " + str(RPM3_innen) + "), stop:0.709497 rgba(0, 255, 228, " + str(RPM3_innen) + "), stop:" + str(RPM3_außen) + " rgba(255, 0, 0, 0));\n"
"")
		if 5 < Intervall_RevAct <= 6:
			RPM4_außen = 0.28 / Intervall_RevWarn   #0.71 bis 1
			RPM4_außen = RPM4_außen * Intervall_modulo
			RPM4_außen = RPM4_außen + 0.71
			RPM4_innen = 254 / Intervall_RevWarn
			RPM4_innen = RPM4_innen * Intervall_modulo
			ui.RPM3.setStyleSheet("background-color: qradialgradient(spread:pad, cx:0.494413, cy:0.506, radius:0.543, fx:0.494413, fy:0.5, stop:0 rgba(0, 57, 255, 255), stop:0.27933 rgba(0, 255, 239, 255), stop:0.614525 rgba(0, 100, 255, 255), stop:0.709497 rgba(0, 255, 228, 255), stop:1 rgba(255, 0, 0, 0));\n")
			ui.RPM5.setStyleSheet("background-color: qradialgradient(spread:pad, cx:0.494413, cy:0.506, radius:0.543, fx:0.494413, fy:0.5, stop:0 rgba(0, 255, 14, 255), stop:0.27933 rgba(232, 255, 0, 0), stop:0.614525 rgba(71, 255, 0, 0), stop:0.709497 rgba(255, 235, 0, 0), stop: 0.71 rgba(255, 0, 0, 0));")
			ui.RPM4.setStyleSheet("background-color: qradialgradient(spread:pad, cx:0.494413, cy:0.506, radius:0.543, fx:0.494413, fy:0.5, stop:0 rgba(0, 255, 14, 255), stop:0.27933 rgba(232, 255, 0, " + str(RPM4_innen) + "), stop:0.614525 rgba(71, 255, 0, " + str(RPM4_innen) + "), stop:0.709497 rgba(255, 235, 0, " + str(RPM4_innen) + "), stop:" + str(RPM4_außen) + " rgba(255, 0, 0, 0));")

		if 6 < Intervall_RevAct <= 7:
			RPM5_außen = 0.28 / Intervall_RevWarn   #0.71 bis 1
			RPM5_außen = RPM5_außen * Intervall_modulo
			RPM5_außen = RPM5_außen + 0.71
			RPM5_innen = 254 / Intervall_RevWarn
			RPM5_innen = RPM5_innen * Intervall_modulo
			ui.RPM4.setStyleSheet("background-color: qradialgradient(spread:pad, cx:0.494413, cy:0.506, radius:0.543, fx:0.494413, fy:0.5, stop:0 rgba(0, 255, 14, 255), stop:0.27933 rgba(232, 255, 0, 255), stop:0.614525 rgba(71, 255, 0, 255), stop:0.709497 rgba(255, 235, 0, 255), stop:1 rgba(255, 0, 0, 0));")
			ui.RPM6.setStyleSheet("background-color: qradialgradient(spread:pad, cx:0.494413, cy:0.506, radius:0.543, fx:0.494413, fy:0.5, stop:0 rgba(0, 255, 14, 255), stop:0.27933 rgba(232, 255, 0, 0), stop:0.614525 rgba(71, 255, 0, 0), stop:0.709497 rgba(255, 235, 0, 0), stop: 0.71 rgba(255, 0, 0, 0));")
			ui.RPM5.setStyleSheet("background-color: qradialgradient(spread:pad, cx:0.494413, cy:0.506, radius:0.543, fx:0.494413, fy:0.5, stop:0 rgba(0, 255, 14, 255), stop:0.27933 rgba(232, 255, 0, " + str(RPM5_innen) + "), stop:0.614525 rgba(71, 255, 0, " + str(RPM5_innen) + "), stop:0.709497 rgba(255, 235, 0, " + str(RPM5_innen) + "), stop:" + str(RPM5_außen) + " rgba(255, 0, 0, 0));")

		if 7 < Intervall_RevAct <= 8:
			RPM6_außen = 0.28 / Intervall_RevWarn   #0.71 bis 1
			RPM6_außen = RPM6_außen * Intervall_modulo
			RPM6_außen = RPM6_außen + 0.71
			RPM6_innen = 254 / Intervall_RevWarn
			RPM6_innen = RPM6_innen * Intervall_modulo
			ui.RPM5.setStyleSheet("background-color: qradialgradient(spread:pad, cx:0.494413, cy:0.506, radius:0.543, fx:0.494413, fy:0.5, stop:0 rgba(0, 255, 14, 255), stop:0.27933 rgba(232, 255, 0, 255), stop:0.614525 rgba(71, 255, 0, 255), stop:0.709497 rgba(255, 235, 0, 255), stop:1 rgba(255, 0, 0, 0));")
			ui.RPM7.setStyleSheet("background-color: qradialgradient(spread:pad, cx:0.494413, cy:0.506, radius:0.543, fx:0.494413, fy:0.5, stop:0 rgba(0, 255, 14, 255), stop:0.27933 rgba(232, 255, 0, 0), stop:0.614525 rgba(71, 255, 0, 0), stop:0.709497 rgba(255, 235, 0, 0), stop: 0.71 rgba(255, 0, 0, 0));")
			ui.RPM6.setStyleSheet("background-color: qradialgradient(spread:pad, cx:0.494413, cy:0.506, radius:0.543, fx:0.494413, fy:0.5, stop:0 rgba(0, 255, 14, 255), stop:0.27933 rgba(232, 255, 0, " + str(RPM6_innen) + "), stop:0.614525 rgba(71, 255, 0, " + str(RPM6_innen) + "), stop:0.709497 rgba(255, 235, 0, " + str(RPM6_innen) + "), stop:" + str(RPM6_außen) + " rgba(255, 0, 0, 0));")

		if 8 < Intervall_RevAct <= 9:
			RPM7_außen = 0.28 / Intervall_RevWarn   #0.71 bis 1
			RPM7_außen = RPM7_außen * Intervall_modulo
			RPM7_außen = RPM7_außen + 0.71
			RPM7_innen = 254 / Intervall_RevWarn
			RPM7_innen = RPM7_innen * Intervall_modulo
			ui.RPM6.setStyleSheet("background-color: qradialgradient(spread:pad, cx:0.494413, cy:0.506, radius:0.543, fx:0.494413, fy:0.5, stop:0 rgba(0, 255, 14, 255), stop:0.27933 rgba(232, 255, 0, 255), stop:0.614525 rgba(71, 255, 0, 255), stop:0.709497 rgba(255, 235, 0, 255), stop:1 rgba(255, 0, 0, 0));")
			ui.RPM8.setStyleSheet("background-color: qradialgradient(spread:pad, cx:0.494413, cy:0.506, radius:0.543, fx:0.494413, fy:0.5, stop:0 rgba(255, 0, 0, 255), stop:0.27933 rgba(255, 255, 0, 0), stop:0.614525 rgba(255, 0, 0, 0), stop:0.709497 rgba(255, 64, 0, 0), stop: 0.71 rgba(255, 0, 0, 0));")
			ui.RPM7.setStyleSheet("background-color: qradialgradient(spread:pad, cx:0.494413, cy:0.506, radius:0.543, fx:0.494413, fy:0.5, stop:0 rgba(0, 255, 14, 255), stop:0.27933 rgba(232, 255, 0, " + str(RPM7_innen) + "), stop:0.614525 rgba(71, 255, 0, " + str(RPM7_innen) + "), stop:0.709497 rgba(255, 235, 0, " + str(RPM7_innen) + "), stop:" + str(RPM7_außen) + " rgba(255, 0, 0, 0));")

		if 9 < Intervall_RevAct <= 10:
			RPM8_außen = 0.28 / Intervall_RevWarn   #0.71 bis 1
			RPM8_außen = RPM8_außen * Intervall_modulo
			RPM8_außen = RPM8_außen + 0.71
			RPM8_innen = 254 / Intervall_RevWarn
			RPM8_innen = RPM8_innen * Intervall_modulo
			ui.RPM7.setStyleSheet("background-color: qradialgradient(spread:pad, cx:0.494413, cy:0.506, radius:0.543, fx:0.494413, fy:0.5, stop:0 rgba(0, 255, 14, 255), stop:0.27933 rgba(232, 255, 0, 255), stop:0.614525 rgba(71, 255, 0, 255), stop:0.709497 rgba(255, 235, 0, 255), stop:1 rgba(255, 0, 0, 0));")
			ui.RPM9.setStyleSheet("background-color: qradialgradient(spread:pad, cx:0.494413, cy:0.506, radius:0.543, fx:0.494413, fy:0.5, stop:0 rgba(255, 0, 0, 255), stop:0.27933 rgba(255, 255, 0, 0), stop:0.614525 rgba(255, 0, 0, 0), stop:0.709497 rgba(255, 64, 0, 0), stop: 0.71 rgba(255, 0, 0, 0));")
			ui.RPM8.setStyleSheet("background-color: qradialgradient(spread:pad, cx:0.494413, cy:0.506, radius:0.543, fx:0.494413, fy:0.5, stop:0 rgba(255, 0, 0, 255), stop:0.27933 rgba(255, 255, 0, " + str(RPM8_innen) + "), stop:0.614525 rgba(255, 0, 0, " + str(RPM8_innen) + "), stop:0.709497 rgba(255, 64, 0, " + str(RPM8_innen) + "), stop:" + str(RPM8_außen) + " rgba(255, 0, 0, 0));")

		if 10 < Intervall_RevAct <= 11:
			RPM9_außen = 0.28 / Intervall_RevWarn   #0.71 bis 1
			RPM9_außen = RPM9_außen * Intervall_modulo
			RPM9_außen = RPM9_außen + 0.71
			RPM9_innen = 254 / Intervall_RevWarn
			RPM9_innen = RPM9_innen * Intervall_modulo
			ui.RPM8.setStyleSheet("background-color: qradialgradient(spread:pad, cx:0.494413, cy:0.506, radius:0.543, fx:0.494413, fy:0.5, stop:0 rgba(255, 0, 0, 255), stop:0.27933 rgba(255, 255, 0, 255), stop:0.614525 rgba(255, 0, 0, 255), stop:0.709497 rgba(255, 64, 0, 255), stop: 1 rgba(255, 0, 0, 0));")
			ui.RPM9.setStyleSheet("background-color: qradialgradient(spread:pad, cx:0.494413, cy:0.506, radius:0.543, fx:0.494413, fy:0.5, stop:0 rgba(255, 0, 0, 255), stop:0.27933 rgba(255, 255, 0, " + str(RPM9_innen) + "), stop:0.614525 rgba(255, 0, 0, " + str(RPM9_innen) + "), stop:0.709497 rgba(255, 64, 0, " + str(RPM9_innen) + "), stop:" + str(RPM9_außen) + " rgba(255, 0, 0, 0));")

				#print(TyreTempFL)
		if TyreTempFL <= 60:
			Temp_FL_R = 0
			Temp_FL_G = (TyreTempFL - 30) * 8.5
			Temp_FL_B = 255
		elif TyreTempFL > 60 and TyreTempFL <= 85:
			Temp_FL_R = 0
			Temp_FL_G = 255
			Temp_FL_B = 255 - ((TyreTempFL - 60) * 10.2)
		elif TyreTempFL > 85 and TyreTempFL <= 100:
			Temp_FL_R = (TyreTempFL - 85) * 17
			Temp_FL_G = 255
			Temp_FL_B = 0
		elif TyreTempFL > 100 and TyreTempFL <= 120:
			Temp_FL_R = 255
			Temp_FL_G = 255 - ((TyreTempFL - 100) * 12.75)
			Temp_FL_B = 0
		elif TyreTempFL > 120:
			Temp_FL_R = 255
			Temp_FL_G = 0
			Temp_FL_B = 0
					
		ui.Tyre_FL_Label.setStyleSheet("border-top-left-radius:20px;\n"
"border-top-right-radius:20px;\n"
"border-bottom-left-radius:20px;\n"
"border-bottom-right-radius:20px;\n"
"background-color: qradialgradient(spread:pad, cx:0.5, cy:0.5, radius:1, fx:0.5, fy:0.5, stop:0 rgba("+str(Temp_FL_R)+", "+str(Temp_FL_G)+", "+str(Temp_FL_B)+", 255), stop:1 rgba(255, 0, 0,0));")

		if TyreTempFR <= 60:
			Temp_FR_R = 0
			Temp_FR_G = (TyreTempFR - 30) * 8.5
			Temp_FR_B = 255
		elif TyreTempFR > 60 and TyreTempFR <= 85:
			Temp_FR_R = 0
			Temp_FR_G = 255
			Temp_FR_B = 255 - ((TyreTempFR - 60) * 10.2)
		elif TyreTempFR > 85 and TyreTempFR <= 100:
			Temp_FR_R = (TyreTempFR - 85) * 17
			Temp_FR_G = 255
			Temp_FR_B = 0
		elif TyreTempFR > 100 and TyreTempFR <= 120:
			Temp_FR_R = 255
			Temp_FR_G = 255 - ((TyreTempFR - 100) * 12.75)
			Temp_FR_B = 0
		elif TyreTempFR > 120:
			Temp_FR_R = 255
			Temp_FR_G = 0
			Temp_FR_B = 0
		ui.Tyre_FR_Label.setStyleSheet("border-top-left-radius:20px;\n"
"border-top-right-radius:20px;\n"
"border-bottom-left-radius:20px;\n"
"border-bottom-right-radius:20px;\n"
"background-color: qradialgradient(spread:pad, cx:0.5, cy:0.5, radius:1, fx:0.5, fy:0.5, stop:0 rgba("+str(Temp_FR_R)+", "+str(Temp_FR_G)+", "+str(Temp_FR_B)+", 255), stop:1 rgba(255, 0, 0,0));")

		if TyreTempRL <= 60:
			Temp_RL_R = 0
			Temp_RL_G = (TyreTempRL - 30) * 8.5
			Temp_RL_B = 255
		elif TyreTempRL > 60 and TyreTempRL <= 85:
			Temp_RL_R = 0
			Temp_RL_G = 255
			Temp_RL_B = 255 - ((TyreTempRL - 60) * 10.2)
		elif TyreTempRL > 85 and TyreTempRL <= 100:
			Temp_RL_R = (TyreTempRL - 85) * 17
			Temp_RL_G = 255
			Temp_RL_B = 0
		elif TyreTempRL > 100 and TyreTempRL <= 120:
			Temp_RL_R = 255
			Temp_RL_G = 255 - ((TyreTempRL - 100) * 12.75)
			Temp_RL_B = 0
		elif TyreTempRL > 120:
			Temp_RL_R = 255
			Temp_RL_G = 0
			Temp_RL_B = 0                    
		ui.Tyre_RL_Label.setStyleSheet("border-top-left-radius:20px;\n"
"border-top-right-radius:20px;\n"
"border-bottom-left-radius:20px;\n"
"border-bottom-right-radius:20px;\n"
"background-color: qradialgradient(spread:pad, cx:0.5, cy:0.5, radius:1, fx:0.5, fy:0.5, stop:0 rgba("+str(Temp_RL_R)+", "+str(Temp_RL_G)+", "+str(Temp_RL_B)+", 255), stop:1 rgba(255, 0, 0,0));")

		if TyreTempRR <= 60:
			Temp_RR_R = 0
			Temp_RR_G = (TyreTempRR - 30) * 8.5
			Temp_RR_B = 255
		elif TyreTempRR > 60 and TyreTempRR <= 85:
			Temp_RR_R = 0
			Temp_RR_G = 255
			Temp_RR_B = 255 - ((TyreTempRR - 60) * 10.2)
		elif TyreTempRR > 85 and TyreTempRR <= 100:
			Temp_RR_R = (TyreTempRR - 85) * 17
			Temp_RR_G = 255
			Temp_RR_B = 0
		elif TyreTempRR > 100 and TyreTempRR <= 120:
			Temp_RR_R = 255
			Temp_RR_G = 255 - ((TyreTempRR - 100) * 12.75)
			Temp_RR_B = 0
		elif TyreTempRR > 120:
			Temp_RR_R = 255
			Temp_RR_G = 0
			Temp_RR_B = 0
		ui.Tyre_RR_Label.setStyleSheet("border-top-left-radius:20px;\n"
"border-top-right-radius:20px;\n"
"border-bottom-left-radius:20px;\n"
"border-bottom-right-radius:20px;\n"
"background-color: qradialgradient(spread:pad, cx:0.5, cy:0.5, radius:1, fx:0.5, fy:0.5, stop:0 rgba("+str(Temp_RR_R)+", "+str(Temp_RR_G)+", "+str(Temp_RR_B)+", 255), stop:1 rgba(255, 0, 0,0));")



		store_Graph_Brake.append(int(Brake)) #Brake Daten speichern in Liste    --------   erste Position ist immer curlap
		store_Graph_Throttle.append(int(Throttle)) #Throttle Daten speichern in Liste    --------   erste Position ist immer curlap
				
				

		Throttle_Graph = Throttle_Graph[1:]  # Remove the first y element.
		Throttle_Graph.append(int(Throttle))  # Add a new value 1 higher than the last.
		ui.hour = ui.hour[1:]  # Remove the first
		ui.hour.append( ui.hour[-1] + 0.0333333333)  # Add a new random value.
		ui.actual_Throttle_line.setData(ui.hour, Throttle_Graph)  # Update the data.

		Brake_Graph = Brake_Graph[1:]  # Remove the first y element.
		Brake_Graph.append(int(Brake))  # Add a new value 1 higher than the last.
		ui.actual_Brake_line.setData(ui.hour, Brake_Graph)  # Update the data.



		if "Best_Graph_Choice" in globals():
			global Best_Graph_Choice
			ui.BestBrake_Graph = list(store_Graph_Gesamt_Brake[Best_Graph_Choice])
			ui.BestThrottle_Graph = list(store_Graph_Gesamt_Throttle[Best_Graph_Choice])
					
										
			if len(BesteBrake) < 100:
				for i in range(100):
					BesteBrake.append(ui.BestBrake_Graph[i])
					BesteThrottle.append(ui.BestThrottle_Graph[i])
					GraphCount = 100
						

			else:
				GraphCount = GraphCount + 1
				BesteThrottle.pop(0)   #erstes element entfernen
				BesteBrake.pop(0)   #erstes element entfernen

				if GraphCount < len(ui.BestThrottle_Graph):
					BesteBrake.append(ui.BestBrake_Graph[GraphCount])  # neues element anhängen mit GraphCount
					BesteThrottle.append(ui.BestThrottle_Graph[GraphCount])  # neues element anhängen mit GraphCount
				else:
						
					BesteThrottle.append(0)
					BesteBrake.append(0)
							



			ui.Best_Brake_line.setData(ui.hour, BesteBrake)         #Update Data
			ui.Best_Throttle_line.setData(ui.hour, BesteThrottle)  # Update the data.





		QtGui.QGuiApplication.processEvents()
		if pknt > 100:
			pknt = 1
			send_hb(s)



# ----------------------------      Fenster einrichten      ------------------------------



class Ui_MainWindow(object):
	def setupUi(self, MainWindow):

		
		def Zelle_click():
			global Best_Graph_Choice
			Best_Graph_Choice = self.tableLaps.currentRow()+1
			
			
			return Best_Graph_Choice

		def Reset_Label():
			self.tableLaps.clearContents()
			self.tableLaps.setRowCount(0)
			global Schluss
			Schluss = 0
			print(Verbindung)
			update_Label(pknt)

		MainWindow.setObjectName("MainWindow")
		MainWindow.resize(1000, 600)

		self.centralwidget = QtWidgets.QWidget(MainWindow)
		self.centralwidget.setEnabled(True)
		self.centralwidget.setObjectName("centralwidget")

		
		self.verticalLayout = QtWidgets.QVBoxLayout(self.centralwidget)
		self.verticalLayout.setContentsMargins(1, 1, 1, 1)
		self.verticalLayout.setSpacing(0)
		self.verticalLayout.setObjectName("verticalLayout")

		self.widget = QtWidgets.QWidget(MainWindow)
		self.widget.setGeometry(QtCore.QRect(0, 0, 998, 598))
		sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Expanding)
		sizePolicy.setHorizontalStretch(0)
		sizePolicy.setVerticalStretch(0)
		sizePolicy.setHeightForWidth(self.widget.sizePolicy().hasHeightForWidth())
		self.widget.setSizePolicy(sizePolicy)
		self.widget.setAutoFillBackground(False)
		self.widget.setStyleSheet("background-color: qlineargradient(spread:pad, x1:0.095, y1:0.108227, x2:0.100324, y2:0.614, stop:0 rgba(27, 38, 216, 255), stop:1 rgba(0, 0, 0, 255));")
		self.widget.setObjectName("widget")
		
		
		self.gridLayout_2 = QtWidgets.QGridLayout(self.widget)
		self.gridLayout_2.setContentsMargins(1, 1, 1, 1)
		self.gridLayout_2.setSpacing(10)
		self.gridLayout_2.setObjectName("gridLayout_2")
		self.gridLayout = QtWidgets.QGridLayout()
		self.gridLayout.setSizeConstraint(QtWidgets.QLayout.SizeConstraint.SetMinAndMaxSize)
		self.gridLayout.setContentsMargins(1, 1, 1, 1)
		self.gridLayout.setSpacing(10)
		self.gridLayout.setObjectName("gridLayout")
		self.Tyre_FL_Label = QtWidgets.QLabel(self.widget)
		sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.MinimumExpanding, QtWidgets.QSizePolicy.Policy.MinimumExpanding)
		sizePolicy.setHorizontalStretch(1)
		sizePolicy.setVerticalStretch(1)
		sizePolicy.setHeightForWidth(self.Tyre_FL_Label.sizePolicy().hasHeightForWidth())
		self.Tyre_FL_Label.setSizePolicy(sizePolicy)
		self.Tyre_FL_Label.setMaximumSize(QtCore.QSize(60, 90))
		font = QtGui.QFont()
		font.setPointSize(14)
		font.setBold(True)
		self.Tyre_FL_Label.setFont(font)
		self.Tyre_FL_Label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
		self.Tyre_FL_Label.setStyleSheet("border-top-left-radius:20px;\n"
"border-top-right-radius:20px;\n"
"border-bottom-left-radius:20px;\n"
"border-bottom-right-radius:20px;\n"
"background-color: qradialgradient(spread:pad, cx:0.5, cy:0.5, radius:1, fx:0.5, fy:0.5, stop:0 rgba(71, 255, 0, 255), stop:0.4 rgba(71, 255, 0, 210), stop:1 rgba(255, 0, 0,255));")
		self.Tyre_FL_Label.setFrameShape(QtWidgets.QFrame.Shape.Box)
		self.Tyre_FL_Label.setLineWidth(1)
		self.Tyre_FL_Label.setObjectName("Tyre_FL_Label")
		self.gridLayout.addWidget(self.Tyre_FL_Label, 3, 7, 1, 1)
		self.LCDSpeed = QtWidgets.QLCDNumber(self.widget)
		sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.MinimumExpanding, QtWidgets.QSizePolicy.Policy.MinimumExpanding)
		sizePolicy.setHorizontalStretch(1)
		sizePolicy.setVerticalStretch(1)
		sizePolicy.setHeightForWidth(self.LCDSpeed.sizePolicy().hasHeightForWidth())
		self.LCDSpeed.setSizePolicy(sizePolicy)
		self.LCDSpeed.setMaximumSize(QtCore.QSize(350, 90))
		font = QtGui.QFont()
		font.setBold(False)
		self.LCDSpeed.setFont(font)
		self.LCDSpeed.setStyleSheet("background-color: rgb(170, 170, 127);\n"
"background-color: qlineargradient(spread:pad, x1:0.838419, y1:0.289, x2:0.944682, y2:0, stop:0 rgba(170, 170, 127, 255), stop:0.234637 rgba(255, 255, 255, 175), stop:0.916201 rgba(0, 0, 0, 130));\n"
"color: rgb(0, 0, 0);")
		self.LCDSpeed.setFrameShape(QtWidgets.QFrame.Shape.WinPanel)
		self.LCDSpeed.setFrameShadow(QtWidgets.QFrame.Shadow.Plain)
		self.LCDSpeed.setLineWidth(1)
		self.LCDSpeed.setMidLineWidth(0)
		self.LCDSpeed.setSmallDecimalPoint(True)
		self.LCDSpeed.setDigitCount(3)
		self.LCDSpeed.setSegmentStyle(QtWidgets.QLCDNumber.SegmentStyle.Flat)
		self.LCDSpeed.setProperty("value", 0)
		self.LCDSpeed.setObjectName("LCDSpeed")
		self.gridLayout.addWidget(self.LCDSpeed, 4, 3, 1, 2)
		
		
		
		
		self.tableLaps = QtWidgets.QTableWidget(self.widget)
		sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Preferred)
		sizePolicy.setHorizontalStretch(3)
		sizePolicy.setVerticalStretch(1)
		sizePolicy.setHeightForWidth(self.tableLaps.sizePolicy().hasHeightForWidth())
		self.tableLaps.setSizePolicy(sizePolicy)
		self.tableLaps.setMaximumSize(QtCore.QSize(300, 8000))
		font = QtGui.QFont()
		#font.setPointSize(10)
		font.setPointSize(14)
		font.setBold(True)
		self.tableLaps.setFont(font)
		self.tableLaps.setContextMenuPolicy(QtCore.Qt.ContextMenuPolicy.NoContextMenu)
		self.tableLaps.setStyleSheet("color: rgb(255, 255, 127);background-color: qlineargradient(spread:pad, x1:0.0954525, y1:0.148, x2:0.402, y2:1, stop:0 rgba(143, 147, 216, 255), stop:1 rgba(0, 0, 0, 255));")
		self.tableLaps.setFrameShape(QtWidgets.QFrame.Shape.Box)
		self.tableLaps.setFrameShadow(QtWidgets.QFrame.Shadow.Sunken)
		self.tableLaps.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
		self.tableLaps.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
		self.tableLaps.setAlternatingRowColors(False)
		self.tableLaps.setSortingEnabled(True)
		self.tableLaps.setWordWrap(False)
		self.tableLaps.setObjectName("tableLaps")
		self.tableLaps.setRowCount(0)
		self.tableLaps.setColumnCount(3)
		self.tableLaps.verticalHeader().hide()
		Testrunde = QtWidgets.QTableWidgetItem("Das ist toll")
		self.tableLaps.setItem(2,1,Testrunde)
		self.tableLaps.setHorizontalHeaderLabels(["Lap", "Time", "Fuel"])
		self.tableLaps.horizontalHeader().setStyleSheet("::section{background-color: rgb(0, 0, 0);font-weight:bold; font-size: 14px;}")
		self.tableLaps.setColumnWidth(0, 30)
		self.tableLaps.setColumnWidth(1, 170)
		self.tableLaps.setColumnWidth(2, 42)
		#self.tableView.setHorizontalHeader("test")
		self.gridLayout.addWidget(self.tableLaps, 2, 0, 3, 1) #Matzeman
		
		

			
		Best_Graph_Choice = self.tableLaps.cellClicked.connect(Zelle_click)

		
		self.LCDSpeed_2 = QtWidgets.QLCDNumber(self.widget)
		sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.MinimumExpanding, QtWidgets.QSizePolicy.Policy.MinimumExpanding)
		sizePolicy.setHorizontalStretch(1)
		sizePolicy.setVerticalStretch(1)
		sizePolicy.setHeightForWidth(self.LCDSpeed_2.sizePolicy().hasHeightForWidth())
		self.LCDSpeed_2.setSizePolicy(sizePolicy)
		self.LCDSpeed_2.setMaximumSize(QtCore.QSize(140, 90))
		self.LCDSpeed_2.setAutoFillBackground(False)
		self.LCDSpeed_2.setStyleSheet("background-color: rgb(170, 170, 127);\n"
"color: rgb(0, 0, 0);\n"
"background-color: qlineargradient(spread:pad, x1:0.838307, y1:0.102, x2:0.838827, y2:0.017, stop:0 rgba(170, 170, 127, 255), stop:0.731844 rgba(255, 255, 255, 148), stop:0.916201 rgba(0, 0, 0, 157));")
		self.LCDSpeed_2.setFrameShape(QtWidgets.QFrame.Shape.WinPanel)
		self.LCDSpeed_2.setFrameShadow(QtWidgets.QFrame.Shadow.Plain)
		self.LCDSpeed_2.setSmallDecimalPoint(True)
		self.LCDSpeed_2.setDigitCount(1)
		self.LCDSpeed_2.setSegmentStyle(QtWidgets.QLCDNumber.SegmentStyle.Flat)
		self.LCDSpeed_2.setProperty("value", 0)
		self.LCDSpeed_2.setObjectName("LCDSpeed_2")
		self.gridLayout.addWidget(self.LCDSpeed_2, 3, 2, 1, 1)
		self.Tyre_FR_Label = QtWidgets.QLabel(self.widget)
		sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.MinimumExpanding, QtWidgets.QSizePolicy.Policy.MinimumExpanding)
		sizePolicy.setHorizontalStretch(1)
		sizePolicy.setVerticalStretch(1)
		sizePolicy.setHeightForWidth(self.Tyre_FR_Label.sizePolicy().hasHeightForWidth())
		self.Tyre_FR_Label.setSizePolicy(sizePolicy)
		self.Tyre_FR_Label.setMaximumSize(QtCore.QSize(60, 90))
		self.Tyre_FR_Label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
		font = QtGui.QFont()
		font.setPointSize(14)
		font.setBold(True)
		self.Tyre_FR_Label.setFont(font)
		self.Tyre_FR_Label.setStyleSheet("border-top-left-radius:20px;\n"
"background-color: qradialgradient(spread:pad, cx:0.5, cy:0.5, radius:1, fx:0.5, fy:0.5, stop:0 rgba(71, 255, 0, 255), stop:0.4 rgba(71, 255, 0, 210), stop:1 rgba(255, 0, 0,255));\n"
"border-top-right-radius:20px;\n"
"border-bottom-left-radius:20px;\n"
"border-bottom-right-radius:20px;")
		self.Tyre_FR_Label.setObjectName("Tyre_FR_Label")
		self.gridLayout.addWidget(self.Tyre_FR_Label, 3, 8, 1, 1)
		self.BrakeBar = QtWidgets.QProgressBar(self.widget)
		sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.MinimumExpanding, QtWidgets.QSizePolicy.Policy.MinimumExpanding)
		sizePolicy.setHorizontalStretch(1)
		sizePolicy.setVerticalStretch(1)
		sizePolicy.setHeightForWidth(self.BrakeBar.sizePolicy().hasHeightForWidth())
		self.BrakeBar.setSizePolicy(sizePolicy)
		self.BrakeBar.setMaximumSize(QtCore.QSize(70, 200))
		self.BrakeBar.setStyleSheet("background-color: rgb(255, 255, 255);\n"
"border-top-left-radius:10px;\n"
"border-top-right-radius:10px;\n"
"color: rgb(85, 255, 0);\n"
"")
		self.BrakeBar.setProperty("value", 24)
		self.BrakeBar.setTextVisible(False)
		self.BrakeBar.setOrientation(QtCore.Qt.Orientation.Vertical)
		self.BrakeBar.setObjectName("BrakeBar")
		self.gridLayout.addWidget(self.BrakeBar, 3, 1, 2, 1)
		self.LCDSpeed_3 = QtWidgets.QLCDNumber(self.widget)
		sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.MinimumExpanding, QtWidgets.QSizePolicy.Policy.MinimumExpanding)
		sizePolicy.setHorizontalStretch(1)
		sizePolicy.setVerticalStretch(1)
		sizePolicy.setHeightForWidth(self.LCDSpeed_3.sizePolicy().hasHeightForWidth())
		self.LCDSpeed_3.setSizePolicy(sizePolicy)
		self.LCDSpeed_3.setMaximumSize(QtCore.QSize(350, 90))
		self.LCDSpeed_3.setStyleSheet("color: rgb(0, 0, 0);\n"
"background-color: qlineargradient(spread:pad, x1:0.263, y1:0.153045, x2:0.062, y2:0.0563636, stop:0 rgba(170, 170, 127, 255), stop:0.653631 rgba(255, 255, 255, 175), stop:1 rgba(0, 0, 0, 130));")
		self.LCDSpeed_3.setFrameShape(QtWidgets.QFrame.Shape.WinPanel)
		self.LCDSpeed_3.setFrameShadow(QtWidgets.QFrame.Shadow.Plain)
		self.LCDSpeed_3.setSmallDecimalPoint(True)
		self.LCDSpeed_3.setDigitCount(6)
		self.LCDSpeed_3.setSegmentStyle(QtWidgets.QLCDNumber.SegmentStyle.Flat)
		self.LCDSpeed_3.setProperty("value", 0)
		self.LCDSpeed_3.setObjectName("LCDSpeed_3")
		self.gridLayout.addWidget(self.LCDSpeed_3, 3, 3, 1, 2)
		self.ThrottleBar = QtWidgets.QProgressBar(self.widget)
		self.ThrottleBar.setEnabled(True)
		sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.MinimumExpanding, QtWidgets.QSizePolicy.Policy.MinimumExpanding)
		sizePolicy.setHorizontalStretch(1)
		sizePolicy.setVerticalStretch(1)
		sizePolicy.setHeightForWidth(self.ThrottleBar.sizePolicy().hasHeightForWidth())
		self.ThrottleBar.setSizePolicy(sizePolicy)
		self.ThrottleBar.setMaximumSize(QtCore.QSize(70, 200))
		self.ThrottleBar.setStyleSheet("background-color: rgb(255, 255, 255);\n"
"border-top-left-radius:10px;\n"
"border-top-right-radius:10px;\n"
"color: rgb(85, 255, 0);\n"
"")
		self.ThrottleBar.setProperty("value", 24)
		self.ThrottleBar.setTextVisible(False)
		self.ThrottleBar.setOrientation(QtCore.Qt.Orientation.Vertical)
		self.ThrottleBar.setObjectName("ThrottleBar")
		self.gridLayout.addWidget(self.ThrottleBar, 3, 5, 2, 1)
		self.Reifensorte = QtWidgets.QSlider(self.widget)
		sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.MinimumExpanding)
		sizePolicy.setHorizontalStretch(0)
		sizePolicy.setVerticalStretch(0)
		sizePolicy.setHeightForWidth(self.Reifensorte.sizePolicy().hasHeightForWidth())
		self.Reifensorte.setSizePolicy(sizePolicy)
		self.Reifensorte.setMaximumSize(QtCore.QSize(140, 40))
		self.Reifensorte.setStyleSheet("background-color: qlineargradient(spread:pad, x1:1, y1:1, x2:0, y2:1, stop:0 rgba(255, 0, 0, 255), stop:0.335196 rgba(255, 0, 0, 255), stop:0.340782 rgba(255, 255, 0, 255), stop:0.662444 rgba(255, 255, 0, 255), stop:0.662469 rgba(0, 0, 255, 255), stop:0.675978 rgba(255, 255, 255, 255), stop:1 rgba(255, 255, 255, 255));")
		self.Reifensorte.setMinimum(1)
		self.Reifensorte.setMaximum(3)
		self.Reifensorte.setPageStep(1)
		self.Reifensorte.setSliderPosition(2)
		self.Reifensorte.setOrientation(QtCore.Qt.Orientation.Horizontal)
		self.Reifensorte.setObjectName("Reifensorte")
		self.gridLayout.addWidget(self.Reifensorte, 2, 7, 1, 2)
		self.dial = QtWidgets.QDial(self.widget)
		self.dial.setMaximumSize(QtCore.QSize(140, 90))
		self.dial.setProperty("value", 50)
		self.dial.setObjectName("dial")
		self.gridLayout.addWidget(self.dial, 4, 2, 1, 1)
		self.Tyre_RL_Label = QtWidgets.QLabel(self.widget)
		sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.MinimumExpanding, QtWidgets.QSizePolicy.Policy.MinimumExpanding)
		sizePolicy.setHorizontalStretch(1)
		sizePolicy.setVerticalStretch(1)
		sizePolicy.setHeightForWidth(self.Tyre_RL_Label.sizePolicy().hasHeightForWidth())
		self.Tyre_RL_Label.setSizePolicy(sizePolicy)
		self.Tyre_RL_Label.setMaximumSize(QtCore.QSize(60, 90))
		self.Tyre_RL_Label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
		font = QtGui.QFont()
		font.setPointSize(14)
		font.setBold(True)
		self.Tyre_RL_Label.setFont(font)
		self.Tyre_RL_Label.setStyleSheet("border-top-left-radius:20px;\n"
"background-color: qradialgradient(spread:pad, cx:0.5, cy:0.5, radius:1, fx:0.5, fy:0.5, stop:0 rgba(71, 255, 0, 255), stop:0.4 rgba(71, 255, 0, 210), stop:1 rgba(255, 0, 0,255));\n"
"border-top-right-radius:20px;\n"
"border-bottom-left-radius:20px;\n"
"border-bottom-right-radius:20px;")
		self.Tyre_RL_Label.setObjectName("Tyre_RL_Label")
		self.gridLayout.addWidget(self.Tyre_RL_Label, 4, 7, 1, 1)
		self.Tyre_RR_Label = QtWidgets.QLabel(self.widget)
		sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.MinimumExpanding, QtWidgets.QSizePolicy.Policy.MinimumExpanding)
		sizePolicy.setHorizontalStretch(1)
		sizePolicy.setVerticalStretch(1)
		sizePolicy.setHeightForWidth(self.Tyre_RR_Label.sizePolicy().hasHeightForWidth())
		self.Tyre_RR_Label.setSizePolicy(sizePolicy)
		self.Tyre_RR_Label.setMaximumSize(QtCore.QSize(60, 90))
		self.Tyre_RR_Label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
		font = QtGui.QFont()
		font.setPointSize(14)
		font.setBold(True)
		self.Tyre_RR_Label.setFont(font)
		self.Tyre_RR_Label.setStyleSheet("border-top-left-radius:20px;\n"
"background-color: qradialgradient(spread:pad, cx:0.5, cy:0.5, radius:1, fx:0.5, fy:0.5, stop:0 rgba(71, 255, 0, 255), stop:0.4 rgba(71, 255, 0, 210), stop:1 rgba(255, 0, 0,255));\n"
"border-top-right-radius:20px;\n"
"border-bottom-left-radius:20px;\n"
"border-bottom-right-radius:20px;")
		self.Tyre_RR_Label.setObjectName("Tyre_RR_Label")
		self.gridLayout.addWidget(self.Tyre_RR_Label, 4, 8, 1, 1)



		#-------------------------------------BEGINN GRAPH___________________________________________________________

		self.Map_Graph = PlotWidget()
		self.gridLayout.addWidget(self.Map_Graph, 0, 0, 2, 2)
		self.Map_Graph.setBackground('w')
		self.Map_Graph.setTitle("Map", color= QColor(0,0,0), size="12pt")
		self.Map_Graph.setYRange(0,105,padding=0)
		self.Map_Graph.setXRange(0,105,padding=0)
		#self.Map_Graph.showGrid(x=True, y=True)
		self.Map_Graph.hideAxis("bottom")
		self.Map_Graph.hideAxis("left")
		penMap = pg.mkPen(width=4, color=(0, 0, 0))
		#self.Map_line =  self.Map_Graph.plot(self.Karten_Graph, self.hour, pen=penMap)



		self.actual_Graph = PlotWidget()
		self.gridLayout.addWidget(self.actual_Graph, 0, 2, 1, 7)
		self.actual_Graph.setBackground('w')
		self.actual_Graph.setTitle("actual Lap", color= QColor(0,0,0), size="12pt")
		self.actual_Graph.setYRange(0,105,padding=0)
		self.actual_Graph.showGrid(x=True, y=True)
		penBrake = pg.mkPen(width=2.5, color=(255, 0, 0))
		penThrottle = pg.mkPen(width=2.5, color=(17, 255, 0))

		self.hour = list(0 for i in range(100))
		self.Throttle_Graph = list(0 for i in range(100))
		self.Brake_Graph = list(0 for i in range(100))
		self.actual_Throttle_line =  self.actual_Graph.plot(self.Throttle_Graph, self.hour, pen=penThrottle)
		self.actual_Brake_line =  self.actual_Graph.plot(self.Brake_Graph, self.hour, pen=penBrake)
		#------------------------------------------------------------ ENDE GRAPH----------------------------------------------------------------



		self.Best_Graph = PlotWidget()
		self.gridLayout.addWidget(self.Best_Graph, 1, 2, 1, 7)
		self.Best_Graph.setBackground('w')
		self.Best_Graph.setTitle("compare Lap", color= QColor(0,0,0), size="12pt")
		self.Best_Graph.setYRange(0,105,padding=0)
		self.Best_Graph.showGrid(x=True, y=True)


		self.BestThrottle_Graph = list(0 for i in range(100))
		self.BestBrake_Graph = list(0 for i in range(100))
		self.Best_Throttle_line =  self.Best_Graph.plot(self.BestThrottle_Graph, self.hour, pen=penThrottle)
		self.Best_Brake_line =  self.Best_Graph.plot(self.BestBrake_Graph, self.hour, pen=penBrake)



		self.widget_2 = QtWidgets.QWidget(self.widget)
		sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Expanding)
		sizePolicy.setHorizontalStretch(1)
		sizePolicy.setVerticalStretch(1)
		sizePolicy.setHeightForWidth(self.widget_2.sizePolicy().hasHeightForWidth())
		self.widget_2.setSizePolicy(sizePolicy)
		self.widget_2.setStyleSheet("background-color: qlineargradient(spread:pad, x1:0.134, y1:0, x2:0.559, y2:0, stop:0 rgba(159, 27, 216, 239), stop:0.592179 rgba(0, 0, 0, 230));\n"
"color: rgb(255, 255, 127);")
		self.widget_2.setObjectName("widget_2")
		self.formLayout = QtWidgets.QFormLayout(self.widget_2)
		self.formLayout.setObjectName("formLayout")
		self.LapsNr_Text = QtWidgets.QLabel(self.widget_2)
		sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.MinimumExpanding, QtWidgets.QSizePolicy.Policy.Expanding)
		sizePolicy.setHorizontalStretch(0)
		sizePolicy.setVerticalStretch(0)
		sizePolicy.setHeightForWidth(self.LapsNr_Text.sizePolicy().hasHeightForWidth())
		self.LapsNr_Text.setSizePolicy(sizePolicy)
		font = QtGui.QFont()
		font.setPointSize(14)
		font.setBold(False)
		self.LapsNr_Text.setFont(font)
		self.LapsNr_Text.setStyleSheet("color: rgb(255, 255, 127);\n"
"background-color: rgba(255, 255, 255, 0);")
		self.LapsNr_Text.setObjectName("LapsNr_Text")
		self.formLayout.setWidget(1, QtWidgets.QFormLayout.ItemRole.LabelRole, self.LapsNr_Text)
		self.Pos_Text = QtWidgets.QLabel(self.widget_2)
		sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.MinimumExpanding, QtWidgets.QSizePolicy.Policy.Expanding)
		sizePolicy.setHorizontalStretch(0)
		sizePolicy.setVerticalStretch(0)
		sizePolicy.setHeightForWidth(self.Pos_Text.sizePolicy().hasHeightForWidth())
		self.Pos_Text.setSizePolicy(sizePolicy)
		font = QtGui.QFont()
		font.setPointSize(14)
		font.setBold(False)
		self.Pos_Text.setFont(font)
		self.Pos_Text.setStyleSheet("color: rgb(255, 255, 127);\n"
"background-color: rgba(255, 255, 255, 0);")
		self.Pos_Text.setObjectName("Pos_Text")
		self.formLayout.setWidget(2, QtWidgets.QFormLayout.ItemRole.LabelRole, self.Pos_Text)
		self.curLap_Text = QtWidgets.QLabel(self.widget_2)
		sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.MinimumExpanding, QtWidgets.QSizePolicy.Policy.Expanding)
		sizePolicy.setHorizontalStretch(0)
		sizePolicy.setVerticalStretch(0)
		sizePolicy.setHeightForWidth(self.curLap_Text.sizePolicy().hasHeightForWidth())
		self.curLap_Text.setSizePolicy(sizePolicy)
		font = QtGui.QFont()
		font.setPointSize(14)
		font.setBold(False)
		self.curLap_Text.setFont(font)
		self.curLap_Text.setStyleSheet("color: rgb(255, 255, 127);\n"
"background-color: rgba(255, 255, 255, 0);")
		self.curLap_Text.setObjectName("curLap_Text")
		self.formLayout.setWidget(7, QtWidgets.QFormLayout.ItemRole.LabelRole, self.curLap_Text)
		self.LastLap_Text = QtWidgets.QLabel(self.widget_2)
		sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.MinimumExpanding, QtWidgets.QSizePolicy.Policy.Expanding)
		sizePolicy.setHorizontalStretch(0)
		sizePolicy.setVerticalStretch(0)
		sizePolicy.setHeightForWidth(self.LastLap_Text.sizePolicy().hasHeightForWidth())
		self.LastLap_Text.setSizePolicy(sizePolicy)
		font = QtGui.QFont()
		font.setPointSize(14)
		font.setBold(False)
		self.LastLap_Text.setFont(font)
		self.LastLap_Text.setStyleSheet("color: rgb(255, 255, 127);\n"
"background-color: rgba(255, 255, 255, 0);")
		self.LastLap_Text.setObjectName("LastLap_Text")
		self.formLayout.setWidget(8, QtWidgets.QFormLayout.ItemRole.LabelRole, self.LastLap_Text)
		self.BenzLastLap_Text = QtWidgets.QLabel(self.widget_2)
		sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.MinimumExpanding, QtWidgets.QSizePolicy.Policy.Expanding)
		sizePolicy.setHorizontalStretch(0)
		sizePolicy.setVerticalStretch(0)
		sizePolicy.setHeightForWidth(self.BenzLastLap_Text.sizePolicy().hasHeightForWidth())
		self.BenzLastLap_Text.setSizePolicy(sizePolicy)
		font = QtGui.QFont()
		font.setPointSize(14)
		font.setBold(False)
		self.BenzLastLap_Text.setFont(font)
		self.BenzLastLap_Text.setStyleSheet("color: rgb(255, 255, 127);\n"
"background-color: rgba(255, 255, 255, 0);")
		self.BenzLastLap_Text.setObjectName("BenzLastLap_Text")
		self.formLayout.setWidget(13, QtWidgets.QFormLayout.ItemRole.LabelRole, self.BenzLastLap_Text)
		self.EstBenzin_Text = QtWidgets.QLabel(self.widget_2)
		sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.MinimumExpanding, QtWidgets.QSizePolicy.Policy.Expanding)
		sizePolicy.setHorizontalStretch(0)
		sizePolicy.setVerticalStretch(0)
		sizePolicy.setHeightForWidth(self.EstBenzin_Text.sizePolicy().hasHeightForWidth())
		self.EstBenzin_Text.setSizePolicy(sizePolicy)
		font = QtGui.QFont()
		font.setPointSize(14)
		font.setBold(False)
		self.EstBenzin_Text.setFont(font)
		self.EstBenzin_Text.setStyleSheet("color: rgb(255, 255, 127);\n"
"background-color: rgba(255, 255, 255, 0);")
		self.EstBenzin_Text.setObjectName("EstBenzin_Text")
		self.formLayout.setWidget(16, QtWidgets.QFormLayout.ItemRole.LabelRole, self.EstBenzin_Text)
		self.LapsNr = QtWidgets.QLabel(self.widget_2)
		sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.MinimumExpanding, QtWidgets.QSizePolicy.Policy.Expanding)
		sizePolicy.setHorizontalStretch(0)
		sizePolicy.setVerticalStretch(0)
		sizePolicy.setHeightForWidth(self.LapsNr.sizePolicy().hasHeightForWidth())
		self.LapsNr.setSizePolicy(sizePolicy)
		font = QtGui.QFont()
		font.setPointSize(14)
		font.setBold(False)
		self.LapsNr.setFont(font)
		self.LapsNr.setStyleSheet("color: rgb(255, 255, 127);\n"
"background-color: rgba(255, 255, 255, 0);")
		self.LapsNr.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
		self.LapsNr.setObjectName("LapsNr")
		self.formLayout.setWidget(1, QtWidgets.QFormLayout.ItemRole.FieldRole, self.LapsNr)
		self.Head_Race = QtWidgets.QLabel(self.widget_2)
		sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.MinimumExpanding, QtWidgets.QSizePolicy.Policy.Expanding)
		sizePolicy.setHorizontalStretch(0)
		sizePolicy.setVerticalStretch(0)
		sizePolicy.setHeightForWidth(self.Head_Race.sizePolicy().hasHeightForWidth())
		self.Head_Race.setSizePolicy(sizePolicy)
		font = QtGui.QFont()
		font.setPointSize(17)
		font.setBold(True)
		font.setUnderline(True)
		self.Head_Race.setFont(font)
		self.Head_Race.setStyleSheet("color: rgb(255, 255, 127);\n"
"background-color: rgba(255, 255, 255, 0);")
		self.Head_Race.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
		self.Head_Race.setObjectName("Head_Race")
		self.formLayout.setWidget(0, QtWidgets.QFormLayout.ItemRole.SpanningRole, self.Head_Race)
		self.Head_Laps = QtWidgets.QLabel(self.widget_2)
		sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.MinimumExpanding, QtWidgets.QSizePolicy.Policy.Expanding)
		sizePolicy.setHorizontalStretch(0)
		sizePolicy.setVerticalStretch(0)
		sizePolicy.setHeightForWidth(self.Head_Laps.sizePolicy().hasHeightForWidth())
		self.Head_Laps.setSizePolicy(sizePolicy)
		font = QtGui.QFont()
		font.setPointSize(17)
		font.setBold(True)
		font.setUnderline(True)
		self.Head_Laps.setFont(font)
		self.Head_Laps.setStyleSheet("color: rgb(255, 255, 127);\n"
"background-color: rgba(255, 255, 255, 0);")
		self.Head_Laps.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
		self.Head_Laps.setObjectName("Head_Laps")
		self.formLayout.setWidget(6, QtWidgets.QFormLayout.ItemRole.SpanningRole, self.Head_Laps)
		self.Head_Fuel = QtWidgets.QLabel(self.widget_2)
		sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.MinimumExpanding, QtWidgets.QSizePolicy.Policy.Expanding)
		sizePolicy.setHorizontalStretch(0)
		sizePolicy.setVerticalStretch(0)
		sizePolicy.setHeightForWidth(self.Head_Fuel.sizePolicy().hasHeightForWidth())
		self.Head_Fuel.setSizePolicy(sizePolicy)
		font = QtGui.QFont()
		font.setPointSize(17)
		font.setBold(True)
		font.setUnderline(True)
		self.Head_Fuel.setFont(font)
		self.Head_Fuel.setStyleSheet("color: rgb(255, 255, 127);\n"
"background-color: rgba(255, 255, 255, 0);")
		self.Head_Fuel.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
		self.Head_Fuel.setObjectName("Head_Fuel")
		self.formLayout.setWidget(12, QtWidgets.QFormLayout.ItemRole.SpanningRole, self.Head_Fuel)
		self.PositionNr = QtWidgets.QLabel(self.widget_2)
		sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.MinimumExpanding, QtWidgets.QSizePolicy.Policy.Expanding)
		sizePolicy.setHorizontalStretch(0)
		sizePolicy.setVerticalStretch(0)
		sizePolicy.setHeightForWidth(self.PositionNr.sizePolicy().hasHeightForWidth())
		self.PositionNr.setSizePolicy(sizePolicy)
		font = QtGui.QFont()
		font.setPointSize(14)
		font.setBold(False)
		self.PositionNr.setFont(font)
		self.PositionNr.setStyleSheet("color: rgb(255, 255, 127);\n"
"background-color: rgba(255, 255, 255, 0);")
		self.PositionNr.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
		self.PositionNr.setObjectName("PositionNr")
		self.formLayout.setWidget(2, QtWidgets.QFormLayout.ItemRole.FieldRole, self.PositionNr)
		self.Stint_Text = QtWidgets.QLabel(self.widget_2)
		sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.MinimumExpanding, QtWidgets.QSizePolicy.Policy.Expanding)
		sizePolicy.setHorizontalStretch(0)
		sizePolicy.setVerticalStretch(0)
		sizePolicy.setHeightForWidth(self.Stint_Text.sizePolicy().hasHeightForWidth())
		self.Stint_Text.setSizePolicy(sizePolicy)
		font = QtGui.QFont()
		font.setPointSize(14)
		font.setBold(False)
		self.Stint_Text.setFont(font)
		self.Stint_Text.setStyleSheet("color: rgb(255, 255, 127);\n"
"background-color: rgba(255, 255, 255, 0);")
		self.Stint_Text.setObjectName("Stint_Text")
		self.formLayout.setWidget(3, QtWidgets.QFormLayout.ItemRole.LabelRole, self.Stint_Text)
		self.Stint = QtWidgets.QLabel(self.widget_2)
		sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.MinimumExpanding, QtWidgets.QSizePolicy.Policy.Expanding)
		sizePolicy.setHorizontalStretch(0)
		sizePolicy.setVerticalStretch(0)
		sizePolicy.setHeightForWidth(self.Stint.sizePolicy().hasHeightForWidth())
		self.Stint.setSizePolicy(sizePolicy)
		font = QtGui.QFont()
		font.setPointSize(14)
		font.setBold(False)
		self.Stint.setFont(font)
		self.Stint.setStyleSheet("color: rgb(255, 255, 127);\n"
"background-color: rgba(255, 255, 255, 0);")
		self.Stint.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
		self.Stint.setObjectName("Stint")
		self.formLayout.setWidget(3, QtWidgets.QFormLayout.ItemRole.FieldRole, self.Stint)
		self.DayTime_Text = QtWidgets.QLabel(self.widget_2)
		sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.MinimumExpanding, QtWidgets.QSizePolicy.Policy.Expanding)
		sizePolicy.setHorizontalStretch(0)
		sizePolicy.setVerticalStretch(0)
		sizePolicy.setHeightForWidth(self.DayTime_Text.sizePolicy().hasHeightForWidth())
		self.DayTime_Text.setSizePolicy(sizePolicy)
		font = QtGui.QFont()
		font.setPointSize(14)
		font.setBold(False)
		self.DayTime_Text.setFont(font)
		self.DayTime_Text.setStyleSheet("color: rgb(255, 255, 127);\n"
"background-color: rgba(255, 255, 255, 0);")
		self.DayTime_Text.setObjectName("DayTime_Text")
		self.formLayout.setWidget(4, QtWidgets.QFormLayout.ItemRole.LabelRole, self.DayTime_Text)
		self.Tageszeit = QtWidgets.QLabel(self.widget_2)
		sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.MinimumExpanding, QtWidgets.QSizePolicy.Policy.Expanding)
		sizePolicy.setHorizontalStretch(0)
		sizePolicy.setVerticalStretch(0)
		sizePolicy.setHeightForWidth(self.Tageszeit.sizePolicy().hasHeightForWidth())
		self.Tageszeit.setSizePolicy(sizePolicy)
		font = QtGui.QFont()
		font.setPointSize(14)
		font.setBold(False)
		self.Tageszeit.setFont(font)
		self.Tageszeit.setStyleSheet("color: rgb(255, 255, 127);\n"
"background-color: rgba(255, 255, 255, 0);")
		self.Tageszeit.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
		self.Tageszeit.setObjectName("Tageszeit")
		self.formLayout.setWidget(4, QtWidgets.QFormLayout.ItemRole.FieldRole, self.Tageszeit)
		self.curLap = QtWidgets.QLabel(self.widget_2)
		font = QtGui.QFont()
		font.setPointSize(14)
		font.setBold(False)
		self.curLap.setFont(font)
		self.curLap.setStyleSheet("color: rgb(255, 255, 127);\n"
"background-color: rgba(255, 255, 255, 0);")
		self.curLap.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
		self.curLap.setObjectName("curLap")
		self.formLayout.setWidget(7, QtWidgets.QFormLayout.ItemRole.FieldRole, self.curLap)
		self.LastLap = QtWidgets.QLabel(self.widget_2)
		font = QtGui.QFont()
		font.setPointSize(14)
		font.setBold(False)
		self.LastLap.setFont(font)
		self.LastLap.setStyleSheet("color: rgb(255, 255, 127);\n"
"background-color: rgba(255, 255, 255, 0);")
		self.LastLap.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
		self.LastLap.setObjectName("LastLap")
		self.formLayout.setWidget(8, QtWidgets.QFormLayout.ItemRole.FieldRole, self.LastLap)
		self.BestLap_Text = QtWidgets.QLabel(self.widget_2)
		font = QtGui.QFont()
		font.setPointSize(14)
		font.setBold(False)
		self.BestLap_Text.setFont(font)
		self.BestLap_Text.setStyleSheet("color: rgb(255, 255, 127);\n"
"background-color: rgba(255, 255, 255, 0);")
		self.BestLap_Text.setObjectName("BestLap_Text")
		self.formLayout.setWidget(9, QtWidgets.QFormLayout.ItemRole.LabelRole, self.BestLap_Text)
		self.BestLap = QtWidgets.QLabel(self.widget_2)
		font = QtGui.QFont()
		font.setPointSize(14)
		font.setBold(False)
		self.BestLap.setFont(font)
		self.BestLap.setStyleSheet("color: rgb(255, 255, 127);\n"
"background-color: rgba(255, 255, 255, 0);")
		self.BestLap.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
		self.BestLap.setObjectName("BestLap")
		self.formLayout.setWidget(9, QtWidgets.QFormLayout.ItemRole.FieldRole, self.BestLap)
		self.averageLap_Text = QtWidgets.QLabel(self.widget_2)
		font = QtGui.QFont()
		font.setPointSize(14)
		font.setBold(False)
		self.averageLap_Text.setFont(font)
		self.averageLap_Text.setStyleSheet("color: rgb(255, 255, 127);\n"
"background-color: rgba(255, 255, 255, 0);")
		self.averageLap_Text.setObjectName("averageLap_Text")
		self.formLayout.setWidget(10, QtWidgets.QFormLayout.ItemRole.LabelRole, self.averageLap_Text)
		self.averageLap = QtWidgets.QLabel(self.widget_2)
		font = QtGui.QFont()
		font.setPointSize(14)
		font.setBold(False)
		self.averageLap.setFont(font)
		self.averageLap.setStyleSheet("color: rgb(255, 255, 127);\n"
"background-color: rgba(255, 255, 255, 0);")
		self.averageLap.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
		self.averageLap.setObjectName("averageLap")
		self.formLayout.setWidget(10, QtWidgets.QFormLayout.ItemRole.FieldRole, self.averageLap)
		self.DurchBenzin_Text = QtWidgets.QLabel(self.widget_2)
		font = QtGui.QFont()
		font.setPointSize(14)
		font.setBold(False)
		self.DurchBenzin_Text.setFont(font)
		self.DurchBenzin_Text.setStyleSheet("color: rgb(255, 255, 127);\n"
"background-color: rgba(255, 255, 255, 0);")
		self.DurchBenzin_Text.setObjectName("DurchBenzin_Text")
		self.formLayout.setWidget(14, QtWidgets.QFormLayout.ItemRole.LabelRole, self.DurchBenzin_Text)
		self.actualBenz_Text = QtWidgets.QLabel(self.widget_2)
		font = QtGui.QFont()
		font.setPointSize(14)
		font.setBold(False)
		self.actualBenz_Text.setFont(font)
		self.actualBenz_Text.setStyleSheet("color: rgb(255, 255, 127);\n"
"background-color: rgba(255, 255, 255, 0);")
		self.actualBenz_Text.setObjectName("actualBenz_Text")
		self.formLayout.setWidget(15, QtWidgets.QFormLayout.ItemRole.LabelRole, self.actualBenz_Text)
		self.BenzLastLap = QtWidgets.QLabel(self.widget_2)
		font = QtGui.QFont()
		font.setPointSize(14)
		font.setBold(False)
		self.BenzLastLap.setFont(font)
		self.BenzLastLap.setStyleSheet("color: rgb(255, 255, 127);\n"
"background-color: rgba(255, 255, 255, 0);")
		self.BenzLastLap.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
		self.BenzLastLap.setObjectName("BenzLastLap")
		self.formLayout.setWidget(13, QtWidgets.QFormLayout.ItemRole.FieldRole, self.BenzLastLap)
		self.DurchBenzin = QtWidgets.QLabel(self.widget_2)
		font = QtGui.QFont()
		font.setPointSize(14)
		font.setBold(False)
		self.DurchBenzin.setFont(font)
		self.DurchBenzin.setStyleSheet("color: rgb(255, 255, 127);\n"
"background-color: rgba(255, 255, 255, 0);")
		self.DurchBenzin.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
		self.DurchBenzin.setObjectName("DurchBenzin")
		self.formLayout.setWidget(14, QtWidgets.QFormLayout.ItemRole.FieldRole, self.DurchBenzin)
		self.BenzAktuell = QtWidgets.QLabel(self.widget_2)
		font = QtGui.QFont()
		font.setPointSize(14)
		font.setBold(False)
		self.BenzAktuell.setFont(font)
		self.BenzAktuell.setStyleSheet("color: rgb(255, 255, 127);\n"
"background-color: rgba(255, 255, 255, 0);")
		self.BenzAktuell.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
		self.BenzAktuell.setObjectName("BenzAktuell")
		self.formLayout.setWidget(15, QtWidgets.QFormLayout.ItemRole.FieldRole, self.BenzAktuell)
		self.BenzinEst = QtWidgets.QLabel(self.widget_2)
		font = QtGui.QFont()
		font.setPointSize(14)
		font.setBold(False)
		self.BenzinEst.setFont(font)
		self.BenzinEst.setStyleSheet("color: rgb(255, 255, 127);\n"
"background-color: rgba(255, 255, 255, 0);")
		self.BenzinEst.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
		self.BenzinEst.setObjectName("BenzinEst")
		self.formLayout.setWidget(16, QtWidgets.QFormLayout.ItemRole.FieldRole, self.BenzinEst)
		self.line_2 = QtWidgets.QFrame(self.widget_2)
		sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Fixed)
		sizePolicy.setHorizontalStretch(0)
		sizePolicy.setVerticalStretch(0)
		sizePolicy.setHeightForWidth(self.line_2.sizePolicy().hasHeightForWidth())
		self.line_2.setSizePolicy(sizePolicy)
		self.line_2.setMinimumSize(QtCore.QSize(50, 0))
		self.line_2.setStyleSheet("color: rgb(255, 255, 127);")
		self.line_2.setFrameShape(QtWidgets.QFrame.Shape.HLine)
		self.line_2.setFrameShadow(QtWidgets.QFrame.Shadow.Sunken)
		self.line_2.setObjectName("line_2")
		self.formLayout.setWidget(5, QtWidgets.QFormLayout.ItemRole.SpanningRole, self.line_2)
		self.line_3 = QtWidgets.QFrame(self.widget_2)
		sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Fixed)
		sizePolicy.setHorizontalStretch(0)
		sizePolicy.setVerticalStretch(0)
		sizePolicy.setHeightForWidth(self.line_3.sizePolicy().hasHeightForWidth())
		self.line_3.setSizePolicy(sizePolicy)
		self.line_3.setMinimumSize(QtCore.QSize(50, 0))
		self.line_3.setStyleSheet("color: rgb(255, 255, 127);")
		self.line_3.setFrameShape(QtWidgets.QFrame.Shape.HLine)
		self.line_3.setFrameShadow(QtWidgets.QFrame.Shadow.Sunken)
		self.line_3.setObjectName("line_3")
		self.formLayout.setWidget(11, QtWidgets.QFormLayout.ItemRole.SpanningRole, self.line_3)
		self.gridLayout.addWidget(self.widget_2, 0, 12, 5, 1)
		self.RPMWidget = QtWidgets.QWidget(self.widget)
		sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.MinimumExpanding, QtWidgets.QSizePolicy.Policy.MinimumExpanding)
		sizePolicy.setHorizontalStretch(0)
		sizePolicy.setVerticalStretch(0)
		sizePolicy.setHeightForWidth(self.RPMWidget.sizePolicy().hasHeightForWidth())
		self.RPMWidget.setSizePolicy(sizePolicy)
		self.RPMWidget.setMaximumSize(QtCore.QSize(660, 40))
		self.RPMWidget.setStyleSheet("background-color: qlineargradient(spread:pad, x1:0.508, y1:0.119319, x2:0.508413, y2:0, stop:0 rgba(0, 0, 0, 255), stop:1 rgba(255, 255, 255, 200));\n"
"border-top-left-radius:20px;\n"
"border-top-right-radius:20px;\n"
"border-bottom-left-radius:20px;\n"
"border-bottom-right-radius:20px;")
		self.RPMWidget.setObjectName("RPMWidget")
		self.horizontalLayout = QtWidgets.QHBoxLayout(self.RPMWidget)
		self.horizontalLayout.setObjectName("horizontalLayout")
		self.RPM1 = QtWidgets.QLabel(self.RPMWidget)
		sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.MinimumExpanding, QtWidgets.QSizePolicy.Policy.MinimumExpanding)
		sizePolicy.setHorizontalStretch(0)
		sizePolicy.setVerticalStretch(0)
		sizePolicy.setHeightForWidth(self.RPM1.sizePolicy().hasHeightForWidth())
		self.RPM1.setSizePolicy(sizePolicy)
		self.RPM1.setMaximumSize(QtCore.QSize(25, 25))
		self.RPM1.setStyleSheet("background-color: qradialgradient(spread:pad, cx:0.494413, cy:0.506, radius:0.543, fx:0.494413, fy:0.5, stop:0 rgba(0, 57, 255, 255), stop:0.27933 rgba(0, 255, 239, 0), stop:0.614525 rgba(0, 100, 255, 0), stop:0.709497 rgba(0, 255, 228, 0), stop:0.71 rgba(255, 0, 0, 0));\n"
"\n"
"")
		self.RPM1.setText("")
		self.RPM1.setObjectName("RPM1")
		self.horizontalLayout.addWidget(self.RPM1)
		self.RPM2 = QtWidgets.QLabel(self.RPMWidget)
		sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.MinimumExpanding, QtWidgets.QSizePolicy.Policy.MinimumExpanding)
		sizePolicy.setHorizontalStretch(0)
		sizePolicy.setVerticalStretch(0)
		sizePolicy.setHeightForWidth(self.RPM2.sizePolicy().hasHeightForWidth())
		self.RPM2.setSizePolicy(sizePolicy)
		self.RPM2.setMaximumSize(QtCore.QSize(25, 25))
		self.RPM2.setStyleSheet("background-color: qradialgradient(spread:pad, cx:0.494413, cy:0.506, radius:0.543, fx:0.494413, fy:0.5, stop:0 rgba(0, 57, 255, 255), stop:0.27933 rgba(0, 255, 239, 0), stop:0.614525 rgba(0, 100, 255, 0), stop:0.709497 rgba(0, 255, 228, 0), stop:0.71 rgba(255, 0, 0, 0));\n"
"")
		self.RPM2.setText("")
		self.RPM2.setObjectName("RPM2")
		self.horizontalLayout.addWidget(self.RPM2)
		self.RPM3 = QtWidgets.QLabel(self.RPMWidget)
		sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.MinimumExpanding, QtWidgets.QSizePolicy.Policy.MinimumExpanding)
		sizePolicy.setHorizontalStretch(0)
		sizePolicy.setVerticalStretch(0)
		sizePolicy.setHeightForWidth(self.RPM3.sizePolicy().hasHeightForWidth())
		self.RPM3.setSizePolicy(sizePolicy)
		self.RPM3.setMaximumSize(QtCore.QSize(25, 25))
		self.RPM3.setStyleSheet("background-color: qradialgradient(spread:pad, cx:0.494413, cy:0.506, radius:0.543, fx:0.494413, fy:0.5, stop:0 rgba(0, 57, 255, 255), stop:0.27933 rgba(0, 255, 239, 0), stop:0.614525 rgba(0, 100, 255, 0), stop:0.709497 rgba(0, 255, 228, 0), stop:0.71 rgba(255, 0, 0, 0));\n"
" ")
		self.RPM3.setFrameShape(QtWidgets.QFrame.Shape.Panel)
		self.RPM3.setFrameShadow(QtWidgets.QFrame.Shadow.Raised)
		self.RPM3.setLineWidth(0)
		self.RPM3.setMidLineWidth(1)
		self.RPM3.setText("")
		self.RPM3.setObjectName("RPM3")
		self.horizontalLayout.addWidget(self.RPM3)
		self.RPM4 = QtWidgets.QLabel(self.RPMWidget)
		sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.MinimumExpanding, QtWidgets.QSizePolicy.Policy.MinimumExpanding)
		sizePolicy.setHorizontalStretch(0)
		sizePolicy.setVerticalStretch(0)
		sizePolicy.setHeightForWidth(self.RPM4.sizePolicy().hasHeightForWidth())
		self.RPM4.setSizePolicy(sizePolicy)
		self.RPM4.setMaximumSize(QtCore.QSize(25, 25))
		self.RPM4.setStyleSheet("background-color: qradialgradient(spread:pad, cx:0.494413, cy:0.506, radius:0.543, fx:0.494413, fy:0.5, stop:0 rgba(0, 255, 14, 255), stop:0.27933 rgba(232, 255, 0, 0), stop:0.614525 rgba(71, 255, 0, 0), stop:0.709497 rgba(255, 235, 0, 0), stop:0.71 rgba(255, 0, 0, 0));")
		self.RPM4.setText("")
		self.RPM4.setObjectName("RPM4")
		self.horizontalLayout.addWidget(self.RPM4)
		self.RPM5 = QtWidgets.QLabel(self.RPMWidget)
		sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.MinimumExpanding, QtWidgets.QSizePolicy.Policy.MinimumExpanding)
		sizePolicy.setHorizontalStretch(0)
		sizePolicy.setVerticalStretch(0)
		sizePolicy.setHeightForWidth(self.RPM5.sizePolicy().hasHeightForWidth())
		self.RPM5.setSizePolicy(sizePolicy)
		self.RPM5.setMaximumSize(QtCore.QSize(25, 25))
		self.RPM5.setStyleSheet("background-color: qradialgradient(spread:pad, cx:0.494413, cy:0.506, radius:0.543, fx:0.494413, fy:0.5, stop:0 rgba(0, 255, 14, 255), stop:0.27933 rgba(232, 255, 0, 0), stop:0.614525 rgba(71, 255, 0, 0), stop:0.709497 rgba(255, 235, 0, 0), stop:0.71 rgba(255, 0, 0, 0));")
		self.RPM5.setText("")
		self.RPM5.setObjectName("RPM5")
		self.horizontalLayout.addWidget(self.RPM5)
		self.RPM6 = QtWidgets.QLabel(self.RPMWidget)
		sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.MinimumExpanding, QtWidgets.QSizePolicy.Policy.MinimumExpanding)
		sizePolicy.setHorizontalStretch(0)
		sizePolicy.setVerticalStretch(0)
		sizePolicy.setHeightForWidth(self.RPM6.sizePolicy().hasHeightForWidth())
		self.RPM6.setSizePolicy(sizePolicy)
		self.RPM6.setMaximumSize(QtCore.QSize(25, 25))
		self.RPM6.setStyleSheet("background-color: qradialgradient(spread:pad, cx:0.494413, cy:0.506, radius:0.543, fx:0.494413, fy:0.5, stop:0 rgba(0, 255, 14, 255), stop:0.27933 rgba(232, 255, 0, 0), stop:0.614525 rgba(71, 255, 0, 0), stop:0.709497 rgba(255, 235, 0, 0), stop:0.71 rgba(255, 0, 0, 0));")
		self.RPM6.setText("")
		self.RPM6.setObjectName("RPM6")
		self.horizontalLayout.addWidget(self.RPM6)
		self.RPM7 = QtWidgets.QLabel(self.RPMWidget)
		sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.MinimumExpanding, QtWidgets.QSizePolicy.Policy.MinimumExpanding)
		sizePolicy.setHorizontalStretch(0)
		sizePolicy.setVerticalStretch(0)
		sizePolicy.setHeightForWidth(self.RPM7.sizePolicy().hasHeightForWidth())
		self.RPM7.setSizePolicy(sizePolicy)
		self.RPM7.setMaximumSize(QtCore.QSize(25, 25))
		self.RPM7.setStyleSheet("background-color: qradialgradient(spread:pad, cx:0.494413, cy:0.506, radius:0.543, fx:0.494413, fy:0.5, stop:0 rgba(0, 255, 14, 255), stop:0.27933 rgba(232, 255, 0, 0), stop:0.614525 rgba(71, 255, 0, 0), stop:0.709497 rgba(255, 235, 0, 0), stop:0.71 rgba(255, 0, 0, 0));")
		self.RPM7.setText("")
		self.RPM7.setObjectName("RPM7")
		self.horizontalLayout.addWidget(self.RPM7)
		self.RPM8 = QtWidgets.QLabel(self.RPMWidget)
		sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.MinimumExpanding, QtWidgets.QSizePolicy.Policy.MinimumExpanding)
		sizePolicy.setHorizontalStretch(0)
		sizePolicy.setVerticalStretch(0)
		sizePolicy.setHeightForWidth(self.RPM8.sizePolicy().hasHeightForWidth())
		self.RPM8.setSizePolicy(sizePolicy)
		self.RPM8.setMaximumSize(QtCore.QSize(25, 25))
		self.RPM8.setStyleSheet("background-color: qradialgradient(spread:pad, cx:0.494413, cy:0.506, radius:0.543, fx:0.494413, fy:0.5, stop:0 rgba(255, 0, 0, 255), stop:0.27933 rgba(255, 255, 0, 0), stop:0.614525 rgba(255, 0, 0, 0), stop:0.709497 rgba(255, 64, 0, 0), stop:0.71 rgba(255, 0, 0, 0));")
		self.RPM8.setText("")
		self.RPM8.setObjectName("RPM8")
		self.horizontalLayout.addWidget(self.RPM8)
		self.RPM9 = QtWidgets.QLabel(self.RPMWidget)
		sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.MinimumExpanding, QtWidgets.QSizePolicy.Policy.MinimumExpanding)
		sizePolicy.setHorizontalStretch(0)
		sizePolicy.setVerticalStretch(0)
		sizePolicy.setHeightForWidth(self.RPM9.sizePolicy().hasHeightForWidth())
		self.RPM9.setSizePolicy(sizePolicy)
		self.RPM9.setMaximumSize(QtCore.QSize(25, 25))
		self.RPM9.setStyleSheet("background-color: qradialgradient(spread:pad, cx:0.494413, cy:0.506, radius:0.543, fx:0.494413, fy:0.5, stop:0 rgba(255, 0, 0, 255), stop:0.27933 rgba(255, 255, 0, 0), stop:0.614525 rgba(255, 0, 0, 0), stop:0.709497 rgba(255, 64, 0, 0), stop:0.71 rgba(255, 0, 0, 0));")
		self.RPM9.setText("")
		self.RPM9.setObjectName("RPM9")
		self.horizontalLayout.addWidget(self.RPM9)
		self.gridLayout.addWidget(self.RPMWidget, 2, 1, 1, 5)




		self.StoppButton = QtWidgets.QPushButton(self.widget)
		sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.MinimumExpanding, QtWidgets.QSizePolicy.Policy.MinimumExpanding)
		sizePolicy.setHorizontalStretch(0)
		sizePolicy.setVerticalStretch(0)
		sizePolicy.setHeightForWidth(self.StoppButton.sizePolicy().hasHeightForWidth())
		self.StoppButton.setSizePolicy(sizePolicy)
		self.StoppButton.setMaximumSize(QtCore.QSize(60, 60))
		font = QtGui.QFont()
		font.setPointSize(12)
		font.setBold(True)
		self.StoppButton.setFont(font)
		self.StoppButton.setStyleSheet("background-color: qradialgradient(spread:pad, cx:0.5, cy:0.5, radius:0.5, fx:0.5, fy:0.5, stop:0 rgba(255, 0, 0, 255), stop:0.19397 rgba(255, 0, 0, 255), stop:0.202312 rgba(255, 0, 0, 255), stop:0.240223 rgba(255, 139, 139, 255), stop:0.877095 rgba(255, 0, 0, 255), stop:0.888268 rgba(255, 255, 255, 255), stop:0.988827 rgba(255, 158, 158, 0));\n"
"color: rgb(0, 0, 0);")
		self.StoppButton.setObjectName("StoppButton")
		self.gridLayout.addWidget(self.StoppButton, 2, 6, 1, 1)


		self.StartButton = QtWidgets.QPushButton(self.widget)
		sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.MinimumExpanding, QtWidgets.QSizePolicy.Policy.MinimumExpanding)
		sizePolicy.setHorizontalStretch(0)
		sizePolicy.setVerticalStretch(0)
		sizePolicy.setHeightForWidth(self.StartButton.sizePolicy().hasHeightForWidth())
		self.StartButton.setSizePolicy(sizePolicy)
		self.StartButton.setMaximumSize(QtCore.QSize(60, 60))
		font = QtGui.QFont()
		font.setPointSize(12)
		font.setBold(True)
		self.StartButton.setFont(font)
		self.StartButton.setStyleSheet("background-color: qradialgradient(spread:pad, cx:0.5, cy:0.5, radius:0.5, fx:0.5, fy:0.5, stop:0 rgba(255, 0, 0, 255), stop:0.19397 rgba(255, 0, 0, 255), stop:0.202312 rgba(255, 0, 0, 255), stop:0.240223 rgba(255, 139, 139, 255), stop:0.877095 rgba(255, 0, 0, 255), stop:0.888268 rgba(255, 255, 255, 255), stop:0.988827 rgba(255, 158, 158, 0));\n"
"color: rgb(0, 0, 0);")
		self.StartButton.setObjectName("StartButton")
		self.StartButton.clicked.connect(update_Label)
		self.gridLayout.addWidget(self.StartButton, 3, 6, 1, 1)



			
		self.ResetButton = QtWidgets.QPushButton(self.widget)
		sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.MinimumExpanding, QtWidgets.QSizePolicy.Policy.MinimumExpanding)
		sizePolicy.setHorizontalStretch(0)
		sizePolicy.setVerticalStretch(0)
		sizePolicy.setHeightForWidth(self.ResetButton.sizePolicy().hasHeightForWidth())
		self.ResetButton.setSizePolicy(sizePolicy)
		self.ResetButton.setMaximumSize(QtCore.QSize(60, 60))
		font = QtGui.QFont()
		font.setPointSize(12)
		font.setBold(True)
		self.ResetButton.setFont(font)
		self.ResetButton.setStyleSheet("background-color: qradialgradient(spread:pad, cx:0.5, cy:0.5, radius:0.5, fx:0.5, fy:0.5, stop:0 rgba(255, 0, 0, 255), stop:0.19397 rgba(255, 0, 0, 255), stop:0.202312 rgba(255, 0, 0, 255), stop:0.240223 rgba(255, 139, 139, 255), stop:0.877095 rgba(255, 0, 0, 255), stop:0.888268 rgba(255, 255, 255, 255), stop:0.988827 rgba(255, 158, 158, 0));\n"
"color: rgb(0, 0, 0);")
		self.ResetButton.setObjectName("ResetButton")
		self.ResetButton.clicked.connect(Reset_Label)
		self.gridLayout.addWidget(self.ResetButton, 4, 6, 1, 1)




		self.gridLayout.setColumnStretch(0, 3)
		self.gridLayout.setColumnStretch(1, 2)
		self.gridLayout.setColumnStretch(2, 2)
		self.gridLayout.setColumnStretch(3, 2)
		self.gridLayout.setColumnStretch(4, 2)
		self.gridLayout.setColumnStretch(5, 2)
		self.gridLayout.setColumnStretch(6, 2)
		self.gridLayout.setColumnStretch(7, 2)
		self.gridLayout.setColumnStretch(8, 2)
		self.gridLayout.setColumnStretch(12, 3)
		self.gridLayout_2.addLayout(self.gridLayout, 0, 0, 1, 1)
		self.verticalLayout.addWidget(self.widget)


		MainWindow.setCentralWidget(self.centralwidget)
		self.menubar = QtWidgets.QMenuBar(MainWindow)
		self.menubar.setGeometry(QtCore.QRect(0, 0, 1000, 21))
		self.menubar.setObjectName("menubar")
		self.menubar.setStyleSheet("color: rgb(255, 255, 127); background-color: qlineargradient(spread:pad, x1:0.095, y1:0.108227, x2:0.100324, y2:0.614, stop:0 rgba(27, 38, 216, 255), stop:1 rgba(0, 0, 0, 255));")
		
		self.menubar.addMenu("Edit")
		self.menubar.addMenu("View")
		self.menubar.addMenu("Help")  		
		
		self.actionFile = self.menubar.addMenu("File")
		self.actionFile.addAction("New")
		self.actionFile.addAction("Open")
		self.actionFile.addAction("Save")
		self.actionFile.addSeparator()
		
		self.exitAct = QAction(QIcon('exit.png'), '&Exit')
		self.exitAct.setShortcut('Ctrl+Q')
		self.exitAct.setStatusTip('Exit application')
		self.exitAct.triggered.connect(qApp.quit)	        
		self.actionFile.addAction(self.exitAct)
		
  
		
		MainWindow.setMenuBar(self.menubar)
		self.statusbar = QtWidgets.QStatusBar(MainWindow)
		self.statusbar.setObjectName("statusbar")
		MainWindow.setStatusBar(self.statusbar)


		self.retranslateUi(MainWindow)
		QtCore.QMetaObject.connectSlotsByName(MainWindow)

	def retranslateUi(self, MainWindow):
		_translate = QtCore.QCoreApplication.translate
		MainWindow.setWindowTitle(_translate("MainWindow", "GT7 Dashboard and Telemetry"))
		self.Tyre_FL_Label.setText(_translate("MainWindow", " - "))
		self.Tyre_FR_Label.setText(_translate("MainWindow", " - "))
		self.Tyre_RL_Label.setText(_translate("MainWindow", " - "))
		self.Tyre_RR_Label.setText(_translate("MainWindow", " - "))
		self.LapsNr_Text.setText(_translate("MainWindow", "Lap :"))
		self.Pos_Text.setText(_translate("MainWindow", "Pos :"))
		self.curLap_Text.setText(_translate("MainWindow", "current :"))
		self.LastLap_Text.setText(_translate("MainWindow", "last :"))
		self.BenzLastLap_Text.setText(_translate("MainWindow", "last Lap :"))
		self.EstBenzin_Text.setText(_translate("MainWindow", "estimate :"))
		self.LapsNr.setText(_translate("MainWindow", "- / -"))
		self.Head_Race.setText(_translate("MainWindow", "Race-Data"))
		self.Head_Laps.setText(_translate("MainWindow", "Lap-Times"))
		self.Head_Fuel.setText(_translate("MainWindow", "Fuel"))
		self.PositionNr.setText(_translate("MainWindow", "- / -"))
		self.Stint_Text.setText(_translate("MainWindow", "Stint :"))
		self.Stint.setText(_translate("MainWindow", "-"))
		self.DayTime_Text.setText(_translate("MainWindow", "Time :"))
		self.Tageszeit.setText(_translate("MainWindow", "--:--:--"))
		self.curLap.setText(_translate("MainWindow", " ---"))
		self.LastLap.setText(_translate("MainWindow", " ---"))
		self.BestLap_Text.setText(_translate("MainWindow", "best :"))
		self.BestLap.setText(_translate("MainWindow", " ---"))
		self.averageLap_Text.setText(_translate("MainWindow", "average :"))
		self.averageLap.setText(_translate("MainWindow", " ---"))
		self.DurchBenzin_Text.setText(_translate("MainWindow", "average :"))
		self.actualBenz_Text.setText(_translate("MainWindow", "actual :"))
		self.BenzLastLap.setText(_translate("MainWindow", "0"))
		self.DurchBenzin.setText(_translate("MainWindow", "0"))
		self.BenzAktuell.setText(_translate("MainWindow", "0"))
		self.BenzinEst.setText(_translate("MainWindow", "0"))
		self.StartButton.setText(_translate("MainWindow", "Start"))
		self.StoppButton.setText(_translate("MainWindow", "Pause"))
		self.ResetButton.setText(_translate("MainWindow", "Reset"))
#----------------------------------------------          ENDE FENSTER                  ----------------------------------------------



if __name__ == "__main__":
	import sys
	app = QtWidgets.QApplication(sys.argv)
	MainWindow = QtWidgets.QMainWindow()
	ui = Ui_MainWindow()
	ui.setupUi(MainWindow)
	MainWindow.show()
	sys.exit(app.exec())
