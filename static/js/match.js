 class Match {
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
		// Réinitialiser les joueurs et les scores basés sur les données reçues
		this.players = [];
		this.scores = [];
	
		for (let i = 0; i <= 3; i++) {
			const playerKey = `player${i}Id`;
			if (data[playerKey] !== undefined) {
				this.players.push(data[playerKey]);
				const scoreKey = `score${i}`;
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
		let matchElement;

		if (this.isRunning)
			this.status = "playing";
		else if (this.scores.some(score => score !== 0))
			this.status = "finished";
		else
			this.status = "waiting";
	
		// Crée un élément <a> ou <div> comme conteneur principal selon le statut du match
		if (this.isRunning == true && this.gameLink) {
			matchElement = document.createElement('a');
			matchElement.href = `/game/${this.gameLink}/`;
			matchElement.classList.add('match-link');
		} else {
			matchElement = document.createElement('div');
		}
	
		const statusClass = this.status.replace(/\s+/g, '-').toLowerCase();
		matchElement.classList.add('match', statusClass);
		matchElement.setAttribute('data-id', this.pos);
		matchElement.setAttribute('data-level', this.level);
	
		// Déterminer l'index du gagnant et traiter tous les autres comme perdants si le match est terminé
		let winnerIndex = -1;
		if (this.status === "finished") {
			const winnerScore = Math.max(...this.scores);
			winnerIndex = this.scores.indexOf(winnerScore);
		}
	
		this.players.forEach((player, index) => {
			const playerElement = document.createElement('div');
			playerElement.classList.add('team');
			// Appliquer la classe 'winner' au gagnant, 'loser' aux autres si le match est terminé
			if (this.status === "finished") {
				if (index === winnerIndex) {
					playerElement.classList.add('winner');
				} else {
					playerElement.classList.add('loser');
				}
			}
	
			playerElement.innerHTML = `
				<span class="name">${player}</span>
				<span class="score">${this.scores[index]}</span>
			`;
			matchElement.appendChild(playerElement);
		});

	
		return matchElement;
	}		
}
