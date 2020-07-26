const app = require('express')();
const http = require('http').createServer(app);
const io = require('socket.io')(http);
const fs = require('fs');


				 
				 


app.get('/', function(req, res) {
	res.sendFile( __dirname + '/index.html' );
});

app.get('/data/*', function(req, res) {
	if(req.method === 'GET') {res.sendFile( __dirname + req.path);}
});


//Whenever someone connects this gets executed
io.on('connection', function(socket) {
	
	socket.on('end', function(){
		console.log('end?');
		socket.disconnect(0);
	});

	socket.on('clientChat', function(data) {
		console.log(data);
		io.emit('serverChat', data);
	});
	
	socket.on('dong', function(data) {
		//console.log("received dong!");
	});
	
	
	
	
	socket.on("reqAllCards", function(data){
		socket.emit("resAllCards", cards);
	});
	
	socket.on('clientAddCard', function(data) {
		console.log(data);
		cards.push(data);		
		fs.appendFileSync(__dirname+'\\cards\\cards.txt', data.name+"|"+data.cost+"|"+data.img+"|"+data.move+"|"+data.txtcolor+"|"+data.cardType+"|"+data.cardAction+"\n");
	});
	
	socket.on('clientAddDeck', function(data) {
		console.log(data);
		// add some check here later
		decks[data.name] = {deck:data.deck, goals:data.goals};
	});
	
	socket.on('clientReqDeck', function(data) {
		console.log('client requests deck', data);
		
		if(!decks || !decks.hasOwnProperty(data.name)) {
			// invalid deck
			return 0;
		}
		
		// check for open games
		console.log("attempting to match");
		for(let m in matches) {
			if(!matches[m].active) {
				// available match!
				console.log("available match!", m);
				
				matches[m].players.push(socket.id);
				matches[m].playerData[socket.id] = new Player(decks[data.name]);
				activePlayers[socket.id] = m;
				matches[m].playerCount ++;
				
				
				console.log(matches[m].playerData[socket.id]);
				
				if(matches[m].playerCount >= 2) {
					matches[m].active = true;
					setTimeout(function() {
						// match has started!
						console.log("both players have joined, begin match!");
						console.log(m);
						if(matches[m].playerCount < 2) { return; };
						for(let player of matches[m].players) {
							// deal
							dealHand(matches[m], player);
						}
						setTimeout(function() {
							if(Math.random() < 0.5) {
								matches[m].switchTurn();
							}
							matches[m].announceTurn();
							dealCard(matches[m], matches[m].playerTurn);
						}, 2000);
					}, 100);
				}
				return;
			}
		}
		
		// no available matches
		if(decks && decks.hasOwnProperty(data.name)){
			playerData[socket.id] = decks[data.name].slice();
			shuffle(playerData[socket.id]);
			let tmp = playerData[socket.id].slice(playerData[socket.id].length-5, playerData[socket.id].length);
			console.log(tmp);
		}
	});
	
	
	socket.on("playCard", function(data) {
		console.log("playcard", data);
		if(activePlayers.hasOwnProperty(socket.id)){
			const match = matches[activePlayers[socket.id]];
			// check if it's that player's turn
			if(match.players.indexOf(socket.id) === match.playerTurn) {
				// tell everyone card has been played
				for(let player of match.players) {
					io.to(player).emit('playCard', {name:data.name, index:data.index, yours:player===socket.id, specialPlay: data.specialPlay});
				}
			}
		}
	});
	
	socket.on("playCardFromDeck", function(data) {
		console.log("playCardFromDeck", data);
		if(activePlayers.hasOwnProperty(socket.id)){
			const match = matches[activePlayers[socket.id]];
			// check if it's that player's turn
			if(match.players.indexOf(socket.id) === match.playerTurn) {
				// tell everyone card has been played
				for(let player of match.players) {
					io.to(player).emit('playCardFromDeck', {name:data.name, index:data.index, yours:player===socket.id, specialPlay: data.specialPlay});
				}
			}
		}
	});
	
	socket.on("playCardFromDiscard", function(data) {
	});
	
	socket.on("useCard", function(data) {
		console.log("usecard", data);
		if(activePlayers.hasOwnProperty(socket.id)){
			const match = matches[activePlayers[socket.id]];
			// check if it's that player's turn
			if(match.players.indexOf(socket.id) === match.playerTurn) {
				// tell everyone card has been played
				for(let player of match.players) {
					io.to(player).emit('useCard', {name:data.name, index:data.index, yours:player===socket.id});
				}
			}
		}
	});
	
	socket.on("passTurn", function(data) {
		if(activePlayers.hasOwnProperty(socket.id)){
			const match = matches[activePlayers[socket.id]];
			const targeti = match.players.indexOf(socket.id);
			match.passTurn(targeti);
		}
	});
	
	socket.on("reqAdvancePhase", function(data) {
		if(activePlayers.hasOwnProperty(socket.id)){
			const match = matches[activePlayers[socket.id]];
			const targeti = match.players.indexOf(socket.id);
			match.advancePhase(targeti);
		}
	});
	
	socket.on("reqDealCard", function(data) {
		if(activePlayers.hasOwnProperty(socket.id)){
			const match = matches[activePlayers[socket.id]];
			// check if it's that player's turn
			if(match.players.indexOf(socket.id) === match.playerTurn) {
				// tell everyone card has been delt	
				dealCard(match, (match.players.indexOf(socket.id)+(data.mine ? 0:1))%match.playerCount);
			}
		}
	});
	
	socket.on("reqDealSpecificCard", function(data) {
		if(activePlayers.hasOwnProperty(socket.id)){
			const match = matches[activePlayers[socket.id]];
			// check if it's that player's turn
			if(match.players.indexOf(socket.id) === match.playerTurn) {
				// tell everyone card has been delt	
				dealSpecificCard(match, (match.players.indexOf(socket.id)+(data.mine ? 0:1))%match.playerCount, data.cardName);
			}
		}
	});
	
	socket.on("reqSearchDeck", function(data) {
		if(activePlayers.hasOwnProperty(socket.id)) {
			const match = matches[activePlayers[socket.id]];
			// check if it's that player's turn
			if(match.players.indexOf(socket.id) === match.playerTurn) {
				// tell everyone card has been delt	
				//dealCard(match, match.players.indexOf(socket.id));
				const targetid = match.players[(match.playerTurn+(data.mine ? 0:1))%match.playerCount];
				console.log("req search deck", data.category);
				console.log(match.playerData[targetid]["deck"]);
				console.log(match.playerData[targetid]["deck"].map(x => cards.find(y => y.name===x).cardType));
				console.log(match.playerData[targetid]["deck"].filter(x => cards.find(y => y.name===x).cardType.includes(data.category)));
				console.log(data.action);
				socket.emit("resSearchDeck", {"cards":match.playerData[targetid]["deck"].filter(x => cards.find(y => y.name===x).cardType.includes(data.category)),
											  "amount":data.amount,
											  "action":data.action});
				
			}
		}
	});
	
	
	
	
	// quiz time
	socket.on("startQuiz", function(data) {
		quizPlayers[socket.id] = 0;
		socket.emit("startQuiz", {});
	});
	
	socket.on("quizAttemptAnswer", function(data) {
		if(!quizPlayers.hasOwnProperty(socket.id)) {
			return;
		}
		if(data.answer === quizAnswers[quizPlayers[socket.id]]) {
			quizPlayers[socket.id] += 1;
			if(quizPlayers[socket.id] >= quizAnswers.length) {
				// finished quiz
				socket.emit("quizFinish", {});
				quizPlayers[socket.id] = -1;
			} else {
				// not finished quiz
				socket.emit("quizRightAnswer", {question:quizQuestions[quizPlayers[socket.id]]});
			}
		} else {
			socket.emit("quizWrongAnswer", {});
		}
	});
	
	socket.on("quizSubmitQuestion", function(data) {
		if(!quizPlayers.hasOwnProperty(socket.id) || quizPlayers[socket.id] !== -1) {
			return;
		}
		fs.appendFileSync(__dirname+'\\quiz\\quizQuestions.txt', "\n"+data.question);
		fs.appendFileSync(__dirname+'\\quiz\\quizAnswers.txt', "\n"+data.answer);
		quizQuestions.push(data.question);
		quizAnswers.push(data.answer);
		
	});
	
	
	
	
	socket.on("platformerNewPlayer", function(data) {
		console.log(data);
		const colors="0123456789ABCDEF";
		const color = "#"+
					  colors[Math.floor(Math.random()*colors.length)]+
				      colors[Math.floor(Math.random()*colors.length)]+
					  colors[Math.floor(Math.random()*colors.length)]+
					  colors[Math.floor(Math.random()*colors.length)]+
					  colors[Math.floor(Math.random()*colors.length)]+
					  colors[Math.floor(Math.random()*colors.length)];
		io.to(socket.id).emit("platformerChangePlayerColor", {c: color});
		platformerPlayers[socket.id] = {x:data.x,y:data.y,c:color};
		
		
		for(let player in platformerPlayers) {
			if(player !== socket.id) {
				io.to(player).emit('platformerNewPlayer', {id:socket.id, x:data.x,y:data.y,c:color});
				io.to(socket.id).emit('platformerNewPlayer', {id:player, x:platformerPlayers[player].x,y:platformerPlayers[player].y,c:platformerPlayers[player].c});
			}
		}
		
	});
	
	socket.on("platformerMovePlayer", function(data) {
		if(!platformerPlayers.hasOwnProperty(socket.id)) {
			platformerPlayers[socket.id] = {x:data.x,y:data.y};
		}
		platformerPlayers[socket.id].x = data.x;
		platformerPlayers[socket.id].y = data.y;
		for(let player in platformerPlayers) {
			if(player !== socket.id) {
				io.to(player).emit('platformerMovePlayer', {id:socket.id, x:data.x,y:data.y});
			}
		}
	});
	
	socket.on("platformerRemovePlayer", function(data) {
		if(!platformerPlayers.hasOwnProperty(socket.id) || !platformerPlayers.hasOwnProperty(data.id)) {
			return;
		}
		for(let player in platformerPlayers) {
			if(player !== data.id) {
				io.to(player).emit('platformerRemovePlayer', {id:data.id});
			} else {
				io.to(player).emit('removeMe', {});
			}
		}
		delete platformerPlayers[data.id];
		console.log(platformerPlayers);
	});
	
	

	//Whenever someone disconnects this piece of code executed
	socket.on('disconnect', function () {
		console.log('user disconnected');
		if(activePlayers.hasOwnProperty(socket.id)){
			// a player left, deactivate match
			const match = matches[activePlayers[socket.id]];
			match.active = false;
			
			while(match.playerCount > 0) {
				const player = match.players[0];
				console.log("match is now:", match, "removing:",player);
				// let connected players know that match is over.
				io.to(player).emit('playerDisconnect', {});
				// remove all players from the match
				delete match.playerData[player];
				--match.playerCount;
				delete match.players.splice(0, 1);
				delete activePlayers[player];
				console.log("removed! Now only", match.playerCount, "left.");
			}
			console.log("match is now:", match);
			console.log("activePlayers is now:", activePlayers);
			
			
			
			
		}
		
		if(quizPlayers.hasOwnProperty(socket.id)){
			delete quizPlayers[socket.id];
		}
	});
});












				 
				 
