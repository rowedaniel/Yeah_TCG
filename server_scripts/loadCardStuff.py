


def loadCards():
    cards = []
    with open('./cards/cards.txt') as f:
        for line in f.readlines():
            args = line.split('|')
            cards.append({'name':args[0],
                          'cost':args[1],
                          'img':args[2],
                          'move':args[3],
                          'txtcolor':args[4],
                          'cardType':args[5],
                          'cardAction':args[6]})
    return cards

def saveCard(card):
    with open('./cards/cards.txt', 'a') as f:
        f.write('|'.join([
                      card['name'],
                      card['cost'],
                      card['img'],
                      card['move'],
                      card['txtcolor'],
                      card['cardType'],
                      card['cardAction']])+'\n')

def loadDecks():
    decks = {'k':{ 'deck': ['Dragon King Hades',
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
                  'goals': ['Overwhelming Attack',
                            'Overwhelming Numbers',
                            'Overwhelming Defense']},
             'j':{ 'deck': ['Tyranny',
                            'Tyranny',
                            'Tyranny',
                            'Sharpen Swords',
                            'Sharpen Swords',
                            'Sharpen Swords',
                            'Breath User Jaycob',
                            'Breath User Jaycob',
                            'Breath User Jaycob',
                            'Skinny Jaycob',
                            'Skinny Jaycob',
                            'Skinny Jaycob',
                            'Ajax the Spearman',
                            'Ajax the Spearman',
                            'Ajax the Spearman',
                            'Chad Squire',
                            'Chad Squire',
                            'Chad Squire',
                            'Mr. Deffrey Javis',
                            'Mr. Deffrey Javis',
                            'Mr. Deffrey Javis',
                            'Call of Hades',
                            'Call of Hades',
                            'Call of Hades',
                            'Lucifer the Demon King'], 
                  'goals': ['Overwhelming Attack',
                            'Overwhelming Numbers',
                            'Overwhelming Defense']},
             }
    return decks

def saveDecks(deck):
    return

