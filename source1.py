import sys
import random
import string
import PyQt5.QtCore
from PyQt5.QtGui import QPixmap, QFont, QColor, QBrush, QTextCursor
from PyQt5.QtWidgets import QWidget, QSlider, QLabel, QPushButton, \
    QVBoxLayout, QHBoxLayout, QGridLayout, QCheckBox, QMessageBox, \
    QTextEdit, QTableWidget, QProgressBar, QAbstractScrollArea, \
    QAbstractItemView, QLCDNumber, QTableWidgetItem, QApplication


nElements = 20
rowBoxChecked = False
columnBoxChecked = False
diagonalBoxChecked = False


class StartMenu(QWidget):

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Поиск слова")

        self.slider = QSlider(PyQt5.QtCore.Qt.Horizontal)
        self.sliderLabel = QLabel()
        self.configSlider()
        self.slider.valueChanged.connect(self.nRowDisplayChanged)

        self.difficultyLevel = QLabel()
        self.nRowDisplay = QLabel()
        self.configElementDisplay()

        buttonStart = QPushButton('Начать')
        buttonStart.clicked.connect(self.onClickStart)

        buttonQuit = QPushButton('Выйти')
        buttonQuit.clicked.connect(self.onClickQuit)

        logoImage = QLabel()
        logoImage.setGeometry(10, 10, 10, 10)
        logoImage.setPixmap(QPixmap("logo.png").scaledToWidth(500))

        hBox = QHBoxLayout()
        hBox.addWidget(buttonQuit)
        hBox.addWidget(buttonStart)

        grid = QGridLayout()
        self.setLayout(grid)
        grid.addWidget(logoImage, 0, 0)
        grid.addWidget(self.sliderLabel, 1, 0)
        grid.addWidget(self.difficultyLevel, 2, 0)
        grid.addWidget(self.slider, 3, 0)
        grid.addWidget(self.nRowDisplay, 4, 0)
        grid.addLayout(hBox, 5, 0)

        self.show()

    def configSlider(self):
        self.slider.setTickPosition(QSlider.TicksBelow)
        self.slider.setRange(10, 40)
        self.slider.setTickInterval(5)
        self.slider.setSingleStep(5)
        self.slider.setValue(nElements)

        self.sliderLabel.setText("Сколько рядов вы хотите?")
        self.sliderLabel.setAlignment(PyQt5.QtCore.Qt.AlignCenter)
        self.sliderLabel.setFont(QFont("Futura", 20))

    def configElementDisplay(self):
        self.difficultyLevel.setAlignment(PyQt5.QtCore.Qt.AlignCenter)
        self.difficultyLevel.setText("Средний")
        self.difficultyLevel.setStyleSheet("color: rgb(255, 193, 37)")

        self.nRowDisplay.setText(str(self.slider.value()))
        self.nRowDisplay.setAlignment(PyQt5.QtCore.Qt.AlignCenter)
        self.nRowDisplay.setFont(QFont("Futura", 30))
        self.nRowDisplay.setStyleSheet("color: rgb(0, 170, 240)")

    def getSliderValue(self):
        global nElements
        nElements = self.slider.value()

    def nRowDisplayChanged(self):
        self.nRowDisplay.setText(str(self.slider.value()))
        if 10 <= self.slider.value() < 20:
            self.difficultyLevel.setText("Легкий")
            self.difficultyLevel.setStyleSheet("color: rgb(67, 205, 128)")
        elif 20 <= self.slider.value() < 30:
            self.difficultyLevel.setText("Средний")
            self.difficultyLevel.setStyleSheet("color: rgb(255, 193, 37)")
        else:
            self.difficultyLevel.setText("Тяжелый")
            self.difficultyLevel.setStyleSheet("color: rgb(255, 99, 71)")

    def onClickStart(self):
        self.getSliderValue()
        self.close()
        self.openApp = App()
        self.openApp.show()

    def onClickQuit(self):
        sys.exit()




