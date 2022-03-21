
// communication init
//const socket = io("/cardgame");
const carddisplaysocket = io("/cards");
/*
socket.on('ding', function(data){
	socket.emit("dong", {beat: 1});});
*/

// player connection+setup stuff

carddisplaysocket.on("resAllStockCards", resAllCards);

/*
socket.on("beginGame", beginGame);
socket.on("endGame", endGame);
socket.on("serverReqChooseCards", getCards);
socket.on("serverReqChooseText", getText);
socket.on("updateCollection", updateCollection);
socket.on("updateCounters", updateCounters);
socket.on("dispCards", dispCards);
*/





// socket stuff
function resAllCards(data) {
	console.log("in resAllCards", data);
	for(let card of data) {
		cards[card.name] = Card([], 0, 0, card.name, card.cost, card.img, card.move, card.txtcolor, card.cardType, card.cardAction);
	}
}


function beginGame(data) {
	console.log('in beginGame', data);
	/*for(let card of data['hand']) {
		dispBGCard(card, playerHand);
	}
	for(let card of data['activeGoals']) {
		dispBGCard(card, playerActiveGoals);
	}*/
	
	dispBGCard('cardBack', playerDeck);
	dispBGCard('cardBack', playerGoals);
	dispBGCard('cardBack', opponentDeck);
	dispBGCard('cardBack', opponentGoals);
	clearMainDisplay();
	
	counterDiv.classList.add('fadein');
}

function endGame(data) {
	console.log('in endGame');
	
	for(let container of [playerPlay, playerHand, playerActiveGoals, opponentPlay, opponentHand, opponentActiveGoals]) {
		while(container.firstChild) {
			removeBGCard(0, container);
		}
	}
	clearControl();
	dispText(data['msg']);
}

function getCards(data) {
	
	authToken = data['authToken'];
	delete data['authToken'];
	
	if(messageId==data['msgId']) {
		return;
	}
	messageId = data['msgId'];
	delete data['msgId'];
	let msg = data['msg'];
	delete data['msg'];
	
	clearControl();
	
	
	
	
	const p = document.createElement("p");
	p.innerHTML = msg;
	p.classList.add("fadein");
	controlTextDiv.appendChild(p);
	
	controlSubmitButton.classList.remove("uninteractable");
	hideOpponentCardButton.classList.remove("uninteractable");
	
	
	
	for(let name in data) {
		makeNewControlArea(name, controlDiv, control, controlNames);
	}
	for(let area of control) {
		area.style.height = (70/control.length)+"vh";
		area.firstChild.style.fontSize = (16/control.length)+"vh";
	}
	for(let i=0; i<controlNames.length; ++i) {
		for(let cindex=0; cindex < data[controlNames[i]].length; ++cindex) {
			console.log(data[controlNames[i]][cindex], cindex, i);
			dispControlCard(data[controlNames[i]][cindex], cindex, i);
		}
	}
}

function getText(data){
	authToken = data['authToken'];
	delete data['authToken'];
	
	if(messageId==data['msgId']) {
		return;
	}
	messageId = data['msgId'];
	delete data['msgId'];
	let msg = data['msg'];
	delete data['msg'];
	
	clearControl();
	
	
	
	
	const p = document.createElement("p");
	p.innerHTML = msg;
	p.classList.add("fadein");
	controlTextDiv.appendChild(p);
	
	controlSubmitButton.classList.remove("uninteractable");
	hideOpponentCardButton.classList.remove("uninteractable");
	
	const chooseTextDiv = document.createElement('div');
	chooseTextDiv.id = "chooseText";
	controlDiv.appendChild(chooseTextDiv);
	control.push(chooseTextDiv);
	
	for(let i=0; i<data['msgs'].length; ++i) {
		const ct = new ChooseText(data['msgs'][i], i);
		chooseTextDiv.appendChild(ct.txt);
	}
}

