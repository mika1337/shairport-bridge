#!/usr/bin/python

# =============================================================================
# Builtin imports
import logging
import logging.config
import traceback

# =============================================================================
# Other imports
import paho.mqtt.client as mqtt

cmd_topic_list = ("command","beginff","beginrew","mutetoggle","nextitem","previtem","pause","playpause","play","stop","playresume","shuffle_songs","volumedown","volumeup")

# =============================================================================
# Classes
class ShairportSyncMQTT:
    _event_topics = ("active_start", "active_end", "play_start", "play_end", "play_flush", "play_resume")
    _player_topics = ("volume", "client_ip")
    _track_topics = ("artist", "album", "title", "genre","songalbum","cover")
    _subscribed_topics = _event_topics + _player_topics + _track_topics

    def __init__(self,handler,topic_root="shairport-sync/rpih1",host="localhost",port=1883):
        self._handler = handler
        self._topic_root = topic_root
        self._host = host
        self._port = port

        self._mttqc = mqtt.Client()
        self._mttqc.on_connect = self._onConnect
        self._mttqc.on_message = self._onMessage

    def start(self):
        self._mttqc.connect( self._host, port=self._port )
        self._mttqc.loop_start()

    def _onConnect(self,client, userdata, flags, rc):
        logging.debug("on_connect(userdata={},flags={},rc={}".format(userdata,flags,rc))

        # Subscribe topics
        for topic in self._subscribed_topics:
            topic_full_name = self._getTopicFullName(topic)
            (result,msg_id) = client.subscribe(topic_full_name,1)
            logging.debug(" > subscribed topic \"{}\" => {}/{}".format(topic_full_name,result,msg_id))

    def _onMessage(self,client, userdata, message):
        try:
            topic = self._getTopicShortName(message.topic)

            if topic in self._event_topics:
                logging.debug("Player event: {} ({})".format(topic, message.payload))
                self._handler.onShairportSyncPlayerEvent(topic)

            elif topic in self._player_topics:
                logging.debug("Player update: {} ({})".format(topic, message.payload))
                self._handler.onShairportSyncPlayerStateUpdate(topic,message.payload)

            elif topic in self._track_topics:
                if topic == "cover":
                    logging.debug("Track data: {}".format(topic))
                else:
                    logging.debug("Track data: {} ({})".format(topic,message.payload))
                self._handler.onShairportSyncTrackUpdate(topic,message.payload)

            else:
                logging.debug("Unhandled topic: {} ({})".format(topic,message.payload))
        except:
            logging.error( "Exception in _onMessage: %s" % traceback.format_exc() )


    def _getTopicShortName(self,topic_full_name):
        if topic_full_name.find(self._topic_root) != 0:
            logging.error("Unexpected topic root: {} (expected to begin with {})".format(topic_full_name,self._topic_root))
            return None
        
        return topic_full_name[len(self._topic_root)+1:]

    def _getTopicFullName(self, topic):
        return self._topic_root + "/" + topic