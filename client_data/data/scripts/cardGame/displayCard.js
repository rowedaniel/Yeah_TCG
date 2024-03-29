﻿// communication init
const socket = io("/cards");

socket.on('ding', function (data) {
    socket.emit("dong", { beat: 1 });
});



// card submit function

/*socket.on('serverAddCard', function(data) {
    addCard(data);
});*/


const initCardFunctions = [];
socket.on("resAllStockCards", function (data) {
    for (let f of initCardFunctions) {
        f(data);
    }
});

const buttonDownFunctions = [];
document.onkeydown = function (e) {
    for (let f of buttonDownFunctions) {
        f(e);
    }
}

const buttonUpFunctions = [];
document.onkeyup = function (e) {
    for (let f of buttonUpFunctions) {
        f(e);
    }
}
/*
const mainLoopFunctions = [];
const mainLoop = function(timestamp) {
    for(let f of mainLoopFunctions) {
        f(timestamp);
    }
    window.requestAnimationFrame(mainLoop);
}
	
	
	
// game init
const cardScroll = function() {
    const canvas = document.getElementById("gamecanvas");
    const ctx = canvas.getContext("2d");
    canvas.width = window.innerWidth-30;
    canvas.height = window.innerHeight-50;
    window.onresize = function() {
        canvas.width = window.innerWidth-50;
        canvas.height = window.innerHeight-50;
    }
	
	
    //const entities = [];
    const cards = [];
    let cardX = 0;
    let cardY = 100;
    let scrollingLeft = false;
    let scrollingRight = false;
	
	
	
    // late init
    addCard = function(data) {
        let c = Card(cards, cardX, cardY, data.name, data.cost, data.img, data.move, data.txtcolor, data.cardType, data.cardAction);
        c.resize(0.4,0.4);
        cardX -= c.width;//*1.2;
    }
	
    initCardFunctions.push(function(data) {
        for(let c of data) {
            addCard(c);
            break;
        }
    });
	
    /*
    scrollCard = function(c) {
        if(c.x > canvas.width) {
            c.x = cardX;
        }
        if(c.x < cardX) {
            c.x = canvas.width - 1;
        }
    	
        if(scrollingLeft) {
            c.xvel -= 1;
        } else if(scrollingRight) {
            c.xvel += 1;
        }else if(!scrollingLeft && !scrollingRight) {
            c.xvel *= 0.95;
        }
    }
	
	
    // input 
    buttonDownFunctions.push(function(e){
        if(e.key === 'a' || e.key === 'ArrowLeft') {
            scrollingLeft = true;
        } else if(e.key === 'd' || e.key === 'ArrowRight') {
            scrollingRight = true;
        } else if(e.key === 'ArrowUp') {
            for(let c of cards) {
                c.yvel = -4;
            }
        } else if(e.key === 'ArrowDown') {
            for(let c of cards) {
                c.yvel = 4;
            }
        } else {
            console.log(e.key);
        }
    });
	
    buttonUpFunctions.push(function(e){
        if(e.key === 'a' || e.key === 'ArrowLeft') {
            scrollingLeft = false;
        } else if(e.key === 'd' || e.key === 'ArrowRight') {
            scrollingRight = false;
        } else if(e.key === 'ArrowUp') {
            for(let c of cards) {
                c.yvel = 0;
            }
        } else if(e.key === 'ArrowDown') {
            for(let c of cards) {
                c.yvel = 0;
            }
        } else {
            console.log(e.key);
        }
    });
	
    let mX, mY, prevMx, prevMy, mouseDown;
    document.onmousedown = function(e) {
        mouseDown = true;
        prevMx = mX;
        mX = e.clientX;
        //console.log(e.clientX, e.clientY);
    }
	
    document.onmousemove = function(e) {
        if(!mouseDown || !e || !e.clientX) {return;}
        prevMx = mX;
        mX = e.clientX;
    	
        for(let c of cards) {
            c.xvel = mX-prevMx;
            //console.log(e.clientX, c.xvel, c.img);
        }
    }
	
    document.onmouseup = function(e) {
        mouseDown = false;
        scrollingLeft = false;
        scrollingRight = false;
    }

    let card;
    mainLoopFunctions.push(function(timestamp) {
        ctx.clearRect(0,0,canvas.width,canvas.height);
        for(card of cards) {
            //card.update();
            //scrollCard(card);
            card.draw(ctx);
        }
    });
    console.log(cards);
}
cardScroll();

*/



const singleCard = function () {
    const img = document.getElementById("bigimage");

    const cards = [];


    let currentCard = 0;
    const cycleCard = function (inc) {
        currentCard += inc;
        currentCard %= cards.length;
        img.src = cards[currentCard].src;
    }


    initCardFunctions.push(function (data) {
        for (let cardData of data) {
            const c = Card([], 0, 0, cardData.name, cardData.cost, cardData.img, cardData.move, cardData.txtcolor, cardData.cardType, cardData.cardAction);
            cards.push(c.img);
        }
        const firstLoad = function () {
            cycleCard(0);
            if (cards[0].src.substr(-16) === "cardtemplate.png") {
                setTimeout(firstLoad, 100);
            }
        }
        firstLoad();
    });

    img.onclick = function () { cycleCard(1); };

    buttonDownFunctions.push(function (e) {
        if (e.key === "k") {
            if (Math.random() < 0.9) {
                cycleCard(1);
            } else {
                cycleCard(-1);
            }
        }
    });
}
singleCard();


socket.emit("reqAllStockCards", {});
	//requestAnimationFrame(mainLoop);