class Match {
	constructor() {
		// active -> match has started
		this.active = false;
		
		// limits to restrict double clicking and stuff
		this.changingTurns = false;
		this.advancingPhase = false;
		this.dealing = false;
		
		// list of player ids
		this.players = [];
		
		// format playerid: Player()
		this.playerData = {};
		
		// things to keep track of stuff
		this.playerCount = 0;
		this.playerTurn = 0;
		this.phase = 1;
	}
	
	switchTurn() {
		this.playerTurn += 1;
		this.playerTurn %= this.players.length;
	}
	
	
	announceTurn() {
		for(let pindex=0; pindex<this.players.length; ++pindex) {
			if(pindex===this.playerTurn) {
				io.to(this.players[pindex]).emit("yourMove", {});
			} else {
				io.to(this.players[pindex]).emit("opponentsMove", {});
			}
		}
	}
	
	passTurn(targeti) {
		if(this.playerCount < 2) {
			return;
		}
		if(this.changingTurns) {
			//setTimeout(function(){passTurn(targetid);}, 400);
			return;
		}
		if(targeti !== this.playerTurn) {
			return;
		}
		
		this.changingTurns = true;
		// check if it's that player's turn
		//setTimeout(function() {
		console.log("pass turn.");
		
		
		//TODO: make this better (reorder+fix disp.flashText)
		this.resetPhase();
		this.announcePhase();
		
		this.switchTurn();
		this.announceTurn();
		dealCard(this, this.playerTurn);
		
		// figure out how to do this properly.
		this.changingTurns = false;
	}
	
