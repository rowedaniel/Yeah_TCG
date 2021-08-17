import hashlib



class Quiz:
    __slots__ = ('questionFilename','answerFilename',
                 'players', 'questions', 'answers')

    def __init__(self, questionFilename, answerFilename, firstAnswer):

        self.questionFilename = questionFilename
        self.answerFilename = answerFilename
        
        self.players = {}
        self.questions = ["Type 'start'"]
        self.answers = [firstAnswer]
        self.load_quiz()

    async def add_player(self, sid):
        if sid not in self.players:
            self.players[sid] = 0

    async def remove_player(self, sid):
        if sid in self.players:
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

        answer = answer
        
        # add new question/answer to the live list
        self.questions.append(question)
        self.answers.append(answer)

        # save the new question/answer in the corresponding file
        with open(self.questionFilename, 'a', encoding='utf-8') as file:
            file.write('\n'+question)
        with open(self.answerFilename, 'a', encoding='utf-8') as file:
            file.write('\n'+answer)


class QuizManager:

    __slots__ = ( 'sio', 'firstAnswer', 'quizzes', 'changeQuizKeywords')

    def __init__(self, sio):
        self.sio = sio

        self.firstAnswer = self.hash('start')
        self.quizzes = [Quiz('quiz/quizQuestions.txt',
                            'quiz/quizAnswers.txt',
                            self.firstAnswer),
                       Quiz('quiz/extraQuizQuestions.txt',
                            'quiz/extraQuizAnswers.txt',
                            self.firstAnswer),
                       Quiz('quiz/jaycobSecretQuizQuestions.txt',
                            'quiz/jaycobSecretQuizAnswers.txt',
                            self.firstAnswer)
                       ]
        self.changeQuizKeywords = {
            '889ed27c6a43a3efe392fe84cd85a9b211c30c0d':self.quizzes[1],
            '0de7d977fc4fbbc001cec3eff9336d819510e360':self.quizzes[2]
            }

    def hash(self, msg):
        return hashlib.sha1(msg.rstrip().encode()).hexdigest()
        
    async def handle_startQuiz(self, sid, data):
        await self.quizzes[0].add_player(sid)
        await self.sio.emit("startQuiz", {}, room=sid)
        
    async def handle_quizAttemptAnswer(self, sid, data):
        if 'answer' not in data: return
        # checkpoint 1
        
        answer = self.hash(data['answer'])
        
        if answer in self.changeQuizKeywords:
            for quiz in self.quizzes:
                await quiz.remove_player(sid)
            newQuiz = self.changeQuizKeywords[answer]
            await newQuiz.add_player(sid)
            await self.attempt_advance(newQuiz, sid, self.firstAnswer)
            
        # check if anwer works for either quiz
        else:
            rightAnswer = False
            for quiz in self.quizzes:
                if await self.attempt_advance(quiz,
                                              sid,
                                              answer):
                    rightAnswer = True
            if not rightAnswer:
                await self.sio.emit('quizWrongAnswer', {}, room=sid)
    
    async def handle_quizSubmitQuestion(self, sid, data):
        if 'question' not in data or 'answer' not in data: return
        question = data['question']
        answer = self.hash(data['answer'])
        for quiz in self.quizzes:
            await quiz.add_question(sid,
                                    question,
                                    answer)


        

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
                                        
