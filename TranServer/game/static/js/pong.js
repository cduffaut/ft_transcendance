document.title = "Pong Game";

/*##################################################################*|
#                                                                    #
#    <---------------------------------------------------------->    #
#    |                      Settings Code                       |    #
#    <---------------------------------------------------------->    #
#                                                                    #
\*##################################################################*/

if (typeof window.Settings === "undefined") {
	window.Settings = class Settings
	{
		constructor(rawSettings){
			var data = JSON.parse(rawSettings);
			this.nbPlayers = data.nbPlayers || 2; // number of players in the game
			this.playersNames = data.users && data.users.length > 0 ? data.users : Array.from({ length: this.nbPlayers }, (_, index) => `User${index + 1}`);
			this.isSolo = data.isSolo; // if no other players on other screens
			this.status = data.status || "waiting"; // if the game is running
			this.winPoints = data.winPoints || 10;

			this.gameWidth = data.gameWidth || 1200; // width of the field
			this.gameHeight = this.gameWidth; // height of the field
			if (this.nbPlayers != 4)
				this.gameHeight /= 2; // field is square if 4 players, else it's a rectangle so we divide the height by 2

			fetch('/api/colors/')
				.then(response => response.json())
				.then(data => {
					this.paddleColor = data.paddle_color || "white"; // color of the paddles
					this.ennemiColor = data.enemy_paddle_color || "red"; // color of the ennemies
					this.ballColor = data.ball_color || "white"; // color of the ball
					this.fieldColor = data.background_color || "#000"; // color of the field
					this.borderColor = data.frame_color || "white"; // color of the border
				});

			this.paddleWidth = data.paddleWidth || 0.02; // width of the paddles
			this.paddleLength = data.paddleLength || 0.2; // length of the paddles
			this.paddleOffset = data.paddleOffset || 0.02; // offset of the paddles from the border
		
			this.ballSize = data.ballSize || 0.03; // size of the ball
			this.ballPosition = { x: 0, y: 0 }; // position of the ball
			this.userName = data.user;
			if (this.isSolo && this.nbPlayers === 2)
				this.userID = 1;
			else if (data.users)
				this.userID = this.playersNames.indexOf(this.userName) + 1;
			else
				this.userID = 1;
			this.gameID = data.gameid;
			this.tournamentid = data.tournamentid;

			if (this.userID == 0)
				this.userID = 1;
		}
	}
}

/*##################################################################*|
#                                                                    #
#    <---------------------------------------------------------->    #
#    |                        Player Code                       |    #
#    <---------------------------------------------------------->    #
#                                                                    #
\*##################################################################*/

