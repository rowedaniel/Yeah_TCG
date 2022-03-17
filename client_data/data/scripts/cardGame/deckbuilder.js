

// communication init
const socket = io("/cards");


socket.on('ding', function (data) {
    socket.emit("dong", { beat: 1 });
});


// deck submit function

function decksubmit() {
    let elem = document.getElementById("warningdiv");
    if (selectedGoalCards.length !== 3) {
        // you must have *exactly* 3 goal cards in deck.
        elem.style = "animation-name: flashRed;animation-duration: 0.1s;animation-fill-mode: forwards;";
        return;
    }
    socket.emit('reqAddDeck', { name: document.forms['cardForm']['deckName'].value, deck: selectedCards, goals: selectedGoalCards });
    document.forms['cardForm']['deckName'].value = '';
    elem.style = "animation-name: flashGreen;animation-duration: 0.1s;animation-fill-mode: forwards;";
    elem.innerHTML = "Success!";
}

// main stuff
socket.on("resAllStockCards", function (data) {
    addCards(data);
});


addCardToSelection = function (card) {
    let selectiondiv;
    let cardArray;
    if (card.cardType[0] === "goal") {
        selectiondiv = document.getElementById("selectiongoaldiv");
        cardArray = selectedGoalCards;
        if (cardArray.length >= 5 || cardArray.filter(x => x === card.name).length >= 1) { return; }
    } else {
        selectiondiv = document.getElementById("selectiondiv");
        cardArray = selectedCards;
        if (cardArray.filter(x => x === card.name).length >= 3) { return; }
    }

    cardArray.push(card.name);
    const img = new Image(card.width, card.height);
    img.src = card.img.src;
    img.classList.add("slidein");
    img.onclick = function () {
        cardArray.splice(cardArray.indexOf(card.name), 1);
        selectiondiv.removeChild(img);
    }
    selectiondiv.appendChild(img);
}
addCardToDisplay = function (card) {
    const carddiv = document.getElementById("carddiv");
    const img = new Image(card.width, card.height);
    img.src = card.img.src;
    img.classList.add("slidein");
    img.onclick = function () {
        addCardToSelection(card);
    }
    carddiv.appendChild(img);
}


cards = [];
selectedCards = [];
selectedGoalCards = [];
addCards = function (data) {
    for (let card of data) {
        const c = Card(cards, 0, 0, card.name, card.cost, card.img, card.move, card.txtcolor, card.cardType, card.cardAction);
    }
}
addCardsToDisplay = function () {
    for (let c of cards) {
        addCardToDisplay(c);
    }
}




socket.emit("reqAllStockCards", {});

setTimeout(addCardsToDisplay, 500);