	incrementPhase() {
		this.phase += 1;
	}
	
	resetPhase() {
		this.phase = 0;
	}
	
	announcePhase() {
		if(this.phase < 0 || this.phase > 2) {
			return;
		}
		for(let pindex=0; pindex<this.players.length; ++pindex) {
			io.to(this.players[pindex]).emit("advancePhase", {"phase":this.phase});
		}
	}
	
	advancePhase(targeti) {
		if(this.playerCount < 2) {
			return;
		}
		if(this.advancingPhase) {
			return;
		}
		if(this.phase >= 2) {
			return;
		}
		
		if(targeti !== this.playerTurn) {
			return;
		}
		
		this.advancingPhase = true;
		console.log("advance phase.");
		this.incrementPhase();
		this.announcePhase();
		
		//TODO: make this better.
		this.advancingPhase = false;
	}
}

class Player {
	constructor(sourceDeck) {
		this.deck = sourceDeck.deck.slice();
		this.goals = sourceDeck.goals.slice();
		this.hand = [];
	}
}
				 
				 
				 
				 
const cards = [];
const decks = {'k':{ deck: ['Dragon King Hades',
							'Dragon King Hades', 
							'Dragon King Hades', 
							'Lucifer the Demon King',
							'Sharpen Swords',
							'Sharpen Swords',
							'Sharpen Swords',
							'Golden Claws',
							'Golden Claws',
							'Golden Claws',
							'Call of Hades',
							'Call of Hades',
							'Call of Hades',
							'Tyranny',
							'Breath User Jaycob',
							'Breath User Jaycob',
							'Breath User Jaycob',
							'Recruitment',
							'Soul Bond',
							'Skinny Jaycob',
							'Skinny Jaycob',
							'Skinny Jaycob',], 
					goals: ['Overwhelming Attack',
							'Overwhelming Numbers',
							'Overwhelming Defense']}};
