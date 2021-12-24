
// Cards

// Base Cards
class GameCard {
	div = document.createElement("div");
	img = new Image();
	category;
	
	constructor(src) {
		// TODO: make all cards into canvases so I can change them.
		this.img.src = src;
		this.div.appendChild(this.img);
		this.div.classList.add("slidein");
		//this.img.classList.add("slidein");
		this.category = "";
	}
	
	getImage() {
		return this.img;
	}
	
	getDiv() {
		return this.div;
	}
}


class VisibleCard extends GameCard {
	name;
	index;
	constructor(index, cardName, src, disp, category, dispCards=-1) {
		super(src);
		this.name = cardName;
		this.category = category;
		this.index = index;
		if(dispCards === -1) {
			dispCards = [this];
		}
		this.getDiv().addEventListener('click', function() {disp.show(dispCards);},false);
		//this.getImage().addEventListener('click', function() {disp.show(dispCards, this.category);},false);
	}
}

class ConcealedCard extends GameCard {
	constructor() {
		super("/data/cards/cardback.png");
	}
}


// Play Cards
class FaceUpPlayCard extends VisibleCard {
	cardName;
	used;
	attacked;
	rp;
	constructor(index, cardName, cards, disp, category, dispCards=-1) {
		super(index, cardName, cards[cardName].img.src, disp, category, dispCards);
		this.cardName = cardName;
		this.used = false;
		this.attacked = false;
		this.rp = parseInt(cards[cardName].cost.toString());
		this.getImage().classList.add("play");
		this.getDiv().classList.add("play");
	}
	
	increaseRP(value) {
		this.rp += value;
	}
	
	decreaseRP(value) {
		this.rp -= value;
	}
}

class FaceDownVisiblePlayCard extends VisibleCard {
	constructor(index, cardName, cards, disp, category, dispCards=-1) {
		super(index, cardName, "/data/cards/cardback.png", disp, category, dispCards);
		this.getImage().classList.add("play");
		this.getDiv().classList.add("play");
	}
}

class FaceDownConcealedPlayCard extends ConcealedCard {
	constructor() {
		super();
		this.getImage().classList.add("play");
		this.getDiv().classList.add("play");
	}
}

// Hand Cards
class VisibleHandCard extends VisibleCard {
	constructor(index, cardName, cards, disp, category) {
		super(index, cardName, cards[cardName].img.src, disp, category);
		this.getImage().classList.add("hand");
	}
}

class ConcealedHandCard extends ConcealedCard {
	constructor() {
		super();
		this.getImage().classList.add("hand");
	}
}

// Disp Cards
class DispCard extends GameCard {
	name;
	constructor(cardName, cards, clickfunc) {
		super(cards[cardName].img.src);
		this.name = cardName;
		this.getDiv().classList.add("disp");
		this.getImage().classList.add("disp");
		//this.getDiv().addEventListener('click', function() {clickfunc.hide();}, false);
		this.getImage().addEventListener('click', function() {clickfunc.hide();}, false);
	}
}


// Card Button 
class CardButton {
	div;
	txt;
	actionArgs;
	
	constructor(txt, cardName) {
		this.div = document.createElement("div");
		this.div.classList.add("slidein");
		this.div.classList.add("buttonTextDiv");
		this.div.innerHTML = txt;
		this.txt = txt;
	}
	
	setAction() {
		const func = this.action;
		const args = this.actionArgs;
		this.div.addEventListener('click', function() {func(args);}, false);
	}
	
	action(args) {
	}
}

class PlayButton extends CardButton {
	
	constructor(args, cardName) {
		super("play", cardName);
		this.actionArgs = [cardName, args[1].index];
		this.setAction();
	}
	
	action(args) {
		reqPlayCard(args[0], args[1]);
	}
	
}

class UseButton extends CardButton {
	
	constructor(args, cardName) {
		super("use", cardName);
		this.actionArgs = [cardName];
		this.setAction();
	}
	
	action(args) {
		console.log("in UseButton, args is,", args);
		reqUseCard(args[0], args[1]);
	}
	
}

class AttackButton extends CardButton {
	// TODO: implement this.
	
	constructor(args, cardName) {
		super("attack", cardName);
		this.actionArgs = [cardName];
		this.setAction();
	}
	
	action(args) {
		reqAttackWithCard(args[0]);
	}
	
}

class TargetButton extends CardButton {
	
	constructor(args, cardName) {
		super("target", cardName);
		this.actionArgs = args.concat([cardName]);
		this.setAction();
	}
	
