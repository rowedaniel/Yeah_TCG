
class Quiz:
    __slots__ = ('questionFilename','answerFilename',
                 'players', 'questions', 'answers')

    def __init__(self, questionFilename, answerFilename):

        self.questionFilename = questionFilename
        self.answerFilename = answerFilename
        
        self.players = {}
        self.questions = ["Type 'start'"]
        self.answers = ["start"]
        self.load_quiz()

    async def add_player(self, sid):
        if sid not in self.players:
            self.players[sid] = 0

    async def remove_player(self, sid):
        del self.players[sid]

    async def get_question(self, sid):
        if sid not in self.players or \
           self.players[sid] >= len(self.questions):
            return ''
        return self.questions[self.players[sid]]

    async def attempt_advance(self, sid, answer):
        if sid not in self.players or \
           answer != self.answers[self.players[sid]]:
            return False
        self.players[sid] += 1
        if self.players[sid] >= len(self.questions):
            self.players[sid] = -1
        return True



    def load_quiz(self):
        with open(self.questionFilename, 'r', encoding='utf-8') as file:
            for line in file:
                self.questions.append(line.rstrip())
                
        with open(self.answerFilename, 'r', encoding='utf-8') as file:
            for line in file:
                self.answers.append(line.rstrip())

    async def add_question(self, sid, question, answer):
        if sid not in self.players or self.players[sid] != -1:
            return False
        
        # add new question/answer to the live list
        self.questions.append(question)
        self.answers.append(answer)

        # save the new question/answer in the corresponding file
        with open(self.questionFilename, 'a', encoding='utf-8') as file:
            file.write('\n'+question)
        with open(self.answerFilename, 'a', encoding='utf-8') as file:
            file.write('\n'+answer)


class QuizManager:

    __slots__ = ( 'sio', 'mainQuiz', 'extraQuiz')

    def __init__(self, sio):
        self.sio = sio
        self.mainQuiz = Quiz('quiz/quizQuestions.txt',
                             'quiz/quizAnswers.txt')
        self.extraQuiz = Quiz('quiz/extraQuizQuestions.txt',
                              'quiz/extraQuizAnswers.txt') 
        
    async def handle_startQuiz(self, sid, data):
        await self.mainQuiz.add_player(sid)
        await self.sio.emit("startQuiz", {}, room=sid)
        
    async def handle_quizAttemptAnswer(self, sid, data):
        # checkpoint 1
        if data['answer'] == 'OBOhcX8B3ruzfvOwFdgQ':
            await self.mainQuiz.remove_player(sid)
            await self.extraQuiz.add_player(sid)
            await self.attempt_advance(self.extraQuiz, sid, 'start')
            
        # check if anwer works for either quiz
        elif not await self.attempt_advance(self.mainQuiz,
                                            sid,
                                            data['answer']) and \
             not await self.attempt_advance(self.extraQuiz,
                                            sid,
                                            data['answer']):
            # if not, signal the player that it was wrong
            await self.sio.emit('quizWrongAnswer', {}, room=sid)
    
    async def handle_quizSubmitQuestion(self, sid, data):
        await self.mainQuiz.add_question(sid,
                                         data['question'],
                                         data['answer'])
        await self.extraQuiz.add_question(sid,
                                          data['question'],
                                          data['answer'])


        

    async def attempt_advance(self, quiz, sid, answer):
        if await quiz.attempt_advance(sid, answer):
            if quiz.players[sid] == -1:
                # finished with quiz
                await self.sio.emit('quizFinish', {}, room=sid)
            else:
                await self.sio.emit('quizRightAnswer',
                        {'question':await quiz.get_question(sid)},
                                    room=sid)
            return True
        return False
                                        
