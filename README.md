# pacman
An A-Level computer science project archive.

Multiplayer Pacman. One player controls Pacman and the other player controls a Ghost. 
Pacman's goal is to collect every pellet, while the Ghost's goal is to stop Pacman by eating them.

This repo contains prototype code (version 1 and version 2) as well as the final game (version 3).

To play the game:
1. Clone the repo
2. Connect both devices to the same Wi-Fi network.
3. One device runs version_3_server.py and version_3.py, while the other device runs version_3.py.
4. Input the IP address and port number from the server output window into each client to connect to the lobby.
5. Once both clients are connected to the server, the character selection page will load.
6. Once both clients have chosen their character, the game will start.

Additional mazes can be added!
Make a text file with the layout of the maze, using "o" to symbolise a pellet and "x" to symbolise a wall. Use any other character to represent a blank cell.
Then append the name of the new maze file to the mazes array inside of the create_maze function on line 413. Make sure to save the maze text file in the same directory as the game!