class App(QWidget):


    def __init__(self):
        super().__init__()
        self.wordBank = ""
        self.wordBankSplit = []
        self.wordSelected = ""
        self.xVisited = []
        self.yVisited = []
        self.inRow = 0
        self.progressValue = 0
        self.wordsCompleted = []
        self.timeFlag = 2
        self.initUI()

    def initUI(self):
        title = 'Поиск слова'
        self.setWindowTitle(title)

        self.wordBankBox = QTextEdit()
        self.tableWidget = QTableWidget()
        self.progress = QProgressBar()
        self.timer = PyQt5.QtCore.QTimer()

        self.createTable()
        self.createWordBank()
        self.createProgressBar()
        self.createTimer()
        self.mouseTracking()

        wordBankTitle = QLabel()
        wordBankTitle.setText("       Слова")
        font = QFont()
        font.setBold(True)
        wordBankTitle.setFont(font)

        buttonClear = QPushButton('Очистить', self)
        buttonClear.setToolTip('Это очищает ваш выбор слова.')
        buttonClear.clicked.connect(self.onClickClear)

        buttonQuit = QPushButton('Выйти', self)
        buttonQuit.setToolTip('Это кнопка Выйти из игры. Вы потеряете весь прогресс.')
        buttonQuit.clicked.connect(self.onClickQuit)

        self.buttonPause = QPushButton('Пауза')
        self.buttonPause.setToolTip('Эта кнопка ставит игру на паузу.')
        self.buttonPause.clicked.connect(self.onClickPause)

        vBox = QVBoxLayout()
        vBox.addWidget(wordBankTitle)
        vBox.addWidget(self.wordBankBox)
        vBox.addWidget(buttonClear)
        vBox.addWidget(self.buttonPause)
        vBox.addWidget(buttonQuit)

        self.grid = QGridLayout()
        self.grid.addLayout(vBox, 0, 1)
        self.grid.addWidget(self.tableWidget, 0, 0)
        self.grid.addWidget(self.progress, 1, 0)
        self.grid.addWidget(self.LCD, 1, 1)

        self.setLayout(self.grid)

        self.tableWidget.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)

        self.show()

    def createTable(self):
        generateAll = False

        global rowBoxChecked
        global columnBoxChecked
        global diagonalBoxChecked
        cyrillic_lower_letters = 'АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ'

        f = open('words_alpha.txt',"r", encoding='utf-8')
        generateAll = True

        wordFileContent = f.readlines()
        wordFileContent = [x.strip() for x in wordFileContent]

        self.tableWidget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tableWidget.setRowCount(nElements)
        self.tableWidget.setColumnCount(nElements)

        for y in range(0, nElements):
            for x in range(0, nElements):
                self.tableWidget.setItem(x, y, QTableWidgetItem(random.choice(cyrillic_lower_letters)))
                self.tableWidget.setColumnWidth(x, 20)
                self.tableWidget.setRowHeight(y, 20)

        def generateRow(self):
            col = 0
            row = 0
            lastColPosition = 0
            wordDuplicate = False
            while row < nElements:
                while col < nElements:
                    col = random.randint(lastColPosition, nElements)
                    word = wordFileContent[random.randint(0, len(wordFileContent) - 1)]
                    while len(word) < 3:
                        word = wordFileContent[random.randint(0, len(wordFileContent) - 1)]
                    for x in self.wordBank.split():
                        if x == word:
                            wordDuplicate = True
                    if not wordDuplicate:
                        if nElements - col > len(word):
                            lastColPosition = len(word) + col
                            self.wordBank += word + "\n"
                            for x in word:
                                self.tableWidget.setItem(row, col, QTableWidgetItem(x))
                                col += 1
                            col = nElements
                    wordDuplicate = False
                row += 3
                col = 0
                lastColPosition = 0

        def generateCol(self):
            col = 0
            row = 0
            lastRowPosition = 0
            decide = 0
            wordDuplicate = False
            while col < nElements:
                while row < nElements:
                    row = random.randint(lastRowPosition, nElements)
                    word = wordFileContent[random.randint(0, len(wordFileContent) - 1)]
                    while len(word) < 3:
                        word = wordFileContent[random.randint(0, len(wordFileContent) - 1)]
                    for x in self.wordBank.split():
                        if x == word:
                            wordDuplicate = True
                    if not wordDuplicate:
                        if nElements - row > len(word):
                            for k in range(row, row + len(word)):
                                if self.tableWidget.item(k, col).text().islower():
                                    decide += 1
                            if decide == 0:
                                lastRowPosition = len(word) + row
                                self.wordBank += word + "\n"
                                for y in word:
                                    self.tableWidget.setItem(row, col, QTableWidgetItem(y))
                                    row += 1
                            decide = 0
                    wordDuplicate = False
                col += 3
                row = 0
                lastRowPosition = 0

        def generateForwardDiag(self):
            col = 0
            row = 0
            wordCount = 0
            decide = 0
            wordDuplicate = False
            while row < nElements:
                while col < nElements:
                    word = wordFileContent[random.randint(0, len(wordFileContent) - 1)]
                    while len(word) < 3:
                        word = wordFileContent[random.randint(0, len(wordFileContent) - 1)]
                    for x in self.wordBank.split():
                        if x == word:
                            wordDuplicate = True
                    if not wordDuplicate:
                        tempRow = row
                        tempCol = col
                        while tempRow < nElements and tempCol < nElements and wordCount < len(word):
                            if self.tableWidget.item(tempRow, tempCol).text().islower():
                                decide += 1
                            tempRow += 1
                            tempCol += 1
                            wordCount += 1
                        tempRow = row
                        tempCol = col
                        if decide == 0 and (len(word) + tempCol) < nElements and (len(word) + tempRow) < nElements:
                            self.wordBank += word + "\n"
                            for y in word:
                                self.tableWidget.setItem(tempRow, tempCol, QTableWidgetItem(y))
                                tempCol += 1
                                tempRow += 1
                    decide = 0
                    wordCount = 0
                    col += 1
                    wordDuplicate = False
                row += 1
                col = 0

        def generateBackwardDiag(self):
            col = nElements - 1
            row = 0
            wordCount = 0
            decide = 0
            wordDuplicate = False
            while row < nElements:
                while col >= 0:
                    word = wordFileContent[random.randint(0, len(wordFileContent) - 1)]
                    while len(word) < 3:
                        word = wordFileContent[random.randint(0, len(wordFileContent) - 1)]
                    for x in self.wordBank.split():
                        if x == word:
                            wordDuplicate = True
                    if not wordDuplicate:
                        tempRow = row
                        tempCol = col
                        while tempRow < nElements and tempCol >= 0 and wordCount < len(word):
                            if self.tableWidget.item(tempRow, tempCol).text().islower():
                                decide += 1
                            tempRow += 1
                            tempCol -= 1
                            wordCount += 1
                        tempRow = row
                        tempCol = col
                        if decide == 0 and (tempCol - len(word)) > 0 and (len(word) + tempRow) < nElements:
                            self.wordBank += word + "\n"
                            for y in word:
                                self.tableWidget.setItem(tempRow, tempCol, QTableWidgetItem(y))
                                tempRow += 1
                                tempCol -= 1
                    decide = 0
                    wordCount = 0
                    col -= 1
                    wordDuplicate = False
                row += 1
                col = nElements - 1

        if generateAll:
            generateRow(self)
            generateCol(self)
            generateForwardDiag(self)
            generateBackwardDiag(self)
        else:
            if rowBoxChecked:
                generateRow(self)
                rowBoxChecked = False
            if columnBoxChecked:
                generateCol(self)
                columnBoxChecked = False
            if diagonalBoxChecked:
                generateForwardDiag(self)
                generateBackwardDiag(self)
                diagonalBoxChecked = False

        for y in range(0, nElements):
            for x in range(0, nElements):
                letter = self.tableWidget.item(x, y).text().lower()
                self.tableWidget.setItem(x, y, QTableWidgetItem(letter))
                self.tableWidget.item(x, y).setTextAlignment(PyQt5.QtCore.Qt.AlignCenter)

        self.tableWidget.horizontalHeader().hide()
        self.tableWidget.verticalHeader().hide()
        self.tableWidget.setShowGrid(False)
        self.tableWidget.clicked.connect(self.onClickLetter)

    def createWordBank(self):
        self.wordBankSplit = self.wordBank.split()
        self.wordBankSplit.sort()
        for x in self.wordBankSplit:
            self.wordBankBox.append(x)
        self.wordBankBox.setReadOnly(True)
        self.wordBankBox.setMaximumWidth(120)
        font = QFont()
        font.setFamily('Arial')
        self.wordBankBox.setFont(font)
        self.wordBankBox.moveCursor(QTextCursor.Start)

    def strikeWord(self, word):
        newWord = ""
        for x in word:
            newWord += x + '\u0336'
        self.wordBankSplit = [newWord if i == word else i for i in self.wordBankSplit]
        self.wordBankBox.setText("")
        for x in self.wordBankSplit:
            self.wordBankBox.append(x)
        self.wordBankBox.show()
        self.wordBankBox.moveCursor(QTextCursor.Start)

    def mouseTracking(self):
        self.currentHover = [0, 0]
        self.tableWidget.setMouseTracking(True)
        self.tableWidget.cellEntered.connect(self.cellHover)

    def cellHover(self, row, column):
        item = self.tableWidget.item(row, column)
        oldItem = self.tableWidget.item(self.currentHover[0], self.currentHover[1])
        mouseTracker1 = True
        mouseTracker2 = True
        for x in range(len(self.xVisited)):
            if self.xVisited[x] == row and self.yVisited[x] == column:
                mouseTracker1 = False
            if self.currentHover[0] == self.xVisited[x] and self.currentHover[1] == self.yVisited[x]:
                mouseTracker2 = False
        if mouseTracker1:
            if self.currentHover != [row, column]:
                if item.text().islower():
                    item.setBackground(QBrush(QColor('yellow')))
                if oldItem.text().islower() and mouseTracker2:
                    oldItem.setBackground(QBrush(QColor('white')))
        elif mouseTracker2:
            oldItem.setBackground(QBrush(QColor('white')))
        self.currentHover = [row, column]

    def onClickLetter(self):
        self.wordSelected = ""
        wordBankSplitOriginal = self.wordBank.split()
        selectionTracker = True
        selectionCorrectness = 0
        word = ""
        listX = []
        listY = []

        for currentQTableWidgetItem in self.tableWidget.selectedItems():
            if self.tableWidget.item(currentQTableWidgetItem.row(), currentQTableWidgetItem.column()).text().isupper():
                letter = self.tableWidget.item(currentQTableWidgetItem.row(),
                                               currentQTableWidgetItem.column()).text().lower()
                self.tableWidget.setItem(currentQTableWidgetItem.row(), currentQTableWidgetItem.column(),
                                         QTableWidgetItem(letter))
                self.tableWidget.clearSelection()
            else:
                for currentQTableWidgetItem in self.tableWidget.selectedItems():
                    for x in range(0, len(self.xVisited)):
                        if currentQTableWidgetItem.row() == self.xVisited[x] and currentQTableWidgetItem.column() == \
                                self.yVisited[x]:
                            selectionTracker = False
                    if selectionTracker:
                        letter = self.tableWidget.item(currentQTableWidgetItem.row(),
                                                       currentQTableWidgetItem.column()).text().upper()
                        self.tableWidget.setItem(currentQTableWidgetItem.row(), currentQTableWidgetItem.column(),
                                                 QTableWidgetItem(letter))
                for currentQTableWidgetItem in self.tableWidget.selectedItems():
                    if selectionTracker:
                        self.tableWidget.item(currentQTableWidgetItem.row(),
                                              currentQTableWidgetItem.column()).setBackground(QColor(216, 191, 216))
                for currentQTableWidgetItem in self.tableWidget.selectedItems():
                    if selectionTracker:
                        self.tableWidget.item(currentQTableWidgetItem.row(),
                                              currentQTableWidgetItem.column()).setTextAlignment(
                            PyQt5.QtCore.Qt.AlignCenter)
                    self.tableWidget.clearSelection()

        for x in range(0, nElements):
            for y in range(0, nElements):
                if self.tableWidget.item(x, y).text().isupper():
                    self.wordSelected += self.tableWidget.item(x, y).text()
                    listX.append(x)
                    listY.append(y)
        for x in wordBankSplitOriginal:
            if x == self.wordSelected.lower():
                selectionCorrectness += 1
                word = x
        if selectionCorrectness == 1:
            for i in range(1, len(listY)):
                if listY[i - 1] == listY[i] - 1 and listX[i - 1] == listX[i]:
                    self.inRow += 1
                if self.inRow == len(listY) - 1:
                    selectionCorrectness += 1
                    self.inRow = 0
        if selectionCorrectness == 1:
            for i in range(1, len(listY)):
                if listX[i - 1] == listX[i] - 1 and listY[i - 1] == listY[i]:
                    self.inRow += 1
                if self.inRow == len(listY) - 1:
                    selectionCorrectness += 1
                    self.inRow = 0
        if selectionCorrectness == 1:
            for i in range(1, len(listY)):
                if listX[i - 1] == listX[i] - 1 and listY[i - 1] == listY[i] - 1:
                    self.inRow += 1
                if self.inRow == len(listY) - 1:
                    selectionCorrectness += 1
                    self.inRow = 0
        if selectionCorrectness == 1:
            for i in range(1, len(listY)):
                if listX[i - 1] == listX[i] - 1 and listY[i - 1] == listY[i] + 1:
                    self.inRow += 1
                if self.inRow == len(listY) - 1:
                    selectionCorrectness += 1
                    self.inRow = 0

        if selectionCorrectness == 2:
            wordIndex = self.wordSelected.find(word)
            self.progressValue += 1
            self.setProgressBar()
            self.strikeWord(word)
            self.wordsCompleted.append(word)
            for i in range(wordIndex, wordIndex + len(word)):
                letterI = self.tableWidget.item(listX[i], listY[i]).text().lower()
                self.tableWidget.setItem(listX[i], listY[i], QTableWidgetItem(letterI))
            for i in range(wordIndex, wordIndex + len(word)):
                self.tableWidget.item(listX[i], listY[i]).setBackground(QColor(144, 238, 144))
                self.xVisited.append(listX[i])
                self.yVisited.append(listY[i])
            for i in range(wordIndex, wordIndex + len(word)):
                self.tableWidget.item(listX[i], listY[i]).setTextAlignment(PyQt5.QtCore.Qt.AlignCenter)

    def onClickClear(self):
        self.wordSelected = ""
        for x in range(0, nElements):
            for y in range(0, nElements):
                if self.tableWidget.item(x, y).text().isupper():
                    letterI = self.tableWidget.item(x, y).text().lower()
                    self.tableWidget.setItem(x, y, QTableWidgetItem(letterI))
                    self.tableWidget.item(x, y).setTextAlignment(PyQt5.QtCore.Qt.AlignCenter)

    def onClickQuit(self):
        quitMessage = QMessageBox()
        quitMessage = QMessageBox.question(self, "Выйти", "Вы уверены, что хотите нажать кнопку Выйти?",
                                           QMessageBox.No | QMessageBox.Yes)
        if quitMessage == QMessageBox.Yes:
            sys.exit()
        else:
            pass

    def createProgressBar(self):
        self.progress.setRange(0, len(self.wordBank.split()))
        self.progress.setToolTip("Показывает ваш прогресс")

    def setProgressBar(self):
        self.progress.setValue(self.progressValue)

    def createTimer(self):
        self.timer.timeout.connect(self.Time)
        self.timer.start(1000)
        self.time = PyQt5.QtCore.QTime(0, 0, 0)

        self.LCD = QLCDNumber()
        self.LCD.display(self.time.toString("hh:mm:ss"))
        self.LCD.setSegmentStyle(QLCDNumber.Flat)

    def Time(self):
        self.time = self.time.addSecs(1)
        self.LCD.display(self.time.toString("hh:mm:ss"))

        if len(self.wordsCompleted) == len(self.wordBankSplit):
            self.timer.stop()
            self.endTime = self.time.toString("hh:mm:ss")
            self.addHighScore()
            self.close()
            self.openHighscoreMenu = HighScoreMenu()
            self.openHighscoreMenu.show()

    def onClickPause(self):
        if self.timeFlag % 2 == 0:
            self.timer.stop()
            self.timeFlag += 1
            self.tableWidget.hide()
            self.buttonPause.setText("Убрать с паузы")
        else:
            self.timer.start()
            self.timeFlag += 1
            self.tableWidget.show()
            self.tableWidget.clearSelection()
            self.buttonPause.setText("Поставить на паузу")

    def addHighScore(self):
        with open("highscores.txt", "a") as highscoreFile:
            if 10 <= nElements <= 19:
                highscoreFile.write("Легком\n")
            elif 20 <= nElements <= 29:
                highscoreFile.write("Среднем\n")
            else:
                highscoreFile.write("Тяжелом\n")
            highscoreFile.write(str(self.endTime) + "\n")


