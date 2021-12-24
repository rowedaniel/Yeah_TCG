// card funcs
function increaseBreath(target, amount) {
	target.counters.increaseBreath(amount);
}

function increaseRP(target, amount) {
	target.increaseRP(amount);
}

function targetCard(target, targetResolution, conditionOverride=-1) {
	disp.show(target.play.cards, [targetResolution], "target", conditionOverride);
}



function executeCardAction(cardName, cardAction, index, me, you) {
	
	const cmdTable = {
					  "increaseBreath":[2,
										x => (["me", "you"].indexOf(x) !== -1) ? x:false,
										x => (["1","2","3"].indexOf(x) !== -1) ? x:false,
										],
					  "increaseRP":    [2,
										x => (["this"].indexOf(x) !== -1 && me.play.hasCard(cardName, index)) ? "me.play.getCard(cardName, index)":false,
										x => (["1","2","3","4","5","6","7","8","9"].indexOf(x) !== -1) ? x:false,
										],
					  "dealCard":      [1,
										x => (["me", "you"].indexOf(x) !== -1) ? "'"+x+"'":false,
										],
					  "searchDeckCategory": [4,
										x => (["me", "you"].indexOf(x) !== -1) ? "'"+x+"'":false,
										x => (["1","2","3","4","5","6","7","8","9"].indexOf(x) !== -1) ? x:false,
										x => (["common", "rare", "legendary"].indexOf(x) !== -1) ? "'"+x+"'":false,
										x => (["swordsman", "demon"].indexOf(x) !== -1) ? "'"+x+"'":false,
										],
					 };
	const c = cardAction.split(" ");
	let i=0;
	let cmdStr = "";
	let currentCommand = "";
	let currentArgIndex = 0;
	
	console.log("in executeCardAction. Execute, ", c);
	
	while(i < c.length) {
		
		console.log("new keyword:",c[i]);
		
		switch(c[i]) {
			
			
			// commands
			case "increaseBreath":
				cmdStr = "increaseBreath(";
				currentCommand = "increaseBreath";
				currentArgIndex = 0;
				console.log("starting new command:", cmdStr);
				break;
			
			case "increaseRP":
				cmdStr = "increaseRP(";
				currentCommand = "increaseRP";
				currentArgIndex = 0;
				console.log("starting new command:", cmdStr);
				break;
				
			case "drawCard":
				cmdStr = "reqDealCard(";
				currentCommand = "dealCard";
				currentArgIndex = 0;
				console.log("starting new command:", cmdStr);
				break;
				
			case "searchDeckCategory":
				cmdStr = "reqSearchDeckCategory(";
				currentCommand = "searchDeckCategory";
				currentArgIndex = 0;
				console.log("starting new command:", cmdStr);
				break;
				
			
			// arguments
			default:
				// check if this argument satisfies conditions
				if(currentCommand && currentCommand in cmdTable && currentArgIndex < cmdTable[currentCommand][0] && cmdTable[currentCommand][currentArgIndex+1](c[i])) {
					// if yes, keep going with command.
					
					cmdStr += cmdTable[currentCommand][currentArgIndex+1](c[i])+",";
					++currentArgIndex;
					console.log("added argument:", cmdStr);
				} else {
					// if no, reset command.
					console.log("invalid argument, restarting", currentCommand, c[i]);
					cmdStr = "";
					currentCommand = "";
					currentArgIndex = 0;
				}
				break;
			
		}
		
		// attempt execute
		if(currentCommand && currentCommand in cmdTable && currentArgIndex >= cmdTable[currentCommand][0]) {
			console.log("running argument");
			eval(cmdStr+")");
		}
		
		
		++i;
	}
	
}