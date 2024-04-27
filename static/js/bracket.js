document.title = "Tournament";

function sleep(milliseconds) {
    return new Promise(resolve => setTimeout(resolve, milliseconds));
}

if (typeof window.Match === "undefined") {
    window.Match = class Match {
		constructor(level, pos, ...players) {
			this.level = level;
			this.pos = pos;
			this.players = players;
			this.scores = new Array(players.length).fill(0);
			this.isRunning = false; // "live", "finished", "to be played"
			this.gameLink = "";
		}

		updateScores(...scores) {
			this.scores = scores;
		}

		setFinished() {
			this.isRunning = false;
		}

		setLive(gameLink) {
			this.isRunning = true;
			this.gameLink = gameLink;
		}

		updateFromData(data) {
			// Update the match data from the server
			this.players = [];
			this.scores = [];
		
			for (var i = 0; i <= 3; i++) {
				var playerKey = `player${i}Id`;
				if (data[playerKey] !== undefined) {
					this.players.push(data[playerKey]);
					var scoreKey = `score${i}`;
					this.scores.push(data[scoreKey] !== undefined ? data[scoreKey] : 0);
				}
				else if (i == 0){
					this.players.push("waiting for players");
					this.scores.push(0);
				}
			}
			this.isRunning = data.isRunning;
			this.gameLink = data.gameId;
		}
		
		

		generateHTML() {
			var matchElement;

			if (this.isRunning)
				this.status = "playing";
			else if (this.scores.some(score => score !== 0))
				this.status = "finished";
			else
				this.status = "waiting";
		
			// Create a link to the game if the match is running
			if (this.isRunning == true && this.gameLink) {
				matchElement = document.createElement('a');
				matchElement.href = `/game/${this.gameLink}/`;
				matchElement.classList.add('match-link');
			} else
				matchElement = document.createElement('div');
		
			var statusClass = this.status.replace(/\s+/g, '-').toLowerCase();
			matchElement.classList.add('match', statusClass);
			matchElement.setAttribute('data-id', this.pos);
			matchElement.setAttribute('data-level', this.level);
		
			// Find the winner index if the match is finished
			var winnerIndex = -1;
			if (this.status === "finished") {
				var winnerScore = Math.max(...this.scores);
				winnerIndex = this.scores.indexOf(winnerScore);
			}
			this.players.forEach((player, index) => {
				var playerElement = document.createElement('div');
				playerElement.classList.add('team');
				// Add the 'winner' or 'loser' class to the player element to change its style
				if (this.status === "finished") {
					if (index === winnerIndex)
						playerElement.classList.add('winner');
					else
						playerElement.classList.add('loser');
				}
				// Add the 'match-top' or 'match-bottom' class to the player element to have appropriate border radius
				if (index === 0 && index === this.players.length - 1)
					playerElement.classList.add('match-unique');
				else if (index === 0)
					playerElement.classList.add('match-top');
				else if (index === this.players.length - 1)
					playerElement.classList.add('match-bottom');
		
				playerElement.innerHTML = `
					<span class="name">${player}</span>
					<span class="score">${this.scores[index]}</span>
				`;
				matchElement.appendChild(playerElement);
			});
			return matchElement;
		}		
	}
}


var myUser = document.getElementById("myUser").getAttribute('data-myUser');
var isFull = false;
var tournamentSizeString = document.getElementById("tour_size").getAttribute('data-tournamentSize');
var tournamentSize = JSON.parse(tournamentSizeString);
var matchesMap = {}; // Store all matches by unique key (level-pos)


var dataTemplate ={
	pos: 1, // position in the round (1, 2, 3, 4, 5, 6, 7, 8, 9, 10)
	level: 0, // tournament round (..., quarterfinals, semifinals, finals)
	player1Id: "J7", // player display name
	player2Id: "J8",
	player3Id: "J9",
	player4Id: "J10",
	score1: 6, // player score
	score2: 9,
	score3: 6,
	score4: 9,
	isRunning: true, // match status (true, false)
	gameId: "" // to build game path https://sitename/game/gameId/
};


// tournament initialization
function initializeTournament(tournamentSize) {
	var bracketContainer = document.getElementById('tournamentBracket');
	bracketContainer.innerHTML = '';

	tournamentSize.forEach((size, index) => {
		var column = document.createElement('div');
		column.classList.add('column');
		column.setAttribute('data-level', index);

		for (var matchIndex = 0; matchIndex < size; matchIndex++) {
			var match = new Match(index, matchIndex + 1, "Waiting for players...");
			matchesMap[`${index}-${matchIndex + 1}`] = match;
			column.appendChild(match.generateHTML());
		}
		bracketContainer.appendChild(column);
	});
}


async function updateTournament(data) {
	var redirection = false;
	if (data.tournamentFull == true)
		isFull = true;
	if (isFull == true)
		document.getElementById('join-button').style.display = 'none';
	var updatedMatches = data.games;

	for (var key in updatedMatches) {
		var matchData = updatedMatches[key];
		var matchKey = `${matchData.level}-${matchData.pos}`;
		var existingMatch = matchesMap[matchKey];
		if (existingMatch) {
			existingMatch.updateFromData(matchData);
			// Replace the existing match HTML with the updated one
			var matchElement = document.querySelector(`.match[data-id="${matchData.pos}"][data-level="${matchData.level}"]`);
			if (matchElement)
				matchElement.replaceWith(existingMatch.generateHTML());
			if (isFull == false){
				for (var i = 0; i <= 3; i++) {
					var playerIdKey = `player${i}Id`;
					if (matchData[playerIdKey] && matchData[playerIdKey] === myUser)
						document.getElementById('join-button').style.display = 'none';
			}}
			if (matchData.isRunning == true) {
				for (var i = 0; i <= 3; i++) {
					var playerIdKey = `player${i}Id`;
					if (matchData[playerIdKey] && matchData[playerIdKey] === myUser && redirection == false) {
						redirection = true;
						var pageToFetch = "/game/" + matchData.gameId + "/";
					}
	}}}}
	if (redirection == true){
		window.history.pushState(null, null, pageToFetch);
		await sleep(3000);
		fetchPage(pageToFetch);
		return ;
	}
}


document.getElementById('join-button').addEventListener('click', function() {
	var baseUrl = window.location.href; 
	var joinUrl = `${baseUrl}join/`;
	fetch(joinUrl, { method: 'GET' });
});


// WebSocket setup
function setupWebSocket() {
	var pathElements = window.location.pathname.split('/');
	console.log('wss://' + window.location.host + '/ws/tournament/' + pathElements[2] + '/');
	var socket = new WebSocket('wss://' + window.location.host + '/ws/tournament/' + pathElements[2] + '/');

	socket.onopen = function(event) {
		console.log('WebSocket connection established');
	};
	socket.onmessage = function(event) {
		var dataPouet = JSON.parse(event.data);
		updateTournament(dataPouet);
	};
	socket.onerror = function(event) {
		console.error('WebSocket error:', event);
	};
	socket.onclose = function(event) {
		console.log('WebSocket connection closed');
	};
}


initializeTournament(tournamentSize); // Initialize the tournament bracket
setupWebSocket(); // Setup the WebSocket connection
