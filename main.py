import machine, display, time, math, network, utime, gc
from machine import Timer
import pccontrol
from microWebSrv import MicroWebSrv

ipstring=station.ifconfig()[0]
led2 = Pin(2, Pin.OUT)
ledstate= {}
ledstate["led2"]=led2.value()

def get_gpio_state_string(pin):
  global ledstate
  if ledstate["led"+str(pin)] == 1:
    gpio_state="ON"
  else:
    gpio_state="OFF"
  return gpio_state
  
def write_tft():
  global tft
  global ipstring
  tft.clear()
  tft.text(5,18,"GPIO2:"+get_gpio_state_string(2))
  tft.text(5,5,ipstring)

def update_led_value(pin, value):
  global ledstate
  ledstate["led"+str(pin)]=value
  

  

def toggle_pin(pin):
  global ledstate
  global led2
  print(ledstate["led2"])
  if ledstate["led2"] == 1:
    led2.value(0)
    update_led_value(2, 0)
  else:
    led2.value(1)
    update_led_value(2, 1)
  
  
def clear_display():
  tft.set_fg(0xFFFFFF)
  tft.set_bg(0x000000)
  tft.clear()
  
  
def initialize_display():
  global tft
  tft.init(tft.ST7789,bgr=False,rot=tft.LANDSCAPE, miso=17,backl_pin=4,backl_on=1, mosi=19, clk=18, cs=5, dc=16)
  tft.setwin(40,52,320,240)

  #tft.text(120-int(tft.textWidth(ipstring)/2),67-int(tft.fontSize()[1]/2),ipstring,0xFFFFFF)
  
def web_page():
  #gpio_state=get_gpio_state_string(2)
  global data
  data["line2"] = "GPIO2:"+get_gpio_state_string(2)
  pcControl.write_to_tft(data)
  #write_tft()
  html = """<html><head> <title>ESP Web Server</title> <meta name="viewport" content="width=device-width, initial-scale=1">
  <link rel="icon" href="data:,"> <style>html{font-family: Helvetica; display:inline-block; margin: 0px auto; text-align: center;}
  h1{color: #0F3376; padding: 2vh;}p{font-size: 1.5rem;}.button{display: inline-block; background-color: #e7bd3b; border: none; 
  border-radius: 4px; color: white; padding: 16px 40px; text-decoration: none; font-size: 30px; margin: 2px; cursor: pointer;}
  .button2{background-color: #4286f4;}</style></head><body> <h1>ESP Web Server</h1> 
  <p>GPIO state: <strong>""" + data["line2"] + """</strong></p><p><a href="/?led=on"><button class="button">ON</button></a></p>
  <p><a href="/?led=off"><button class="button button2">OFF</button></a></p></body></html>"""
  return html

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('', 80))
s.listen(5)
tft = display.TFT()
pcControl = pccontrol.pc_control()

#initialize_display()
#clear_display()
pcControl.initialize_display()
pcControl.clear_display()


def handle_interrupt(pin):
  print("button pressed")

data = {"line1":ipstring, "line2": "GPIO2:"+get_gpio_state_string(2)}
#write_tft()
pcControl.write_to_tft(data)
tim0 = Timer(0)

#pir = Pin(35, Pin.IN)
#pir.init(trigger=Pin.IRQ_RISING, handler=handle_interrupt, debounce=1000, acttime=400)
pcControl.activate_button()

while True:
  conn, addr = s.accept()
  print('Got a connection from %s' % str(addr))
  request = conn.recv(1024)
  request = str(request)
  print('Content = %s' % request)
  led_on = request.find('/?led=on')
  led_off = request.find('/?led=off')
  toggle = request.find('/?toggle')
  reset = request.find('/?reset')
  poweroff = request.find('/?poweroff')
  test = request.find('/?test')
  if led_on == 6:
    print('LED ON')
    ledstate["led2"]=1
    led2.value(1)
  if led_off == 6:
    print('LED OFF')
    ledstate["led2"]=0
    led2.value(0)
  if toggle == 6:
    print('Toggle pin2.')
    toggle_pin(2)
  if reset == 6:
    print('Sending reset signal..')
    data["status"]="Resetting"
    send_hw_push()
  if poweroff == 6:
    print('Sending poweroff signal..')
    data["status"]="Powering off."
    send_hw_push(5)
  if test == 6:
    data["status"]="Status message"

    
    
  response = web_page()
  conn.send('HTTP/1.1 200 OK\n')
  conn.send('Content-Type: text/html\n')
  conn.send('Connection: close\n\n')
  conn.sendall(response)
  conn.close()
  