if (typeof window.Player === "undefined") {
	window.Player = class Player
	{
		constructor(PlayerID, PlayerName, gameParams){
			this.PlayerID = PlayerID || 1; // 1, 2, 3 our 4
			this.PlayerName = PlayerName || "bob"; // eg "BarnabéEnculeurDeMouches"
			this.Points = 0; // Points scored by the player
			this.Position = 0; // from -0.5 to 0.5, represents pos on the paddle slider
			this.keysPressed = {}; // stores keys status (pressed/released) for up and down
			this.gameParams = gameParams; // game settings	
		}

		// store current keys status (pressed/released)
		updateKeysPressed(event, value, ws){
			if (event.key != "w" && event.key != "s" && event.key != "W" && event.key != "S" &&event.key != "ArrowUp" && event.key != "ArrowDown")
				return;
			var message = "";
			if ((event.key == "ArrowUp" || event.key == "ArrowDown") && this.gameParams.isSolo && this.gameParams.nbPlayers == 2 && this.PlayerID == 2)
			{
				if (event.key == "ArrowUp" && this.keysPressed["up"] != value) {
					this.keysPressed["up"] = value;
					message = this.PlayerID + "u-" + (value == true ? "on" : "off");
				}
				else if (event.key == "ArrowDown" && this.keysPressed["down"] != value) {
					this.keysPressed["down"] = value;
					message = this.PlayerID + "d-" + (value == true ? "on" : "off");
				}
			} else {
				if (this.PlayerID == 1  || this.PlayerID == 4 || (this.gameParams.isSolo && this.gameParams.nbPlayers == 2))
				{
					if ((event.key == "w" || event.key == "W") && this.keysPressed["up"] != value) {
						this.keysPressed["up"] = value;
						message = this.PlayerID + "u-" + (value == true ? "on" : "off");
					}
					else if ((event.key == "s" || event.key == "S") && this.keysPressed["down"] != value) {
						this.keysPressed["down"] = value;
						message = this.PlayerID + "d-" + (value == true ? "on" : "off");
					}
				}
				else
				{
					if ((event.key == "w" || event.key == "W") && this.keysPressed["up"] != value) {
						this.keysPressed["up"] = value;
						message = this.PlayerID + "d-" + (value == true ? "on" : "off");
					}
					else if ((event.key == "s" || event.key == "S") && this.keysPressed["down"] != value) {
						this.keysPressed["down"] = value;
						message = this.PlayerID + "u-" + (value == true ? "on" : "off");
					}
				}
			}
			if (ws && message != "")
				ws.send(message);
		}

		// rotate if needed to put player on the left side of the screen
		applyRotation(canvasContext){
			if (this.PlayerID == 1)
				return;
			canvasContext.save(); // Save the current state
			canvasContext.translate(this.gameParams.gameWidth / 2, this.gameParams.gameHeight / 2); // Move to the center of the canvas
			if (this.PlayerID == 2)
				canvasContext.rotate(Math.PI); // Rotate 180 degrees
			else if (this.PlayerID == 3)
				canvasContext.rotate(-Math.PI / 2); // Rotate 90 degrees
			else if (this.PlayerID == 4)
				canvasContext.rotate(Math.PI / 2); // Rotate -90 degrees
			canvasContext.translate(-this.gameParams.gameWidth / 2, -this.gameParams.gameHeight / 2); // Move back to the original position
		}

		// draw the player's paddle with updated data
		updateStatus(newPosition, newPoints){
			this.Position = newPosition;
			this.Points = newPoints;
		}

		// draw the player's paddle
		draw(canvasContext){
			// Calculate the real position of the paddle
			var realPaddlePos = (this.gameParams.gameHeight * (this.Position * -1 + 0.5)) - (this.gameParams.paddleLength / 2);
			canvasContext.fillStyle = this.gameParams.paddleColor;
			if (this.PlayerID != settings.userID)
				canvasContext.fillStyle = this.gameParams.ennemiColor;

			var x, y, width, height;

			if (this.PlayerID < 3) {
				width = this.gameParams.paddleWidth * this.gameParams.gameHeight;
				height = this.gameParams.paddleLength * this.gameParams.gameHeight;
			} else {
				width = this.gameParams.paddleLength * this.gameParams.gameHeight;
				height = this.gameParams.paddleWidth * this.gameParams.gameHeight;
			}

			// Calculate the position and size based on PlayerID
			if (this.PlayerID === 1) {
				x = this.gameParams.paddleOffset * this.gameParams.gameHeight;
				y = realPaddlePos - this.gameParams.paddleLength * this.gameParams.gameHeight / 2;
			} else if (this.PlayerID === 2) {
				x = this.gameParams.gameWidth - this.gameParams.paddleWidth * this.gameParams.gameHeight - this.gameParams.paddleOffset * this.gameParams.gameHeight;
				y = realPaddlePos - this.gameParams.paddleLength * this.gameParams.gameHeight / 2;
			} else if (this.PlayerID === 3) {
				x = realPaddlePos - this.gameParams.paddleLength * this.gameParams.gameHeight / 2;
				y = this.gameParams.paddleOffset * this.gameParams.gameHeight;
			} else if (this.PlayerID === 4) {
				x = realPaddlePos - this.gameParams.paddleLength * this.gameParams.gameHeight / 2;
				y = this.gameParams.gameHeight - this.gameParams.paddleWidth * this.gameParams.gameHeight - this.gameParams.paddleOffset * this.gameParams.gameHeight;
			}
		
			// Draw the paddle with the calculated dimensions
			canvasContext.fillRect(x, y, width, height);
		}
	}
}


/*##################################################################*|
#                                                                    #
#    <---------------------------------------------------------->    #
#    |                      Main Pong Code                      |    #
#    <---------------------------------------------------------->    #
#                                                                    #
\*##################################################################*/

var settings;
var players;
var canvas, CanvasContext;
var scoreBoard;
var nbPaddles = 2;

function setGameSize() {
	if (window.innerHeight < window.innerWidth)
		settings.gameWidth = window.innerHeight * 0.9;
	else
		settings.gameWidth = window.innerWidth * 0.9;
	settings.gameHeight = settings.gameWidth;
	if (settings.nbPlayers !== 4)
		settings.gameHeight /= 2;
}	