const activePlayers = {};
const matches = [new Match(), new Match()];
				 
				 
				 
		







		
				 


function shuffle(a) {
    var j, x, i;
    for (i = a.length - 1; i > 0; i--) {
        j = Math.floor(Math.random() * (i + 1));
        x = a[i];
        a[i] = a[j];
        a[j] = x;
    }
    return a;
}






function dealCard(match, targeti) {
	if(match.playerCount < 2) {
		return;
	}
	if(match.dealing) {
		console.log("already dealing");
		//setTimeout(function(){dealCard(match, targeti);}, 400);
		return;
	}
	
	match.dealing = true;
	for(let pindex=0; pindex<match.playerCount; ++pindex) {
		if(pindex===targeti) {
			io.to(match.players[pindex]).emit('dealCard', {yours:true, cardName: match.playerData[match.players[targeti]].deck.shift()});
		} else {
			io.to(match.players[pindex]).emit("dealCard", {yours:false});
		}
		console.log(targeti, "deck", match.playerData[match.players[targeti]].deck);
		console.log(targeti, "deck", match.playerData[match.players[targeti]].deck);
		console.log(targeti, "deck", match.playerData[match.players[targeti]].deck);
		console.log(targeti, "deck", match.playerData[match.players[targeti]].deck);
		console.log(targeti, "deck", match.playerData[match.players[targeti]].deck);
		console.log(targeti, "deck", match.playerData[match.players[targeti]].deck);
	}
	match.dealing = false;
}

