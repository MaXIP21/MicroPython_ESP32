import time
import json
import network
import os
try:
    import webrepl
except ImportError:
    pass
try:
    import uasyncio as asyncio
except ImportError:
    pass
try:
    import logging
    log = logging.getLogger("wifi_manager")
except ImportError:
    def fake_log(msg, *args):
        print("[?] No logger detected. (log dropped)")
    log = type("", (), {"debug": fake_log, "info": fake_log, "warning": fake_log, "error": fake_log, "critical": fake_log})()

class wlan_control:
    def __init__(self):
        self.webrepl_triggered = False
        self._ap_start_policy = "never"
        self.config_file = "/flash/network.json"

    @classmethod
    def start_managing(self):
        loop = asyncio.get_event_loop()
        loop.create_task(self.manage())

    @classmethod
    async def manage(self):
        while True:
          status = self.wlan().status()
          if (status != network.STAT_GOT_IP) or \
          (self.wlan().ifconfig()[0] == '0.0.0.0'):  
              print("Network not connected: managing")
              self.setup_network()
          await asyncio.sleep(10)  
  
    @classmethod
    def wlan(self):
        return network.WLAN(network.STA_IF)
    @classmethod
    def get_ip(self):
      return self.wlan().ifconfig()[0]
      
    @classmethod
    def accesspoint(self):
        return network.WLAN(network.AP_IF)
    
    @classmethod
    def wants_accesspoint(self) -> bool:
        _ap_start_policy = "never"
        static_policies = {"never": False, "always": True}
        if _ap_start_policy in static_policies:
            return static_policies[_ap_start_policy]
        return self.wlan().status() != network.STAT_GOT_IP  
        
    @classmethod
    def load_config(self):
      try:
        with open("/flash/network.json", "r") as f:
            config = json.loads(f.read())
            self.preferred_networks = config['known_networks']
            self.ap_config = config["access_point"]
            if config.get("schema", 0) != 2:
                log.warning("Did not get expected schema [2] in JSON config.")
      except Exception as e:
        log.error("Failed to load config file, no known networks selected ")
        print(e)
        self.preferred_networks = []
        return
    
    def list_available_networks(self):
      self.available_networks = []
      for network in self.wlan().scan():
          ssid = network[0].decode("utf-8")
          bssid = network[1]
          strength = network[3]
          self.available_networks.append(dict(ssid=ssid, bssid=bssid, strength=strength))
      self.available_networks.sort(key=lambda station: station["strength"], reverse=True)
        
    def setup_network(self) -> bool:
        self.load_config()
        self.webrepl_triggered = False  
        self.wlan().active(True)
        self.list_available_networks()

        candidates = []
        for aPreference in self.preferred_networks:
            for aNetwork in self.available_networks:
                if aPreference["ssid"] == aNetwork["ssid"]:
                    connection_data = {
                        "ssid": aNetwork["ssid"],
                        "bssid": aNetwork["bssid"],  
                        "password": aPreference["password"],
                        "enables_webrepl": aPreference["enables_webrepl"]}
                    candidates.append(connection_data)
    
        for new_connection in candidates:
            print("Attempting to connect to network {0}...".format(new_connection["ssid"]))
            if self.connect_to(ssid=new_connection["ssid"], password=new_connection["password"], bssid=new_connection["bssid"]):
                print("Successfully connected {0}".format(new_connection["ssid"]))
                self.webrepl_triggered = new_connection["enables_webrepl"]
        
        self._ap_start_policy = self.ap_config.get("start_policy", "never")
        should_start_ap = self.wants_accesspoint()
        self.accesspoint().active(should_start_ap)
        if should_start_ap:  
            print("Enabling your access point...")
            self.accesspoint().config(**self.ap_config["config"])
            self.webrepl_triggered = self.ap_config["enables_webrepl"]
        self.accesspoint().active(self.wants_accesspoint())  

        if self.webrepl_triggered:
            try:
                webrepl.start()
                print("webrepl started.")
            except NameError:
                print("Failed to start webrepl, module is not available.")
        return self.wlan().isconnected()

    @classmethod
    def connect_to(self, ssid, password, bssid) -> bool:
        self.wlan().connect(ssid, password)
        for check in range(0, 10):  
            if self.wlan().isconnected():
                return True
            time.sleep_ms(500)
        return False