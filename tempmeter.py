import os
import glob
import time
import sys
import datetime
os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')
base_dir = '/sys/bus/w1/devices/'
try:
    device_folder = glob.glob(base_dir + '28*')
    print "Measurement started:"+str(datetime.datetime.now())
    print device_folder
except:
    sys.exit("No sensors found!")

def read_temp_raw(c):
    cc=c+'/w1_slave'
    f = open(cc, 'r')
#    print c+"    "
    lines = f.readlines()
    f.close()
    return lines
def read_temp(c):
    lines = read_temp_raw(c)
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = read_temp_raw(c)
    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        temp_string = lines[1][equals_pos+2:]
        temp_c = float(temp_string) / 1000.0
        return temp_c
while True:
    ss=0
    ttemp=[]
    for dev in device_folder:
#        print (read_temp(dev))
        ttemp.append(read_temp(dev))
        ss=ss+1
    try:
# This tries to open an existing file but creates a new file if necessary.
        logfile = open("temp_log.txt", "a")
        try:
            logfile.write(datetime.datetime.now().strftime('%Y.%m.%d %H:%M:%S')+" "+str(ttemp)+"\n")
        finally:
            logfile.close()
    except IOError:
        pass


    print datetime.datetime.now().strftime('%Y.%m.%d %H:%M:%S')+" "+str(ttemp)
    time.sleep(10)
