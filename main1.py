
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
import pincontrol
import json
import gc

WS_messages = False
srv_run_in_thread = True
ws_run_in_thread = False
data = {}

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
    
@MicroWebSrv.route('/presspower')                     
def _httpHandlerEditWithArgs(httpClient, httpResponse, args={}) :
    message = {}
    message["status"]="success"
    message["task"]="presspower"
    json_dump = json.dumps(message)
    content=json_dump
    httpResponse.WriteResponseOk( headers = None,contentType = "application/json",contentCharset = "UTF-8", content = content )
    _thread.sendmsg(0, '{"command" : "pressPower", "seconds" : 1}')
    
def main():
  try:
    mywlanlib=wlanlib.wlan_control()
    pcControl = pccontrol.pc_control()
    mypins=pincontrol.pinControl()
    th1 = _thread.start_new_thread("WIFITH#1", mywlanlib.setup_network, ())
    th3 = _thread.start_new_thread("PINCTL#1", mypins.startPinThread, ())
    th2 = _thread.start_new_thread("TFTTH#1", pcControl.monitor_data, ())
    pcControl.send_message_to_tft("line1", "Connecting to wlan..")
    data["try"]=1
    while mywlanlib.wlan().isconnected() == False or data["try"] == 10:
      print("Waiting WIFI to be ready")
      pcControl.send_message_to_tft("line2", "Waiting WIFI to be ready.."+str(data["try"]))
      data["try"]+=1
      time.sleep(5)
      pass
    
    pcControl.send_message_to_tft("line3", "Connection established..")
    pcControl.clear_display(3)
    pcControl.empty_buffer()
    pcControl.send_message_to_tft("line1", "IP Address : "+mywlanlib.get_ip())
    pcControl.activate_button()
    srv = MicroWebSrv()
    srv.MaxWebSocketRecvLen     = 256
    srv.WebSocketThreaded       = ws_run_in_thread
    srv.WebSocketStackSize      = 4096
    srv.Start(threaded=srv_run_in_thread, stackSize=8192)
  except Exception as e:
    print("[EXCEPTION] - Exception in main thread : %s" % _thread.getSelfName())
    print(e)
    pass
if __name__ == "__main__":
    gc.collect()
    main()
    #test()
