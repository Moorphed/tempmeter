# find logging.debug("Logging") and in next line put your google account credential
# create in google doc spreadsheet and put 1 in F2 cell
# change "test22" to your spreadsheet name - to run use following command 'sudo python tempmeter.py &'

import os
import glob
import time
import sys
import datetime
import gspread
import logging

logging.basicConfig(filename="appLog.log", format='%(levelname)s: %(asctime)s %(message)s', level=logging.INFO)
logging.info("---------------------------------------")
logging.info("Application Start")

#gpio initialise root perm needed
logging.debug("Configuration of GPIO")
os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')
logging.info("GPIO configured")
#gpio initialise

base_dir = '/sys/bus/w1/devices/'
try:
    device_folder = glob.glob(base_dir + '28*')
    print "Measurement started:" + str(datetime.datetime.now())
    print device_folder
    logging.info("Sensors found: " + str(device_folder))
except:
    logging.error("No sensors found!")
    logging.error("Application STOP")
    sys.exit("No sensors found!")


def read_temp_raw(c):
    cc = c + '/w1_slave'
    f = open(cc, 'r')
#    print c+"    "
    lines = f.readlines()
    f.close()
    return lines


def read_temp(c):
    lines = read_temp_raw(c)
    while lines[0].strip()[-3:] != 'YES':
        logging.debug("Read temp - Wrong control sum.")
        time.sleep(0.2)
        lines = read_temp_raw(c)
    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        temp_string = lines[1][equals_pos + 2:]
        temp_c = float(temp_string) / 1000.0
        logging.debug("Readed temp - "+str(temp_c))
        return temp_c


def write_data_toGoogle():
    logging.debug("Write date to Google - start")
    try:
        logging.debug("Logging")
        gc = gspread.login('username@gmail.com', 'userpassword')
        wks = gc.open('test22').sheet1
        cell_index = int(wks.acell('F2').value)
        try:
            logging.debug("Check if add a new row")
            if wks.row_count < cell_index:
                logging.debug("Adding 1 row")
                wks.add_rows(1)
            try:
                logging.info("Uloading data to google doc")
                wks.update_acell("A" + str(cell_index),str(datetime.datetime.now().strftime('%Y.%m.%d')))
                wks.update_acell("B" + str(cell_index),str(datetime.datetime.now().strftime('%H:%M:%S')))
                wks.update_acell("C" + str(cell_index), ttemp[0])
                wks.update_acell("D" + str(cell_index), ttemp[1])
                wks.update_acell("E" + str(cell_index), ttemp[2])
                cell_index = cell_index + 1
                wks.update_acell("F2", cell_index)
            except:
                logging.error("Can't add data to google.")
#                wks.add_rows(20)
#                pass
            #
        except:
            logging.error("Can't add new row!")
#            pass
    except:
        logging.error("No access to google doc")
#        pass


def write_data_toFile():
    try:
# This tries to open an existing file but creates a new file if necessary.
        datafile = open("temp_log.txt", "a")
        logging.debug("Write temp to file - start")
        try:
            datafile.write(datetime.datetime.now().strftime('%Y.%m.%d %H:%M:%S') + " " + str(ttemp)+"\n")
            logging.info("Write to file")
        finally:
            datafile.close()
    except IOError:
        logging.error("Write to file - IO Error")
#        pass


while True:
    ss = 0
    ttemp = []
    logging.info("Measurement period started.")
    for dev in device_folder:

        ttemp.append(read_temp(dev))
        time.sleep(5)
        ss = ss + 1

    write_data_toFile()
    write_data_toGoogle()
#delay
    logging.info("Waiting 2 min.")
    time.sleep(120)
