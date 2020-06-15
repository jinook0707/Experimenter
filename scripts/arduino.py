#[flag:import-begin] !!! DO NOT EDIT THIS LINE !!!
import serial #[flag_marker:arduino]
#[flag:import-end] !!! DO NOT EDIT THIS LINE !!!

# --------------------------------------------------
#[flag:function-begin] !!! DO NOT EDIT THIS LINE !!!

def try_open(port): #[flag_marker:arduino]
    ''' function for Arduino-chip connection
    '''
    try:
        port = serial.Serial(port, 9600, timeout = 0)
    except serial.SerialException:
        return None
    else:
        return port
# --------------------------------------------------
def serial_scan(ARDUINO_USB_GLOB): #[flag_marker:arduino]
    ''' function for Arduino-chip connection
    '''
    for fn in glob(ARDUINO_USB_GLOB):
        port = try_open(fn)
        if port is not None:
            yield port
# --------------------------------------------------
#[flag:function-end] !!! DO NOT EDIT THIS LINE !!!


#[flag:init-begin] !!! DO NOT EDIT THIS LINE !!!
    ARDUINO_MSG = "motor_on" #[flag:arduino] #[flag_marker:arduino]
    if 'darwin' in sys.platform: ARDUINO_USB_GLOB = "/dev/cu.usbmodem*" #[flag_marker:arduino]
    elif 'linux' in sys.platform: ARDUINO_USB_GLOB = "/dev/ttyACM*" #[flag_marker:arduino]
    for aConn in serial_scan(ARDUINO_USB_GLOB): #[flag_marker:arduino]
        ARDUINO_PORT = aConn.name #[flag_marker:arduino]
        aConn = aConn #[flag_marker:arduino]
    if ARDUINO_PORT == "": print("No arduino connection is established") #[flag_marker:arduino]
    else: print("Arduino is connected : %s"%(ARDUINO_PORT)) #[flag_marker:arduino]
#[flag:init-end] !!! DO NOT EDIT THIS LINE !!!


