const fontscale = function(text, s, maxsize) {
	if(!text || text.length===0) {
		return 0;
	}
	return Math.min(Math.floor(4*s/text.length),maxsize);
}

textToLines = function(movetext) {
	movetext += " ";
	const lines = [];
	const noOfLines = 5;
	const linelength = Math.max(Math.floor(movetext.length/noOfLines)+5, 30);
	let linestart = 0;
	let lineend = 0;
	for(let i=0; i<noOfLines; ++i) {
		lineend += linelength;
		if(lineend >= movetext.length) {
			lineend = movetext.length;
		} else {
			while(movetext[lineend] !== " ") {
				--lineend;
			}
		}
		lines.push(movetext.substring(linestart, lineend));
		linestart = lineend+1;
	}
	return lines;
}



// entities
const GameObject = function(entities, x, y, w, h, imgScaleX, imgScaleY, imgsrc) {
	let entity = {x:x,
				  y:y,
				  width:w,
				  height:h,
				  xvel:0,
				  yvel:0,
				  animationX:0,
				  animationY:0,
				  imgScaleX:imgScaleX,
				  imgScaleY:imgScaleY,};
	entity.img = new Image(entity.width, entity.height);
	entity.img.src = imgsrc;
	entity.update = function() {
		entity.x += entity.xvel;
		entity.y += entity.yvel;
	};
	entity.draw = function(c) {
		if((entity.x>c.canvas.width) || (entity.y>c.canvas.height) || (entity.x+entity.width*entity.imgScaleX<0) || (entity.y+entity.height*entity.imgScaleY<0)) {
			return 0;
		}
		c.drawImage(entity.img, 
					entity.animationX*entity.width, 
					entity.animationY*entity.height, 
					entity.width, 
					entity.height, 
					entity.x, 
					entity.y, 
					entity.width*entity.imgScaleX, 
					entity.height*entity.imgScaleY);
	};
	entities.push(entity);
	return entity;
}

const Card = function(entities, x, y, name, cost, imgsrc, movetext, textcolor, cardType, cardAction) {
	const entity = GameObject(entities, x, y, 606, 890, 1, 1, "/data/cards/cardtemplate.png");
	entity.name = name;
	entity.cost = cost;
	
	// checks
	if(imgsrc === "") {
		imgsrc = "/data/cards/default.png"
	}
	
	let cardoutline = "/data/cards/cardtemplate_outline_default.png";
	cardType = cardType.split(" ");
	let cardTypeText = '';
	if((cardType) && ((cardType.indexOf("unit") !== -1) || (cardType.indexOf("fullart") !== -1) || (cardType.indexOf("goal") !== -1))){
		console.log("setting card type: ", cardType);
		cardoutline = "/data/cards/cardtemplate_outline_" + cardType[cardType.length-1] + ".png";
	}
	entity.cardType = cardType;
	for(let word of cardType){
		if(word === 'fullart') {
			break;
		}
		cardTypeText += word+' ';
	}
	
	let costText = "";
	if(cost && cost !== "" && cost.toString) {
		costText += "RP: "+cost.toString();
	}
	
	/*let actionText = "(function(){})";
	if(cardAction && cardAction.length > 0) {
		actionText = cardAction;
	}*/
	entity.cardAction = cardAction;//actionText;
	
	

	// subentity stuff
	const imgOffsets =  [
						 [0, 0, imgsrc], 
						 [0, 0, cardoutline], 
						];
	const textOffsets = [
						[60, 110, fontscale(cardTypeText, 140, 35), cardTypeText],
						[20, 80, fontscale(name, 200, 60), name], 
						[480, 88, fontscale(costText, 60, 60), costText], 
						];
	const subentities = [];
	
	for(let i = 0; i<imgOffsets.length; ++i) {
		GameObject(subentities, x+imgOffsets[i][0], y+imgOffsets[i][1], 606, 890, 1, 1, imgOffsets[i][2]);
	}
	
	for(let i = 0; i<textOffsets.length; ++i) {
		Text(subentities, x+textOffsets[i][0], y+textOffsets[i][1], textOffsets[i][2]+"px Shintaku", textcolor, textOffsets[i][3]);
	}

	
	// bottom text
	const lines = textToLines(movetext);
	let movetextX = 20;
	let movetextY = 600;
	let bottomtextsize = fontscale(lines[0], 280, 60);
	for(let line of lines) {
		if(line && line.length > 1) {
			bottomtextsize = Math.min(fontscale(line, 320, 60), bottomtextsize);
		}
	}
	for(let txt of lines) {
		textOffsets.push([movetextX, movetextY, bottomtextsize]);
		Text(subentities, x+movetextX, y+movetextY, bottomtextsize+"px Shintaku", textcolor, txt);
		movetextY += bottomtextsize*1.2;
	}
	
	entity.finishedinit = false;
	entity.lateinit = function() {
		entity.finishedinit = true;
		const x = entity.x;
		const y = entity.y;
		entity.x = 0;
		entity.y = 0;
		// pack it to an image (image compositing?)
		const tmpCanvas = document.createElement("canvas");
		tmpCanvas.width = entity.width;
		tmpCanvas.height = entity.height;
		let tmpCtx = tmpCanvas.getContext("2d");
		entity.draw(tmpCtx);
		for(let i in subentities) {
			//setSubentityPosition(i);
			subentities[i].draw(tmpCtx);
		}
		entity.img.src = tmpCanvas.toDataURL("image/png");
		entity.x = x;
		entity.y = y;
	}
	setTimeout(entity.lateinit, 200);
	
	
	const setSubentityPosition = function(e) {	
		subentities[e].x = subentityOffsets[e][0];//*entity.imgScaleX;
		subentities[e].y = subentityOffsets[e][1];//*entity.imgScaleY;
	}
	
	
	
	entity.resize = function(scaleX, scaleY) {
		if(!entity.finishedinit) {
			setTimeout(function(){entity.resize(scaleX, scaleY);},100);
			return;
		}
		entity.imgScaleX = scaleX;
		entity.imgScaleY = scaleY;
		
		
	}
	
	return entity;
}

const Text = function(entities, x, y, font, color, text) {
	const entity = {x:x,
				    y:y,
				    text:text,
				    font:font,};
	if(!color) {
		entity.color = "#000000";
	}
	entity.update = function() {};
	entity.draw = function(c) {
		if(entity.text.length===0 || (entity.x+entity.width<0 || entity.y+entity.height<0 || entity.x>c.canvas.width || entity.y>c.canvas.height)) {
			return 0;
		}
		c.save();
		c.font = entity.font;
		
		//TODO: make this the opposite color as font color.
		c.strokeStyle = '#FFFFFF';
		c.lineWidth = 4;
		c.strokeText(entity.text, entity.x, entity.y);
		c.fillStyle = color;
		c.fillText(entity.text, entity.x, entity.y);
		c.restore();
	};
	entity.getScale = function() {
		entity.width = entity.text.length*parseInt(entity.font.split("px")[0]);
		entity.height = parseInt(entity.font.split("px")[0])*1.2;
	}
	entity.getScale();
	
	
	entities.push(entity);
	return entity;
}

const Rect = function(entities, x, y, w, h, color) {
	const entity = {x:x,
				  y:y,
				  width:w,
				  height:h};
	entity.update = function(){}
	entity.draw = function(c) {
		c.save();
		c.fillStyle = color;
		c.fillRect(entity.x,entity.y,entity.width,entity.height);
		c.restore();
	}
}