	action(args) {
		console.log("in targetButton action, args is:", args);
		targetFuncs[args[2]](args[3]);
		args[0].removeCard(args[0].getCard(args[3]));
		
		//need to remove this card.
		//console.log(args);
		//args[1](args[0]);
		//targetCard(player);
	}
	
}


// Base Card group
class CardGroup {
	
	cards = [];
	allcards;
	div;
	
	/*discard;
	goal;
	deck;
	counters;
	hand;
	play;*/
	disp;
	
	constructor(allcards, divid){
		this.allcards = allcards;
		this.div = document.getElementById(divid);
	}
	
	lateinit(disp) { //discard, goal, deck, counters, hand, play, disp) {
		/*this.discard = discard;
		this.goal = goal;
		this.deck = deck;
		this.counters = counters;
		this.hand = hand;
		this.play = play;*/
		this.disp = disp;
	}
	
	hasCard(cardName) {
		if(!cardName) {
			return false;
		}
		const f = this.cards.filter(x => x.name === cardName);
		if(f.length > 0) {
			return true;
		}
		return false;
	}
	
	filterCards(func) {
		if(!func) {
			return false;
		}
		const f = this.cards.filter(func);
		return f;
	}
	
	addCard(cardName="cardback") {
		if(!cardName) {
			return false;
		}
		
		const card = this.makeCard(cardName);
		if(this.addCardInternal(card) && this.addCardImage(card)) {
			return true;
		}
		return false;
	}
	
	addCardInternal(card) {
		if(!card) {
			return false;
		}
		
		this.cards.push(card);
		return true;
	}
	
	addCardImage(card) {
		if(!card) {
			return false;
		}
		
		this.div.appendChild(card.getDiv());//card.getImage());
		return true;
	}
	
	makeCard(cardName) {
		return new ConcealedCard();
	}
	
	getCard(cardName, index=-1) {
		if(!cardName) {
			return false;
		}
		
		// decide whether to use index or cardName
		let card;
		if(index > -1 && index<this.cards.length && this.cards[index].name === cardName){
			card = this.cards[index];
		} else {
			const f = this.cards.filter(x => x.name === cardName);
			if(f.length === 0) {
				return false;
			}
			card = f[0];
		}
		
		return card;
	}
	
	removeCard(cardName, index=-1) {
		const card = this.getCard(cardName, index);
		if(!card) {
			return false;
		}
		
		// actually remove it
		if(this.removeCardImage(card) && this.removeCardInternal(card)) {
			return true;
		}
		return false;
	}
	
	removeCardInternal(card) {
		if(!card) {
			return false;
		}
		
		const i = this.cards.indexOf(card);
		if(i === -1) {
			return false;
		}
		
		this.cards.splice(i,1);
		return true;
	}
	
	removeCardImage(card) {
		if(!card || !this.div.contains(card.getDiv())) {//card.getImage())) {
			return false;
		}
		
		this.div.removeChild(card.getDiv());//card.getImage());
		return true;
	}
	
}



// Card Stacks

// base Card Stack

class Discard extends CardGroup {
	constructor(allcards, divid) {
		super(allcards, divid);
	}
	
	addCard(cardName) {
		if(this.cards.length > 0) {
			super.removeCardImage(this.cards[this.cards.length-1]);
		}
		super.addCard(cardName);
	}
	
	removeCard(cardName) {
		// TODO: This might not work. Fix later
		
		const card = this.getCard(cardName);
		if(card) {
			super.removeCardInternal(card);
			return true;
		}
		return false;
	}
	
	makeCard(cardName) {
		return new FaceUpPlayCard(this.cards.length, cardName, this.allcards, this.disp, "discard", this.cards);
	}
}

class VisibleGoal extends CardGroup {
	constructor(allcards, divid) {
		super(allcards, divid);
	}
	
	addCard(cardName) {
		const card = this.makeCard(cardName);
		super.addCardInternal(card);
	}
	
	removeCard(cardName) {
		const card = this.makeCard(cardName);
		super.removeCardInternal(card);
	}
	
	deal(cs) {
		super.addCardImage(this.makeCard("cardback"));
		for(let c of cs) {
			const card = this.makeCard(c);
			super.addCardInternal(card);
		}
	}
	
	makeCard(cardName) {
		return new FaceDownVisiblePlayCard(this.cards.length, cardName, this.allcards, this.disp,  "goal", this.cards);
	}
}

