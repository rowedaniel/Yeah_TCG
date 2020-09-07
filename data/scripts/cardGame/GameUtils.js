
const selected = [];



class BaseCard {
	div = document.createElement("div");
	img = new Image();
	
	constructor(cardName) {
		
		this.div.classList.add("dispDiv");
		this.div.classList.add("slidein");
		
		
		if(cardName === 'cardBack') {
			this.img.src = "/data/cards/cardback.png";
		} else {
			const card = this;
			const setImage = function() {
				card.img.src = cards[cardName].img.src;
				if(card.img.src === 'http://localhost:3000/data/cards/cardtemplate.png') {
					setTimeout(setImage, 100);
				}
			}
			setImage();			
		}
		this.img.classList.add("dispCard");

		
		this.div.appendChild(this.img);
		
		
		
		
		const card = this;
		
		this.div.addEventListener('click', function() {
			console.log(cardName);
		},false);
	}
	
	addTo(container) {
		container.appendChild(this.div);
	}
}






class GameCard extends BaseCard {
	number = 0;
	origNumber = 0;
	numberText = document.createElement('p');
	category;
	
	constructor(cardName, number, category) {
		super(cardName);
		
		this.category = category;
		
		this.div.appendChild(this.numberText);
		
		this.origNumber = number;
		
		
		
		
		const card = this;
		
		this.div.addEventListener('click', function() {
			if(card.div.classList.contains('selected')) {
				card.div.classList.remove('selected');
				selected.splice(card.number, 1);
				for(let c of selected.slice(card.number, selected.length)) {
					c.number--;
					c.numberText.innerHTML = c.number+1;
				}
				
			} else {
				card.number = selected.length;
				card.numberText.innerHTML = card.number+1;
				card.div.classList.add('selected');
				selected.push(card);
			}
		},false);
	}
}



class BGCard extends BaseCard {
	counter = 0;
	counterText = document.createElement('p');
	
	constructor(cardName) {
		super(cardName);
		
		this.counterText.classList.add('counter');
		this.div.appendChild(this.counterText);
		
		const counterText = this.counterText;
		this.div.addEventListener('click', function() {
			clearAndDispCard(cardName, counterText.innerHTML);
		},false);
	}
	
	removeFrom(container) {
		container.removeChild(this.div);
	}
}

class DispCard extends BaseCard{
	
	counterText = document.createElement('p');
	
	constructor(cardName, counter) {
		super(cardName);
		this.counterText.innerHTML = counter;
		this.counterText.classList.add('counter');
		this.counterText.classList.add('dispCounter');
		this.div.appendChild(this.counterText);
	}
}





class ChooseText {
	selected = false;
	origNumber = 0;
	category = 'chooseText';
	txt = document.createElement('p');
	
	constructor(msg, number) {
		this.txt.innerHTML = msg;
		this.origNumber = number;
		const chooseText = this;
		this.txt.addEventListener('click', function() {
			if(chooseText.selected) {
				for(let ct of selected) {
					chooseText.selected = false;
					ct.txt.classList.remove('selected');
				}
				selected.splice(0,selected.length);
			} else {
				for(let ct of selected) {
					ct.selected = false;
					ct.txt.classList.remove('selected');
				}
				selected.splice(0,selected.length);
				
				chooseText.selected = true;
				chooseText.txt.classList.add('selected');
				selected.push(chooseText);
			}
		},false);
	}
}