function updateCollection(data) {
	console.log('in updateCollection', data);
	let cardFunc;
	if(data['operation'] === 'add') {
		cardFunc = dispBGCard;
		if(data['collection']==='response') {
			cardFunc = dispBGCardReverse;
		}
	} else if(data['operation']==='remove'){
		cardFunc = removeBGCard;
		if(data['collection']==='response') {
			cardFunc = removeBGCardReverse;
		}
	}
	
	if(data['collection'] === 'discard') {
		if(data['yours']) {
			for(let card of data['cards']) {
				cardFunc(card, playerDiscard);
			}
		} else {
			for(let card of data['cards']) {
				cardFunc(card, opponentDiscard);
			}
		}
	} else if(data['collection'] === 'hand') {
		if(data['yours']) {
			for(let card of data['cards']) {
				cardFunc(card, playerHand);
			}
		} else {
			for(let card of data['cards']) {
				cardFunc(card, opponentHand);
			}
		}
	} else if(data['collection'] === 'activeGoals') {
		if(data['yours']) {
			for(let card of data['cards']) {
				cardFunc(card, playerActiveGoals);
			}
		} else {
			for(let card of data['cards']) {
				cardFunc(card, opponentActiveGoals);
			}
		}
	} else if(data['collection'] === 'play') {
		if(data['yours']) {
			for(let card of data['cards']) {
				if(data['operation'] === 'remove') {
					card += playerResponseCards;
				}
				console.log("removing: ", card);
				cardFunc(card, playerPlay);
			}
		} else {
			for(let card of data['cards']) {
				if(data['operation'] === 'remove') {
					card += opponentResponseCards;
				}
				cardFunc(card, opponentPlay);
			}
		}
	} else if(data['collection'] === 'response') {
		if(data['yours']) {
			for(let card of data['cards']) {
				if(data['operation'] === 'remove') {
					card += playerResponseCards;
				}
				console.log("adding/removing response card: ", card);
				cardFunc(card, playerPlay);
				playerResponseCards += (data['operation'] === "add") - (data['operation'] === "remove");
			}
		} else {
			for(let card of data['cards']) {
				if(data['operation'] === 'remove') {
					card += opponentResponseCards;
				}
				cardFunc(card, opponentPlay);
				opponentResponseCards += (data['operation'] === "add") - (data['operation'] === "remove");
			}
		}
	}
}


function updateCounters(data) {
	console.log('in updateCounters', data);
	if(data['yours']) {
		if(data['counter'] === 'health') {
			playerHealth.innerHTML = 'health: '+data['amount'];
		} else if(data['counter'] === 'breath') {
			playerBreath.innerHTML = 'breath: '+data['amount'];
		} else if(data['counter'] === 'rp') {
			playerPlay.children[playerResponseCards + data['amount'][0]].children[1].innerHTML = data['amount'][1];
		}
	} else {
		if(data['counter'] === 'health') {
			opponentHealth.innerHTML = 'health: '+data['amount'];
		} else if(data['counter'] === 'breath') {
			opponentBreath.innerHTML = 'breath: '+data['amount'];
		} else if(data['counter'] === 'rp') {
			opponentPlay.children[opponentResponseCards + data['amount'][0]].children[1].innerHTML = data['amount'][1];
		}
	}
}




function dispCards(data) {
	console.log('in dispCards', data);
	
	
	
	makeNewControlArea(data.msg, opponentCardDiv, opponentCards, opponentCardNames);
	opponentCards[opponentCards.length-1].style.height = 35+"vh";
	opponentCards[opponentCards.length-1].firstChild.style.fontSize = 8+"vh";
	for(let cindex=0; cindex<data.cards.length; ++cindex) {
		dispOpponentCard(data.cards[cindex], cindex, opponentCards.length-1);
	}
}







// init values
cards = {};
const control = [];
const controlNames = [];
const opponentCards = [];
const opponentCardNames = [];
let authToken = 0;
let messageId = 0;

const controlDiv = document.getElementById("control");
const opponentCardDiv = document.getElementById("opponentCards");
const controlTextDiv = document.getElementById("controlText");
const controlSubmitButton = document.getElementById("submitButton");
const hideOpponentCardButton = document.getElementById("hideOpponentCardButton");


const mainDisplayDiv = document.getElementById('mainDisplayDiv');

const counterDiv = document.getElementById("counterDivs");
const playerHealth = document.getElementById("playerHealth");
const playerBreath = document.getElementById("playerBreath");
const opponentHealth = document.getElementById("opponentHealth");
const opponentBreath = document.getElementById("opponentBreath");