class ConcealedGoal extends CardGroup {
	constructor(allcards, divid) {
		super(allcards, divid);
	}
	
	addCard(cardName) {
	}
	
	removeCard(cardName) {
	}
	
	deal() {
		super.addCardImage(this.makeCard("cardback"));
	}
	
	makeCard(cardName) {
		return new FaceDownConcealedPlayCard();
	}
}

class Deck extends CardGroup {
	constructor(allcards, divid) {
		super(allcards, divid);
	}
	
	addCard(cardName) {
	}
	
	removeCard(cardName) {
	}
	
	deal() {
		super.addCardImage(this.makeCard("cardback"));
	}
	
	makeCard(cardName) {
		return new FaceDownConcealedPlayCard();
	}
}

// scrolling stuff
class VisibleHand extends CardGroup {
	makeCard(cardName) {
		return new VisibleHandCard(this.cards.length, cardName, this.allcards, this.disp, "hand");
	}
}

class ConcealedHand extends CardGroup {
	makeCard(cardName) {
		return new ConcealedHandCard();
	}
	
	addCard() {
		if(this.cards) {
			super.addCard("cardback");
			return true;
		}
		return false;
	}
	
	removeCard() {
		if(this.cards.length === 0) {
			return false;
		}
		const card = this.cards[0];
		if(!card) {
			return false;
		}
		
		// actually remove it
		if(this.removeCardImage(card) && this.removeCardInternal(card)) {
			return true;
		}
		return false;
	}
}

class Play extends CardGroup {
	makeCard(cardName) {
		return new FaceUpPlayCard(this.cards.length, cardName, this.allcards, this.disp, "play");
	}
	
	refreshCards() {
		for(let c of this.cards) {
			c.used = false;
			c.attacked = false;
		}
	}
}

// display
class Disp extends CardGroup {
	announceText;
	
	constructor(allcards, divid) {
		super(allcards, divid);
		this.announceText = document.createElement("text");
	}
	
	show(cards, extraButtonArgs=[], buttonOverride=-1, conditionOverride=-1) {
		const buttonmap = {
			"":[],
			"discard":[],
			"goal":[],
			"hand":[{"type":PlayButton, "args":[this, 0].concat(extraButtonArgs), condition:canPlayCard}],
			"play":[{"type":UseButton,  "args":[this, 0].concat(extraButtonArgs), condition:canUseCard},
					{"type":AttackButton,  "args":[this, 0].concat(extraButtonArgs), condition:canAttackCard}],
			"target":[{"type":TargetButton,  "args":[this, 0].concat(extraButtonArgs), condition:(conditionOverride === -1 ? x => true : conditionOverride)}],
		};
		
		this.hide();
		this.makeInteractable();
		
		for(let c of cards) {
			// give buttons access to parent card
			for(let cat of buttonmap[(buttonOverride === -1 ? c.category : buttonOverride)]) {
				if(cat.hasOwnProperty("args") && cat.args.length >= 2) {
					cat.args[1] = c;
				}
			}
			
			// add card
			console.log("add card", c.name, "category", (buttonOverride === -1 ? c.category : buttonOverride), buttonOverride);
			this.addCard(c.name, buttonmap[(buttonOverride === -1 ? c.category : buttonOverride)]);
		}
	}
	
	hide() {
		this.makeUninteractable();
		while(this.cards.length>0) {
			this.removeCard(this.cards[0]);
		}
	}
	
	flashText(txt) {
		this.announceText.innerHTML = txt;
		this.announceText.classList.add("slideby");
		this.div.appendChild(this.announceText);
		this.makeInteractable();
		
		const div = this.div;
		const announceText = this.announceText;
		const makeHidden = this;
		this.announceText.addEventListener('animationend', function(){
			if(div.contains(announceText)){div.removeChild(announceText);}
			makeHidden.makeUninteractable();
		}, false);
	}
	
	makeInteractable() {
		this.div.style.visibility = "visible";
		this.div.style.zIndex = 2;
	}
	
	makeUninteractable() {
		this.div.style.visibility = "hidden";
		this.div.style.zIndex = -1;
	}
	
	addCard(cardName, buttons) {
		super.addCard(cardName);
		this.addButtons(this.cards[this.cards.length-1], buttons);
	}
	
	removeCard(card) {
		this.removeButtons(card.buttons);
		super.removeCard(card.name);
	}
	