function sleep(milliseconds) {
    return new Promise(resolve => setTimeout(resolve, milliseconds));
}


/*‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾*\
||===========================[game drawing]=========================||
\*__________________________________________________________________*/
async function drawGame() {
	// Adjust canvas size
	canvas.width = settings.gameWidth;
	canvas.height = settings.gameHeight;
	// If playerID is 'j2', rotate the canvas for the player's perspective
	players[settings.userID - 1].applyRotation(CanvasContext);

	// Draw field
	CanvasContext.fillStyle = settings.fieldColor;
	CanvasContext.fillRect(0, 0, settings.gameWidth, settings.gameHeight);
	// Add field border
	CanvasContext.strokeStyle = settings.borderColor;
	CanvasContext.lineWidth = settings.gameWidth / 75;
	CanvasContext.strokeRect(0, 0, settings.gameWidth, settings.gameHeight);
	//draw paddles
	for (var i = 0; i < nbPaddles; i++)
		players[i].draw(CanvasContext);
	// Draw ball
	CanvasContext.fillStyle = settings.ballColor;
	CanvasContext.beginPath();
	CanvasContext.arc(settings.gameWidth * (settings.ballPosition.x + 0.5),  settings.gameHeight * (settings.ballPosition.y + 0.5), settings.ballSize * settings.gameHeight / 2, 0, Math.PI * 2);
	CanvasContext.fill();

	// Restore the original state if the canvas was rotated for player 2
	if (settings.userID === '2' || settings.userID === '3' || settings.userID === '4')
		CanvasContext.restore();
	// relative positions of players repending on the playerID (if player 1, we use positions[0(playerID - 1)])
	var positions = [ [1, 2, 3], [0, 3, 2], [3, 1, 0], [2, 0, 1]];
	// Select the right positions for the player
	var [pRight, pTop, pBottom] = positions[settings.userID - 1];

	if (settings.status == "playing")
	{
		document.getElementById('waitingScreen').style.display = 'none';
		document.getElementById('endGameScreen').style.display = 'none';
		// Display the score for 2 players
		if (nbPaddles === 2)
			scoreBoard.innerHTML = `${settings.playersNames[settings.userID - 1]}: ${players[settings.userID - 1].Points} - ${settings.playersNames[pRight]}: ${players[pRight].Points}`;
		else { // Display the score for 4 players
			scoreBoard.innerHTML = `${settings.playersNames[pTop]}: ${players[pTop].Points}<br>`;
			scoreBoard.innerHTML += `${settings.playersNames[settings.userID - 1]}: ${players[settings.userID - 1].Points} - ${settings.playersNames[pRight]}: ${players[pRight].Points}<br>`;
			scoreBoard.innerHTML += `${settings.playersNames[pBottom]}: ${players[pBottom].Points}`;
		}
	}

	// Display waiting screen or end game screen depending on the game status
	if (settings.status == "waiting")
	{
		document.getElementById('endGameScreen').style.display = 'none';
		document.getElementById('waitingScreen').style.display = 'block';
	}
	if (settings.status == "game_over")
	{
		document.getElementById('waitingScreen').style.display = 'none';
		var winner = 'le Prince de LU';
		var highestScore = 0;
		for (var i = 0; i < nbPaddles; i++)
		{
			if (players[i].Points > highestScore)
			{
				winner = settings.playersNames[i];
				highestScore = players[i].Points;
			}
		}
		document.getElementById('winnerText').textContent = 'Winner: ' + winner;
		var score = '';
		for (var i = 0; i < nbPaddles; i++)
			score += settings.playersNames[i] + ': ' + players[i].Points + " <br> ";
  		document.getElementById('scoreText').innerHTML = score;
		document.getElementById('endGameScreen').style.display = 'block';	
		await sleep(4000);
		var pageToFetch = "/dashboard/";
		if (settings.tournamentid != undefined && settings.tournamentid != null && settings.tournamentid != 0)
			pageToFetch = "/tournament/" + settings.tournamentid + "/";
		window.history.pushState(null, null, pageToFetch);
		fetchPage(pageToFetch);
}}