const playerDiscard = document.getElementById('player1');
const playerDeck = document.getElementById('player2');
const playerActiveGoals = document.getElementById('player3');
const playerGoals = document.getElementById('player4');
const playerHand = document.getElementById('player5');
const playerPlay = document.getElementById('player6');
let playerResponseCards = 0;


const opponentDiscard = document.getElementById('opponent1');
const opponentDeck = document.getElementById('opponent2');
const opponentActiveGoals = document.getElementById('opponent3');
const opponentGoals = document.getElementById('opponent4');
const opponentHand = document.getElementById('opponent5');
const opponentPlay = document.getElementById('opponent6');
let opponentResponseCards = 0;



// other stuff



function makeNewControlArea(name, div, controls, names) {
	const newArea = document.createElement('div');
	newArea.classList.add('subControl');
	//newArea.innerHTML = name;
	
	
	const p = document.createElement('p');
	p.innerHTML = name;
	p.classList.add("label");
	p.classList.add("fadeinthenout");
	
	newArea.appendChild(p);
	
	div.appendChild(newArea);
	controls.push(newArea);
	names.push(name);
	
	
	
	
}


function clearControl() {
	for(let area of control) {
		controlDiv.removeChild(area);
	}
	while(controlTextDiv.firstChild) {
		controlTextDiv.removeChild(controlTextDiv.firstChild);
	}
	control.splice(0,control.length);
	controlNames.splice(0,controlNames.length);
	selected.splice(0,selected.length);
	
	controlSubmitButton.classList.add('uninteractable');
	hideOpponentCardButton.classList.add('uninteractable');
}

function dispControlCard(cardName, i, section) {
	const c = new GameCard(cardName, i, controlNames[section]);
	c.addTo(control[section]);
}

function dispOpponentCard(cardName, i, section) {
	const c = new BGCard(cardName);
	c.addToStart(opponentCards[section]);
}













// background stuff
function dispBGCard(cardName, container) {
	const c = new BGCard(cardName);
	c.addTo(container);
}

function removeBGCard(i, container) {
	container.removeChild(container.children[i]);
}

function dispBGCardReverse(cardName, container) {
	const c = new BGCard(cardName);
	c.addToStart(container);
}

function removeBGCardReverse(i, container) {
	container.removeChild(container.children[container.children.length-i]);
}




// disp stuff
mainDisplayDiv.addEventListener('click', function() {
	clearMainDisplay();
},false);

function clearAndDispCard(cardName, counter) {
	clearMainDisplay();
	dispCard(cardName, counter);
}

function dispCard(cardName, counter) {
	mainDisplayDiv.classList.add("fadein");
	mainDisplayDiv.style.pointerEvents = "auto";
	const c = new DispCard(cardName, counter);
	c.addTo(mainDisplayDiv);
}

function dispText(msg) {
	mainDisplayDiv.classList.add("fadein");
	mainDisplayDiv.style.pointerEvents = "auto";
	const p = document.createElement('p');
	p.innerHTML = msg;
	mainDisplayDiv.appendChild(p);
}

function clearMainDisplay() {
	while(mainDisplayDiv.firstChild) {
		mainDisplayDiv.removeChild(mainDisplayDiv.firstChild);
	}
	mainDisplayDiv.classList.remove("fadein");
	mainDisplayDiv.style.pointerEvents = "none";
}










// button interaction functions
function deckreq(){
	//socket.emit('reqQueueGame', {name : document.forms['cardForm']['deckName'].value});
	document.getElementById("deckformdiv").style.visibility = "hidden";
	document.getElementById("gamediv").style.visibility = "visible";
}

function resGetCards() {
	out = [];
	for(let c of selected) {
		out.push([c.category, c.origNumber]);
	}
	socket.emit('clientResChooseCards', {'authToken':authToken, order:out});
	clearControl();
}

function cycleControl(button) {
	if(opponentCardDiv.style.display === "block") {
		opponentCardDiv.style.display = "none";
		controlDiv.style.display = "block";
		hideOpponentCardButton.innerHTML = "show opponent cards";
	} else {
		opponentCardDiv.style.display = "block";
		controlDiv.style.display = "none";
		hideOpponentCardButton.innerHTML = "hide opponent cards";
	}
}

