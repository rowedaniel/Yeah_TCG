

// communication init
const socket = io("/cards");


socket.on('ding', function (data) {
    socket.emit("dong", { beat: 1 });
});


// card submit function


socket.on("resAllStockCards", function (data) {
    console.log("AAAA");
    for (let c of data) {
        addCard(c);
    }
    setTimeout(function () {
        for (let c of cards) {
            dispCard(c);
        }
    }, 200);
});

/*const buttonDownFunctions = [];
document.onkeydown = function(e) {
    for(let f of buttonDownFunctions) {
        f(e);
    }
}*/

let delay = 0;
const cards = [];
addCard = function (card) {
    const c = Card([], 0, 0, card.name, card.cost, card.img, card.move, card.txtcolor, card.cardType, card.cardAction);
    c.img.style.animationDelay = delay + "ms";
    delay += 100;
    cards.push(c.img);
}

dispCard = function (card) {
    document.getElementById("carddiv").appendChild(card);
}


socket.emit("reqAllStockCards", {});
console.log("BBBBB");