
import os
from machine import Pin
import time
pin = Pin(0, Pin.IN, Pin.PULL_UP)
if pin.value() == 0:
  print("Don't load main selected by keypress..")
  sys.exit(0)
  
from microWebSrv import MicroWebSrv
import _thread
import wlanlib
import pccontrol
from pincontrol import pin_Control
from tft_control import tft_Control
from btn_control import btn_Control
import json

WS_messages = False
srv_run_in_thread = True
ws_run_in_thread = False
data = {}
wifiRetry=5
@MicroWebSrv.route('/update/<time>')
@MicroWebSrv.route('/update/<time>/<client>') 
@MicroWebSrv.route('/update/<time>/<client>/<minerstatus>')   
@MicroWebSrv.route('/update')                     
def _httpHandlerEditWithArgs(httpClient, httpResponse, args={}) :
    message = {}
    message["status"]="success"
    if 'time' in args :
      message["time"]=args['time']
    if 'client' in args :
      message["client"]=args['client']
    if 'minerstatus' in args :
      message["minerstatus"]=args['minerstatus']
    json_dump = json.dumps(message)
    content=json_dump
    httpResponse.WriteResponseOk( headers = None,contentType = "application/json",contentCharset = "UTF-8", content = content )
  
@MicroWebSrv.route('/reset')                     
def _httpHandlerEditWithArgs(httpClient, httpResponse, args={}) :
    message = {}
    message["status"]="success"
    message["task"]="reset"
    json_dump = json.dumps(message)
    content=json_dump
    httpResponse.WriteResponseOk( headers = None,contentType = "application/json",contentCharset = "UTF-8", content = content )
    _thread.sendmsg(0, '{"command" : "pressReset"}')

@MicroWebSrv.route('/forceshutdown')                     
def _httpHandlerEditWithArgs(httpClient, httpResponse, args={}) :
    message = {}
    message["status"]="success"
    message["task"]="forceshutdown"
    json_dump = json.dumps(message)
    content=json_dump
    httpResponse.WriteResponseOk( headers = None,contentType = "application/json",contentCharset = "UTF-8", content = content )
    _thread.sendmsg(0, '{"command" : "pressPower", "seconds" : 6}')
    
@MicroWebSrv.route('/power')                     
def _httpHandlerEditWithArgs(httpClient, httpResponse, args={}) :
    message = {}
    message["status"]="success"
    message["task"]="power"
    json_dump = json.dumps(message)
    content=json_dump
    httpResponse.WriteResponseOk( headers = None,contentType = "application/json",contentCharset = "UTF-8", content = content )
    _thread.sendmsg(0, '{"command" : "pressPower", "seconds" : 1}')
    
def try_again():
  time.sleep(10)
  reboot()
  
def main():
  try:
    mywlanlib=wlanlib.wlan_control()
    _thread.list()
    mytft=tft_Control()
    mypins=pin_Control()
    mybtn=btn_Control()
    mybtn.activate_button()
    th1 = _thread.start_new_thread("WIFITH#1", mywlanlib.setup_network, ())
    th3 = _thread.start_new_thread("PINCTL#1", mypins.startPinThread, ())
    th2 = _thread.start_new_thread("TFTTH#1", mytft.tft_monitor_data, ())
    _thread.sendmsg(0, '{"tft_command" : "message", 1 : "Connecting to wlan.."}')
    data["try"]=1
    while mywlanlib.wlan().isconnected() == False and data["try"] <= 10:
      print("Waiting WIFI to be ready")
      _thread.sendmsg(0, '{"tft_command" : "message", 2 : "Waiting WIFI to be ready.. %s"}' % str(data["try"]))
      data["try"]+=1
      time.sleep(1)
      pass
    _thread.sendmsg(0, '{"tft_command" : "message", 3 : "Connection established.."}')
    print("Done")
    srv = MicroWebSrv()
    srv.MaxWebSocketRecvLen     = 256
    srv.WebSocketThreaded       = ws_run_in_thread
    srv.WebSocketStackSize      = 4096
    srv.Start(threaded=srv_run_in_thread, stackSize=8192)
    _thread.sendmsg(0, '{"tft_command" : "message", 4 : "Web server started.."}')
    time.sleep(1)
    _thread.sendmsg(0, '{"tft_command" : "message", "clear" : "True", "center" : "IP Address : %s"}' % mywlanlib.get_ip())
    if mywlanlib.get_ip() == "0.0.0.0":
      try_again()
  except Exception as e:
    print("[EXCEPTION] - Exception in main thread : %s" % _thread.getSelfName())
    print(e)
    pass
if __name__ == "__main__":
    main()
    #test()