class HighScoreMenu(QWidget):

    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        self.setWindowTitle("Поиск слова")

        self.contents = ""

        with open("highscores.txt", "r") as highscoreFile:
            self.contents = highscoreFile.readlines()
            self.contents = [x.strip() for x in self.contents]

        self.easyBoard = QTextEdit()
        self.easyBoard.setReadOnly(True)
        self.easyBoard.setMaximumWidth(150)
        self.easyBoard.setAlignment(PyQt5.QtCore.Qt.AlignCenter)
        self.mediumBoard = QTextEdit()
        self.mediumBoard.setReadOnly(True)
        self.mediumBoard.setMaximumWidth(150)
        self.mediumBoard.setAlignment(PyQt5.QtCore.Qt.AlignCenter)
        self.hardBoard = QTextEdit()
        self.hardBoard.setReadOnly(True)
        self.hardBoard.setMaximumWidth(150)
        self.hardBoard.setAlignment(PyQt5.QtCore.Qt.AlignCenter)

        titleLabel = QLabel()
        titleLabel.setText("Лучшие результаты")
        titleLabel.setAlignment(PyQt5.QtCore.Qt.AlignCenter)
        titleLabel.setFont(QFont("Futura", 30))
        easyLabel = QLabel()
        easyLabel.setText("Легкий режим")
        easyLabel.setAlignment(PyQt5.QtCore.Qt.AlignCenter)
        easyLabel.setToolTip("Игра находится в простом режиме, если вы выбрали ряды 10-19.")
        mediumLabel = QLabel()
        mediumLabel.setText("Средний режим")
        mediumLabel.setAlignment(PyQt5.QtCore.Qt.AlignCenter)
        mediumLabel.setToolTip("Игра находится в среднем режиме, если вы выбрали ряды 20-29.")
        hardLabel = QLabel()
        hardLabel.setText("Тяжелый режим")
        hardLabel.setAlignment(PyQt5.QtCore.Qt.AlignCenter)
        hardLabel.setToolTip("Игра находится в сложном режиме, если вы выбрали ряды 30-40.")

        for x in range(0, len(self.contents), 2):
            if self.contents[x] == "Легком":
                self.addEasyBoard(self.contents[x + 1])
            if self.contents[x] == "Среднем":
                self.addMediumBoard(self.contents[x + 1])
            if self.contents[x] == "Тяжелом":
                self.addHardBoard(self.contents[x + 1])

        self.buttonStartOver = QPushButton()
        self.buttonStartOver.setText("Сыграть ещё раз")
        self.buttonStartOver.clicked.connect(self.onClickStartOver)

        self.buttonQuit = QPushButton()
        self.buttonQuit.setText("Выйти")
        self.buttonQuit.clicked.connect(self.onClickQuit)


        self.createHighScoreDisplay()

        HBoxLabel = QHBoxLayout()
        HBoxLabel.addWidget(easyLabel)
        HBoxLabel.addWidget(mediumLabel)
        HBoxLabel.addWidget(hardLabel)
        HBox = QHBoxLayout()
        HBox.addWidget(self.easyBoard)
        HBox.addWidget(self.mediumBoard)
        HBox.addWidget(self.hardBoard)
        HBoxButton = QHBoxLayout()
        HBoxButton.addWidget(self.buttonQuit)
        HBoxButton.addWidget(self.buttonStartOver)
        self.grid = QGridLayout()
        self.setLayout(self.grid)
        self.grid.addWidget(titleLabel, 0, 0)
        self.grid.addLayout(HBoxLabel, 1, 0)
        self.grid.addLayout(HBox, 2, 0)
        self.grid.addWidget(self.currentScore, 3, 0)
        self.grid.addWidget(self.highScore, 4, 0)
        self.grid.addLayout(HBoxButton, 5, 0)

        self.show()

    def addEasyBoard(self, score):
        self.easyBoard.append(score)

    def addMediumBoard(self, score):
        self.mediumBoard.append(score)

    def addHardBoard(self, score):
        self.hardBoard.append(score)

    def onClickStartOver(self):
        self.close()
        self.openStartMenu = StartMenu()
        self.openStartMenu.show()

    def onClickQuit(self):
        self.quitMessage = QMessageBox()
        self.quitMessage = QMessageBox.question(self, "Выйти", "Вы уверены, что хотите выйти?",
                                                QMessageBox.No | QMessageBox.Yes)
        if self.quitMessage == QMessageBox.Yes:
            sys.exit()
        else:
            pass

    def createHighScoreDisplay(self):
        self.currentScore = QLabel()
        self.currentScore.setAlignment(PyQt5.QtCore.Qt.AlignCenter)
        self.currentScore.setFont(QFont("Futura", 14))

        self.highScore = QLabel()
        self.highScore.setAlignment(PyQt5.QtCore.Qt.AlignCenter)
        self.highScore.setFont(QFont("Futura", 14))

        highestScore = self.contents[len(self.contents) - 1]

        if int(highestScore[1]) > 0 or int(highestScore[0]) > 0:
            time = " часов"
        elif int(highestScore[4]) > 0 or int(highestScore[3]) > 0:
            time = " минут"
        else:
            time = " секунд"

        self.currentScore.setText("Ваш результат в игре поиск слова в " + self.contents[len(self.contents) - 1]
                                  + time + " в " + self.contents[len(self.contents) - 2] + " Режиме")

        mode = self.contents[len(self.contents) - 2]

        for x in range(1, len(self.contents), 2):
            if highestScore > self.contents[x] and self.contents[x - 1] == mode:
                highestScore = self.contents[x]
        if highestScore == self.contents[len(self.contents) - 1]:
            self.highScore.setText("Вы побили свой рекорд!")
        else:
            self.highScore.setText("Вы не превзошли свой лучший результат в" + highestScore + " .")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main = StartMenu()
    main.show()
    sys.exit(app.exec_())