function toggleControl(button) {
	console.log(button);
	if(controlDiv.classList.contains('uninteractable')) {
		controlDiv.classList.remove('uninteractable');
		controlTextDiv.classList.remove('uninteractable');
		controlSubmitButton.classList.remove('uninteractable');
		hideOpponentCardButton.classList.remove('uninteractable');
		opponentCardDiv.classList.remove('uninteractable');
		button.innerHTML = 'hide control';
	} else {
		controlDiv.classList.add('uninteractable');
		controlTextDiv.classList.add('uninteractable');
		controlSubmitButton.classList.add('uninteractable');
		hideOpponentCardButton.classList.add('uninteractable');
		opponentCardDiv.classList.add('uninteractable');
		button.innerHTML = 'show control';
	}
	
}





window.addEventListener("DOMContentLoaded", function(event) {
	//carddisplaysocket.emit("reqAllStockCards", {});
	
	// for testing purposes, pretend server sent everything over to start game
	resAllCards([
  {
    "name": "The March of the Fairyfly",
    "cost": "",
    "img": "",
    "move": "End your turn with 7 or more unit cards with 5 RP or less in play.",
    "txtcolor": "",
    "cardType": "goal",
    "cardAction": "",
    "cardActionOnPlay": "",
    "cardActionOnAttack": "",
    "cardActionOnKill": ""
  },
  {
    "name": "Miyamoto Musashi",
    "cost": "5",
    "img": "",
    "move": "Spend 1 breath, then set this unit's RP to 2*X, where X is the number of units your opponent controls.",
    "txtcolor": "",
    "cardType": "rare swordsman unit",
    "cardAction": "checkBreath me 1 this 0 setRP me 1 0 miyamotoMusashi me you play 0 miyamotoMusashi me you play 0 increaseRP me -1 0 checkBreath me 1 increaseBreath me -1",
    "cardActionOnPlay": "",
    "cardActionOnAttack": "",
    "cardActionOnKill": ""
  },
  {
    "name": "Demon's Rebirth",
    "cost": "3",
    "img": "",
    "move": "Special call 2 Demon Unit cards from your discard pile.",
    "txtcolor": "",
    "cardType": "action",
    "cardAction": "searchCollection me discard any demon 0 choose me me discard 2 0 1 moveCards me discard play 1",
    "cardActionOnPlay": "",
    "cardActionOnAttack": "",
    "cardActionOnKill": ""
  },
  {
    "name": "Full Counter",
    "cost": "1",
    "img": "",
    "move": "Activate when you would have taken direct damage from an opponent's card. Cancel the damage and reflect it back onto them.",
    "txtcolor": "",
    "cardType": "response",
    "cardAction": "",
    "cardActionOnPlay": "",
    "cardActionOnAttack": "",
    "cardActionOnKill": ""
  },
]);
	deckreq();
	beginGame();
	
	// populate with cards, just to see how it looks
	let data = [
		{
			'operation' : 'add',
			'yours'     : true,
			'collection': 'hand',
			'cards'     : ['Full Counter', 'Full Counter', 'Full Counter', 'Full Counter', 'Full Counter',  'Full Counter',  'Full Counter', ]
		},
		{
			'operation' : 'add',
			'yours'     : true,
			'collection': 'discard',
			'cards'     : ['Full Counter', 'Full Counter', 'Full Counter']
		},
		{
			'operation' : 'add',
			'yours'     : true,
			'collection': 'activeGoals',
			'cards'     : ['The March of the Fairyfly', 'The March of the Fairyfly']
		},
		{
			'operation' : 'add',
			'yours'     : false,
			'collection': 'hand',
			'cards'     : ['cardBack', 'cardBack','cardBack','cardBack','cardBack','cardBack','cardBack',]
		},
		{
			'operation' : 'add',
			'yours'     : false,
			'collection': 'discard',
			'cards'     : ['Full Counter', 'Full Counter', 'Full Counter', 'Full Counter', 'Full Counter', 'Full Counter']
		},
		{
			'operation' : 'add',
			'yours'     : false,
			'collection': 'activeGoals',
			'cards'     : ['cardBack']
		},
	];
	for(let d of data) {
		updateCollection(d);
	}
		
});

