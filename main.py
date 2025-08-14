#IA-Geyser BASIC SERVER
# -- ONLY FOR 1 SERVER
# -- FOR MORE SERVER, USE IA-Geyser-Server-Queue for a queue based system
# Version 3.0
# GPL-3.0 license
# Revision Date: 01/08/2025
# Description: This is the basic server for IA-Geyser
# -- It will handle the connection to the client and the server
# -- It will handle the download of the pack
# -- It will handle the conversion of the pack ( Items )
# -- It will handle the temporary storage of the pack
# -- It will handle the sending of the pack download url to the plugin

#TODO: Implement WSS connection <-- Being worked on in this commit
#TODO: Implement Download Pack <-- Being worked on in the next commit
#TODO: Implement Kas-tle's Converter
#TODO: Implement Block/Entity Conversion

#Command format: W/ Args
#{
#  "command": "echo",
#  "args": {
#    "text": "This will be echoed back!"
#  }
#}

#Command format: W/o Args
#{
#  "command": "ping"
#}


import asyncio
import json
import logging
import websockets
import subprocess
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SimpleWebSocketServer:
    """Simple WebSocket server with basic command handling"""
    
    def __init__(self, host: str = 'localhost', port: int = 8765):
        self.host = host
        self.port = port
        self.clients = {}
        self.client_counter = 0
    
    async def handle_command(self, client_id: str, message: str) -> dict:
        """Handle incoming commands"""
        try:
            data = json.loads(message)
            command = data.get('command', '').lower()
            args = data.get('args', {})  # Get arguments from the message
            
            if command == 'ping':
                message_text = args.get('message', 'Server is alive!')
                return {
                    'command': 'pong',
                    'message': message_text,
                    'client_id': client_id,
                    'timestamp': datetime.now().isoformat()
                }
            elif command == 'pack':
                pack_name = args.get('name', 'Unknown Pack')
                pack_url = args.get('url', '')
                pack_size = args.get('size', 'unknown')
                # TODO: Run on Ubuntu 20.04 LTS WITH Java2Bedrock W/ Args, Note to brebs dumbass, YOU CANT RUN IT ON WINDOWS
                # Run test .bat TODO: Run actual shell script!
                pack_output = subprocess.run(['converttest.bat', ''], stdout=subprocess.PIPE)
                # Why the fuck does it output a byte?
                pack_output_string = pack_output.stdout.decode('utf-8')
                # Give the client the info of the pack TODO: Actually handle file downloads!
                return {
                    'command': 'pack',
                    'status': 'converting',
                    'message': f'Pack "{pack_name}" received!',
                    'client_id': client_id,
                    'timestamp': datetime.now().isoformat(),
                    'testout' : pack_output_string
                }
                # TODO: Add method for notification of pack conversion completion
                # TODO: Finish plugin side
            elif command == 'echo':
                text = args.get('text', 'No text provided')
                return {
                    'command': 'echo_response',
                    'message': text,
                    'client_id': client_id,
                    'timestamp': datetime.now().isoformat()
                }
            else:
                return {
                    'command': 'commanderror',
                    'error': f'Unknown command: {command}',
                    'client_id': client_id,
                    'timestamp': datetime.now().isoformat()
                }
                
        except json.JSONDecodeError:
            return {
                'command': 'jsonerror',
                'error': 'Invalid JSON format',
                'client_id': client_id,
                'timestamp': datetime.now().isoformat()
            }
    
    async def handle_client(self, websocket):
        """Handle individual client connections"""
        client_id = f"client_{self.client_counter:04d}"
        self.client_counter += 1
        
        self.clients[client_id] = websocket
        logger.info(f"Client {client_id} connected")
        
        try:
            # Send welcome message
            welcome_message = {
                'status': 'waiting',
                'version': 's1.0',
                'client_id': client_id,
                'timestamp': datetime.now().isoformat()
            }
            await websocket.send(json.dumps(welcome_message))
            
            # Handle incoming messages
            async for message in websocket:
                logger.info(f"Received from {client_id}: {message}")
                
                # Handle command
                response = await self.handle_command(client_id, message)
                
                # Send response back to client
                await websocket.send(json.dumps(response))
                logger.info(f"Sent to {client_id}: {response}")
                
        except websockets.exceptions.ConnectionClosed:
            logger.info(f"Client {client_id} disconnected")
        except Exception as e:
            logger.error(f"Error handling client {client_id}: {e}")
        finally:
            # Clean up
            if client_id in self.clients:
                del self.clients[client_id]
            logger.info(f"Client {client_id} cleanup completed")
    
    async def start_server(self):
        """Start the WebSocket server"""
        logger.info(f"Starting IA-Geyser WebSocket Server on {self.host}:{self.port}")
        
        async with websockets.serve(self.handle_client, self.host, self.port):
            logger.info(f"Server is running on ws://{self.host}:{self.port}")
            logger.info("Available commands: ping")
            
            # Keep the server running
            await asyncio.Future()  # Run forever

async def main():
    """Main function to start the server"""
    server = SimpleWebSocketServer()
    await server.start_server()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")