function dealSpecificCard(match, targeti, cardName) {
	if(match.playerCount < 2) {
		return;
	}
	
	if(match.playerData[match.players[targeti]].deck.indexOf(cardName) === -1) {
		return;
	}
	
	if(match.dealing) {
		console.log("already dealing");
		//setTimeout(function(){dealCard(match, targeti);}, 400);
		return;
	}
	
	match.dealing = true;
	for(let pindex=0; pindex<match.playerCount; ++pindex) {
		if(pindex===targeti) {
			const cardIndex = match.playerData[match.players[targeti]].deck.indexOf(cardName);
			console.log(' ==================== in reqDealSpecificCard ===========================================');
			console.log(cardIndex, match.playerData[match.players[targeti]].deck[cardIndex]);
			io.to(match.players[pindex]).emit('dealCard', {yours:true, cardName: match.playerData[match.players[targeti]].deck.splice(cardIndex,1)});
		} else {
			io.to(match.players[pindex]).emit("dealCard", {yours:false});
		}
		console.log(targeti, "deck", match.playerData[match.players[targeti]].deck);
		console.log(targeti, "deck", match.playerData[match.players[targeti]].deck);
		console.log(targeti, "deck", match.playerData[match.players[targeti]].deck);
		console.log(targeti, "deck", match.playerData[match.players[targeti]].deck);
		console.log(targeti, "deck", match.playerData[match.players[targeti]].deck);
		console.log(targeti, "deck", match.playerData[match.players[targeti]].deck);
	}
	match.dealing = false;
}

function dealHand(match, targetid) {
	const tmpDeck = shuffle(match.playerData[targetid].deck);
	const tmpGoal = shuffle(match.playerData[targetid].goals);
	console.log(targetid, "new deck", match.playerData[targetid].deck);
	io.to(targetid).emit("clientDeal", {goal:tmpGoal.shift(), hand:tmpDeck.splice(0,6)});
	console.log("deck", match.playerData[targetid].deck);
	console.log("deck", match.playerData[targetid].deck);
	console.log("deck", match.playerData[targetid].deck);
}









function sendHeartbeat(){
    setTimeout(sendHeartbeat, 8000);
    io.sockets.emit('ding', { beat : 1 });
	//console.log('dinging');
}
sendHeartbeat();

function loadcards() {
	fs.readFile(__dirname+'\\cards\\cards.txt', 'utf8', function(err, contents) {
		let lines = contents.split("\n");
		let arguments;
		for(let line of lines) {
			if(!line || line.length === 0 || line.indexOf("|") === -1) {
				continue;
			}
			arguments = line.split("|");
			cards.push({name:arguments[0], cost:arguments[1], img:arguments[2], move:arguments[3], txtcolor:arguments[4], cardType:arguments[5], cardAction:arguments[6]});
		}
	});
}
loadcards();






// quiz stuff
const quizPlayers = {};
const quizQuestions = ["Type 'start'"];
const quizAnswers = ["start"];
function loadQuiz() {
	fs.readFile(__dirname+'\\quiz\\quizQuestions.txt', 'utf8', function(err, contents) {
		let lines = contents.split("\n");
		
		for(let line of lines) {
			if(!line || line.length === 0) {
				continue;
			}
			quizQuestions.push(line.replace(/(\r\n|\n|\r)/gm, ""));
		}
	});
	fs.readFile(__dirname+'\\quiz\\quizAnswers.txt', 'utf8', function(err, contents) {
		let lines = contents.split("\n");
		
		for(let line of lines) {
			if(!line || line.length === 0) {
				continue;
			}
			quizAnswers.push(line.replace(/(\r\n|\n|\r)/gm, ""));
		}
	});
	
}
loadQuiz();





const platformerPlayers = {};














http.listen(3000, function() {
	console.log('listening on *:3000');
});