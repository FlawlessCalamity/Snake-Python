from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import random

BOARD_SIZE = 400
INFO_SIZE = 100
GAME_SPEED = 150
MOUSE_SIZE = 20
SNAKE_SIZE = 20


class Board(QFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.initBoard()

    def initBoard(self):
        '''initiates board'''
        self.endGamePopUp = QMessageBox()
        self.endGamePopUp.setText('You chrashed...')
        self.endGamePopUp.setInformativeText('Do you want to retry?')
        self.endGamePopUp.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        self.endGamePopUp.setDefaultButton(QMessageBox.Yes)
        self.endGamePopUp.buttonClicked.connect(self.endGameDecision)
        self.scoreLabelPoint = QPoint(10, BOARD_SIZE/10)
        self.score = 0
        self.speed = GAME_SPEED
        self.direction = 180
        self.setFocusPolicy(Qt.StrongFocus)
        self.snake = Snake()
        self.mouse = Mouse()
        self.paintEvent("event")
        self.timer = QBasicTimer()
        self.timer.start(self.speed, self)
        # self.snakeSection = QRectF(
        # self.snake.sizeX, self.snake.sizeY, self.snake.posX, self.snake.posY)

    def endGameDecision(self, event):
        if event.text() == '&Yes':
            print('success')
            # self.initBoard()
            qApp.exit(main_window.EXIT_CODE_REBOOT)
        else:
            app.instance().quit()

    def paintEvent(self, event):
        painter = QPainter(self)
        self.drawGame(self.snake, self.mouse, painter, self.score)

    def drawGame(self, snake, mouse, painter, score):
        painter.drawPixmap(mouse.posX, mouse.posY,
                           mouse.sizeX, mouse.sizeY, mouse.mousePixmap)
        snakeHead = snake.headPixmap.transformed(
            QTransform().rotate(snake.direction), Qt.FastTransformation
        )

        if len(snake.tailPoints) == 0:
            painter.drawPixmap(snake.posX, snake.posY,
                               snake.sizeX, snake.sizeY, snakeHead)
        else:
            painter.drawPixmap(snake.posX, snake.posY,
                               snake.sizeX, snake.sizeY, snakeHead)
            for tailSection in snake.tailPoints:
                snakeBody = snake.bodyPixmap.transformed(
                    QTransform().rotate(tailSection[2]), Qt.FastTransformation)
                if (tailSection[2] == 90 and tailSection[3] == 180) or (tailSection[2] == 0 and tailSection[3] == 270):
                    # from down to right and left to up
                    snakeBend = snake.bendPixmap.transformed(
                        QTransform().rotate(0), Qt.FastTransformation)
                    painter.drawPixmap(tailSection[0], tailSection[1],
                                       snake.sizeX, snake.sizeY, snakeBend)
                elif (tailSection[2] == 90 and tailSection[3] == 0) or (tailSection[2] == 180 and tailSection[3] == 270):
                     # from up to right and left to down
                    snakeBend = snake.bendPixmap.transformed(
                        QTransform().rotate(90), Qt.FastTransformation)
                    painter.drawPixmap(tailSection[0], tailSection[1],
                                       snake.sizeX, snake.sizeY, snakeBend)
                elif (tailSection[2] == 270 and tailSection[3] == 180) or (tailSection[2] == 0 and tailSection[3] == 90):
                     # from down to left and right to up
                    snakeBend = snake.bendPixmap.transformed(
                        QTransform().rotate(270), Qt.FastTransformation)
                    painter.drawPixmap(tailSection[0], tailSection[1],
                                       snake.sizeX, snake.sizeY, snakeBend)
                elif (tailSection[2] == 180 and tailSection[3] == 90) or (tailSection[2] == 270 and tailSection[3] == 0):
                    # from right to down and up to left
                    snakeBend = snake.bendPixmap.transformed(
                        QTransform().rotate(180), Qt.FastTransformation)
                    painter.drawPixmap(tailSection[0], tailSection[1],
                                       snake.sizeX, snake.sizeY, snakeBend)
                else:
                    painter.drawPixmap(tailSection[0], tailSection[1],
                                       snake.sizeX, snake.sizeY, snakeBody)
        painter.drawText(self.scoreLabelPoint, 'Score:  '+str(self.score))

    def keyPressEvent(self, event):
        key = event.key()
        # self.snake.prevDirection = self.snake.direction
        if key == Qt.Key_Left and self.snake.direction != 90:
            self.snake.direction = 270
        elif key == Qt.Key_Right and self.snake.direction != 270:
            self.snake.direction = 90
        elif key == Qt.Key_Down and self.snake.direction != 0:
            self.snake.direction = 180
        elif key == Qt.Key_Up and self.snake.direction != 180:
            self.snake.direction = 0
        # self.update()

    def timerEvent(self, event):
        '''handles timer event'''
        self.snake.checkMouseIsCaught(self.snake.direction, self.mouse)
        self.snake.snakeMove()


class Snake(object):
    def __init__(self):
        self.direction = 180
        self.prevDirection = 0
        self.posX = self.snakeStartPos()
        self.posY = self.snakeStartPos()
        self.tailPoints = []
        self.sizeX = SNAKE_SIZE
        self.sizeY = SNAKE_SIZE
        self.movementLength = SNAKE_SIZE
        self.headPixmap = QPixmap('snakeHead.png')
        self.bodyPixmap = QPixmap('snakeBody.png')
        self.bendPixmap = QPixmap('snakeBend.png')

    def snakeStartPos(self):
        pos = BOARD_SIZE/2
        if pos % SNAKE_SIZE == 0:
            return int(pos)
        else:
            return (pos + (pos % SNAKE_SIZE))

    def snakeMove(self):
        if self.direction == 270:  # and self.posX > 0:
            self.snakeTrail(True)
            self.posX -= self.movementLength
        elif self.direction == 90:  # and self.posX + self.sizeX < BOARD_SIZE:
            self.snakeTrail(True)
            self.posX += self.movementLength
        elif self.direction == 0:  # and self.posY > 0:
            self.snakeTrail(True)
            self.posY -= self.movementLength
        elif self.direction == 180:  # and self.posY + self.sizeY < BOARD_SIZE:
            self.snakeTrail(True)
            self.posY += self.movementLength
        self.collisionCheck()
        main_window.board.update()

    def checkMouseIsCaught(self, snakeDirecetion, mouse):
        if self.direction == 270 and self.posX == mouse.posX and self.posY == mouse.posY:
            mouse.newMousePos()
            self.snakeTrail(False)
            main_window.board.score += 1
        elif self.direction == 90 and self.posX == mouse.posX and self.posY == mouse.posY:
            mouse.newMousePos()
            self.snakeTrail(False)
            main_window.board.score += 1
        elif self.direction == 0 and self.posX == mouse.posX and self.posY == mouse.posY:
            mouse.newMousePos()
            self.snakeTrail(False)
            main_window.board.score += 1
        elif self.direction == 180 and self.posX == mouse.posX and self.posY == mouse.posY:
            mouse.newMousePos()
            self.snakeTrail(False)
            main_window.board.score += 1

    def snakeTrail(self, flag):
        if len(self.tailPoints) > 1:
            self.tailPoints.append(
                (self.posX, self.posY, self.direction, self.prevDirection))
            if flag:
                self.prevDirection = self.direction
        else:
            self.tailPoints.append(
                (self.posX, self.posY, self.direction, self.prevDirection))
            self.prevDirection = self.direction
        if flag:
            self.tailPoints.pop(0)

    def collisionCheck(self):
        collision = False
        if (self.direction == 270 and self.posX < 0) or (self.direction == 90 and self.posX + self.sizeX > BOARD_SIZE) or (self.direction == 0 and self.posY < 0) or (self.direction == 180 and self.posY + self.sizeY > BOARD_SIZE):
            collision = True
        for check in self.tailPoints:
            if self.posX == check[0] and self.posY == check[1]:
                collision = True
        if collision:
            main_window.board.timer.stop()
            main_window.board.endGamePopUp.setText(
                'You crashed.... Your score was: '+str(main_window.board.score))
            main_window.board.endGamePopUp.show()


class Mouse(object):
    def __init__(self):
        self.posX = random.randrange(
            MOUSE_SIZE, BOARD_SIZE-MOUSE_SIZE, MOUSE_SIZE)
        self.posY = random.randrange(
            MOUSE_SIZE, BOARD_SIZE-MOUSE_SIZE, MOUSE_SIZE)
        self.sizeX = MOUSE_SIZE
        self.sizeY = MOUSE_SIZE
        self.mousePixmap = QPixmap('mouse.png')

    def newMousePos(self):
        availableSpace = False
        check = True
        while not availableSpace:
            check = True
            availableSpace = True
            newPosX = random.randrange(
                MOUSE_SIZE, BOARD_SIZE-MOUSE_SIZE, MOUSE_SIZE)
            newPosY = random.randrange(
                MOUSE_SIZE, BOARD_SIZE-MOUSE_SIZE, MOUSE_SIZE)
            if len(main_window.board.snake.tailPoints) == 0:
                availableSpace = True
            else:
                for availableSpot in main_window.board.snake.tailPoints:
                    if newPosX == availableSpot[0] and newPosY == availableSpot[1]:
                        check = False
                        break
                if check == True:
                    availableSpace = True
                else:
                    availableSpace = False
        self.posX = newPosX
        self.posY = newPosY


class MainWindow(QMainWindow):
    EXIT_CODE_REBOOT = -123

    def __init__(self):
        super().__init__()
        self.setFixedSize(BOARD_SIZE, BOARD_SIZE)
        self.setWindowTitle('Snake Basic')
        self.InitUI()

    def InitUI(self):
        self.board = Board(self)
        self.setCentralWidget(self.board)
        self.setStyleSheet('background-color:black;color:white;')
        self.show()


if __name__ == "__main__":
    currentExitCode = MainWindow.EXIT_CODE_REBOOT
    while currentExitCode == MainWindow.EXIT_CODE_REBOOT:
        app = QApplication([])
        main_window = MainWindow()
        currentExitCode = app.exec_()
        app = None