	addButtons(card, buttons) {
		if(!buttons || this.cards.length === 0) {
			return false;
		}
		
		this.cards[this.cards.length-1].buttons = [];
		for(let but of buttons) {
			if(!but.condition(card.name)) {continue;}
			const b = this.makeButton(but.type, but.args, card.name);
			card.getDiv().appendChild(b.div);//card.getImage().appendChild(b.div);
			console.log(but);
			//this.cards[this.cards.length-1].buttons.push(b);
		}
		return true;
	}
	
	removeButtons(buttons) {
		if(!buttons || this.cards.length === 0) {
			return false;
		}
		
		for(let b of buttons) {
			this.div.removeChild(b.div);
		}
		return true;
	}
	
	makeButton(btype, bargs, cardName) {
		return new btype(bargs, cardName);
	}
	
	makeCard(cardName) {
		return new DispCard(cardName, this.allcards, this);
	}
}

// Counters
class Counters {
	breathdiv;
	healthdiv;
	breath;
	health;
	
	constructor(breathid, healthid) {
		this.breathdiv = document.getElementById(breathid);
		this.healthdiv = document.getElementById(healthid);
		
		this.breath = 3;
		this.health = 40;
		
		this.updateCounters();
	}
	
	updateCounters() {
		this.breathdiv.innerHTML = "Breath: "+this.breath;
		this.healthdiv.innerHTML = "Health: "+this.health;
	}
	
	setBreath(value) {
		if(value===undefined) {
			return false;
		}	
		this.breath = value;
		this.updateCounters();
		return true;
	}
	
	increaseBreath(value) {
		if(value===undefined) {
			return false;
		}	
		this.breath += value;
		this.updateCounters();
		return true;
	}
	
	decreaseBreath(value) {
		if(value===undefined) {
			return false;
		}	
		this.breath -= value;
		this.updateCounters();
		return true;
	}
	
	getBreath() {
		return this.breath;
	}
	
	setHealth(value) {
		if(value===undefined) {
			return false;
		}	
		this.health = value;
		this.updateCounters();
		return true;
	}
	
	increaseHealth(value) {
		if(value===undefined) {
			return false;
		}	
		this.health += value;
		this.updateCounters();
		return true;
	}
	
	decreaseHealth(value) {
		if(value===undefined) {
			return false;
		}	
		this.health -= value;
		this.updateCounters();
		return true;
	}
	
	getHealth() {
		return this.health;
	}
}



// big boi player class
class Combatant {

	constructor(dividstart, disp) {
		
		this.disp = disp;
		
		this.counters = new Counters(dividstart+"health", dividstart+"breath");
		this.discard = new Discard(cards, dividstart+"discard");
		this.deck = new Deck(cards, dividstart+"deck");
		this.play = new Play(cards, dividstart+"play");
		this.discard.lateinit(disp);
		this.deck.lateinit(disp);
		this.play.lateinit(disp);
	}

}

class Player extends Combatant {
	constructor(dividstart, disp) {
		super(dividstart, disp);
		
		this.goal = new VisibleGoal(cards, dividstart+"goal");
		this.hand = new VisibleHand(cards, dividstart+"hand");
		this.goal.lateinit(disp);
		this.hand.lateinit(disp);
	}
}

class Opponent extends Combatant {
	constructor(dividstart, disp) {
		super(dividstart, disp);
		
		this.goal = new ConcealedGoal(cards, dividstart+"goal");
		this.hand = new ConcealedHand(cards, dividstart+"hand");
		this.goal.lateinit(disp);
		this.hand.lateinit(disp);
	}
}


function canPlayCard(cardName) {
	if(!yourMove || phase !== 1 || !cardName || !cards || !cards.hasOwnProperty(cardName) || !cards[cardName] || !player.hand.hasCard(cardName) || cards[cardName].cost > player.counters.getBreath()) {
		return false;
	}
	return true;
}

function canUseCard(cardName) {
	if(!yourMove || phase !== 1 || !cardName || !cards || !cards.hasOwnProperty(cardName) || !cards[cardName] || 
		!player.play.hasCard(cardName) || player.play.filterCards((  x => ((x.name==cardName)&&!x.used))).length === 0) {
		return false;
	}
	return true;
}

function canAttackCard(cardName) {
	if(!yourMove || phase !== 2 || !cardName || !cards || !cards.hasOwnProperty(cardName) || !cards[cardName] || 
		!player.play.hasCard(cardName) || player.play.filterCards((  x => ((x.name==cardName)&&!x.attacked))).length === 0) {
		return false;
	}
	return true;
}




