from sys import exit

from tetrisMain import TetrisMain

class Main:
    def __init__(self):
        self.tetrisMain = TetrisMain()

    def run(self):
        self.ran = self.tetrisMain.run()
        print(self.ran)
        exit()



if __name__ == '__main__':
    main = Main()
    main.run()