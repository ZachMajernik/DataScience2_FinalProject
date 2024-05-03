from tetris import Tetris

class Main:
    def __init__(self):
        self.tetris = Tetris()

    def run(self):
        self.tetris.run()
        self.tetris.step()

if __name__ == '__main__':
    main = Main()
    main.run()