/*‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾*\
||=====================[Context initialisation]=====================||
\*__________________________________________________________________*/
var container = document.createElement('div');
// Container for canvas and scoreboard
document.body.appendChild(container); 
container.style.display = 'flex'; container.style.flexDirection = 'column'; container.style.alignItems = 'center';
canvas = document.getElementById('pongCanvas');
// Add the canvas to the container
container.appendChild(canvas); 
CanvasContext = canvas.getContext('2d');
// Creating a separate scoreboard
scoreBoard = document.createElement('div');
// Insert scoreboard above canvas in the container
container.insertBefore(scoreBoard, canvas); 
// Styling the scoreboard
scoreBoard.style.textAlign = 'center'; scoreBoard.style.fontSize = '20px'; scoreBoard.style.color = 'white'; scoreBoard.style.marginBottom = '10px';


/*‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾*\
||====================[variables initialisation]====================||
\*__________________________________________________________________*/
// Initialize game settings and players
var rawSettings = document.getElementById("gameSettings").getAttribute('data-gameSettings');
settings = new Settings(rawSettings);
if (settings.nbPlayers > 2)
	nbPaddles = 4;
players = [nbPaddles];
for (var i = 0; i < nbPaddles; i++)
	players[i] = new Player(i + 1, settings.playersNames[i], settings);
setGameSize()


/*‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾*\
||====================[websocket communication]=====================||
\*__________________________________________________________________*/
// WebSocket setup
var ws;
var attemptDuration = 10000;
var attemptInterval = 500;
var startTime = Date.now();

async function connectWebSocket() {
	document.getElementById('waitingMessage').textContent = "Game loading...";
	await sleep(3000); 
	var url = 'wss://' + window.location.host + '/wsGame/' + settings.gameID + '/' + settings.userName + '/';
	ws = openWebSocket(url);
	while (ws.readyState !== ws.OPEN) {
		ws.close();
		closeAllWebSockets();
		if (!document.getElementById('waitingScreen'))
			return;
		await sleep(3000);
		ws = openWebSocket(url);
		if (ws.readyState !== ws.OPEN)
			await sleep(3000);
	}
	document.getElementById('waitingMessage').textContent = "Waiting for players...";
	

	ws.onopen = () =>
		{console.log("WebSocket connection established.");};
	ws.onmessage = (event) => {
		// parsing
		if (!document.getElementById('waitingScreen'))
			ws.close();
		var data = JSON.parse(event.data);
		if (data.users)
		{
			settings.playersNames = data.users;
			if (settings.isSolo && settings.nbPlayers == 2)
				settings.userID = 1;
			else
				settings.userID = settings.playersNames.indexOf(settings.userName) + 1;
			if (settings.userID == 0)
				settings.userID = 1;
		}
		settings.status = data.state;
		// ball update
		settings.ballPosition = { x: data.ballx, y: -1 * data.bally };
		// update players
		for (var i = 0; i < nbPaddles; i++)
			players[i].updateStatus(data[`p${i + 1}`], data[`score${i + 1}`]);
		drawGame();
	};
	ws.onclose = (event) => {
		if (!event.wasClean) {
		  console.log(`WebSocket closed with event code ${event.code}, retrying...`);
		  let currentTime = Date.now();
		  let elapsedTime = currentTime - startTime;
		  if (elapsedTime < attemptDuration) {
			setTimeout(connectWebSocket, attemptInterval);
		  } else {
			console.log("Stopped attempting to reconnect WebSocket after 10 seconds.");
		  }
		}
	};
	ws.onerror = (error) =>
		{console.log("WebSocket error: ", error);};
}
// Establish WebSocket connection
connectWebSocket();


/*‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾*\
||=========================[input managment]========================||
\*__________________________________________________________________*/
// Event listeners for key presses
document.addEventListener('keydown', (event) => {
	if (settings.status !== "playing")
		return;
	players[settings.userID - 1].updateKeysPressed(event, true, ws);
	if (settings.isSolo == true && settings.nbPlayers == 2 && event.key == "ArrowUp" || event.key == "ArrowDown")
		players[1].updateKeysPressed(event, true, ws);
});
// Event listeners for key releases
document.addEventListener('keyup', (event) => {
	players[settings.userID - 1].updateKeysPressed(event, false, ws); // Update keysPressed for the player
	if (settings.isSolo && settings.nbPlayers == 2)
		players[1].updateKeysPressed(event, false, ws); // Update keysPressed for the other player if in 1v1 singlescreen
});
drawGame();

// Adjust canvas size on window resize
window.addEventListener('resize', () => {
	if (!document.getElementById('waitingScreen'))
		return ;
	setGameSize();
	drawGame();
});
