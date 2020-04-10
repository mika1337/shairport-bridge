#!/usr/bin/env python3

# =============================================================================
# Builtin imports
import logging
import logging.config
import traceback
from base64    import b64encode
from threading import Lock,Timer

# =============================================================================
# Other imports
from utils.shairportSyncMqtt import ShairportSyncMQTT
from utils.websocketServer   import WebSocketServer

# =============================================================================
# Class
class ShairportBridge:
    # Note: only process play_start and play_end as others are unreliable
    _state_from_player_event = { "play_start": "playing"
                               , "play_end": "stopped" }
    _track_cover_timer_duration = 0.25

    def __init__(self,ws_port):
        self._ws_port = ws_port
        self._wss = WebSocketServer(self,1234)
        self._ssm = ShairportSyncMQTT(self)

        self._player_data = dict()
        self._player_data["player"] = dict()
        self._player_data["player"]["state"] = "stopped"

        self._track_data = dict()
        self._track_data["track"] = dict()

        self._cover_data = dict()
        self._cover_data["cover"] = dict()
        self._cover_data["cover"]["mimetype"] = ""
        self._cover_data["cover"]["data"] = ""

        self._track_cover_data_lock = Lock()
        self._track_cover_update_list = set()
        self._track_cover_update_timer = None

    def start(self):
        self._ssm.start()
        self._wss.start()

    def onWebSocketNewConnection(self,arg):
        try:
            logging.debug("New websocket connection")
            self._wss.sendToClient(self._player_data,arg)
            self._wss.sendToClient(self._track_data,arg)
            self._wss.sendToClient(self._cover_data,arg,log=False)
        except:
            logging.error( "Exception in onWebSocketNewConnection: %s" % traceback.format_exc() )

    def onShairportSyncPlayerEvent(self,event):
        if event in self._state_from_player_event:
            state = self._state_from_player_event[event]
            if self._player_data["player"]["state"] != state:
                self._player_data["player"]["state"] = state
                self._wss.sendToClients(self._player_data)

    def onShairportSyncPlayerStateUpdate(self,event,param):
        pass

    def onShairportSyncTrackUpdate(self,data,param):
        self._track_cover_data_lock.acquire()

        if self._track_cover_update_timer != None:
            self._track_cover_update_timer.cancel()
            self._track_cover_update_timer = None

        try:
            if data != "cover":
                value = param.decode("utf-8")
                if data not in self._track_data["track"] or self._track_data["track"][data] != value:
                    self._track_data["track"][data] = value
                    self._track_cover_update_list.add("track_data")
            else:
                if data:
                    mime_type = self._guessImageMime(param)
                    b64_cover = b64encode(param).decode("utf-8")

                    if self._cover_data["cover"]["data"] != b64_cover:
                        self._cover_data["cover"]["mimetype"] = mime_type
                        self._cover_data["cover"]["data"] = b64_cover
                        self._track_cover_update_list.add("cover_data")
        except:
            logging.error( "Exception in onShairportSyncTrackUpdate: %s" % traceback.format_exc() )
        
        self._track_cover_update_timer = Timer(self._track_cover_timer_duration,self._onTrackCoverTimerEnd)
        self._track_cover_update_timer.start()

        self._track_cover_data_lock.release()

    def _onTrackCoverTimerEnd(self):
        self._track_cover_data_lock.acquire()

        for data in self._track_cover_update_list:
            if data == "track_data":
                self._wss.sendToClients(self._track_data)
            elif data == "cover_data": 
                self._wss.sendToClients(self._cover_data,log=False)

        self._track_cover_update_list.clear()
        self._track_cover_update_timer = None
        self._track_cover_data_lock.release()


    def _guessImageMime(self,magic):
        if magic.startswith(b"\xff\xd8"):
            return "image/jpeg"
        elif magic.startswith(b"\x89PNG\r\n\x1a\r"):
            return "image/png"
        else:
            return "image/jpg"

# =============================================================================
# Main
if __name__ == '__main__':
    logging.config.fileConfig("logging.conf")
    logging.info("Shairport bridge starting")

    sb = ShairportBridge(1234)
    sb.start()

    logging.info("Shairport bridge stopping")
