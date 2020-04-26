# =============================================================================
# System imports
import logging
import asyncio
import websockets
import json

# =============================================================================
# Logger setup
logger = logging.getLogger(__name__)

# =============================================================================
# Classes
class WebSocketServer:
    def __init__(self,handler,port):
        self._handler = handler
        self._port = port
        self._connections = set()

    def start(self):
        start_server = websockets.serve(self._newConnection, port=self._port)

        self._event_loop = asyncio.get_event_loop()
        self._event_loop.run_until_complete(start_server)
        self._event_loop.run_forever()

    def sendToClient(self,data,websocket,log=True):
        if log:
            logger.debug('Sending {} to 1 client'.format(data))

        payload = json.dumps( data )
        self._syncRunCoroutine(websocket.send(payload))

    def sendToClients(self,data,log=True):
        if log:
            logger.debug('Sending {} to {} client(s)'.format(data,len(self._connections)))
        else:
            logger.debug('Sending data to {} client(s)'.format(len(self._connections)))

        payload = json.dumps( data )
        for websocket in self._connections:
            try:
                self._syncRunCoroutine(websocket.send(payload))
            except:
                endpoint = '{}:{}'.format(websocket.remote_address[0],websocket.remote_address[1])
                logger.exception( 'Failed to send data to '+endpoint+':')

    def _syncRunCoroutine(self,coro):
        try:
            asyncio.get_event_loop()
        except RuntimeError:
            asyncio.run(coro)
        else:
            asyncio.create_task(coro)

    async def _newConnection(self,websocket, path):
        endpoint = '{}:{}'.format(websocket.remote_address[0], websocket.remote_address[1])
        logger.info('New connection from {}'.format(endpoint))

        await self._register(websocket)
        self._handler.onWebSocketNewConnection(websocket)

        try:
            async for message in websocket:
                logger.debug('Data received from {}: {}'.format(endpoint,message))
        finally:
            logger.info('{} disconnected'.format(endpoint))
            await self._unregister(websocket)

    async def _register(self,websocket):
        self._connections.add(websocket)
    
    async def _unregister(self,websocket):
        self._connections.remove(websocket)
