from settings import *
from sys import exit

# components
from game import Game
from gameOver import GameOver
from score import Score
from preview import Preview
from random import choice

class Main:
    def __init__(self):

        # general
        pygame.init()
        self.display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.clock = pygame.time.Clock()

        pygame.display.set_caption('Tetris')

        # shapes
        self.bag = list(TETROMINOS.keys())
        self.next_shapes = [choice(self.bag) for _ in range(3)]
        for shape in self.next_shapes:
            self.bag.remove(shape)

        # components
        self.game = Game(self.get_next_shape, self.update_score)
        self.gameOver = GameOver()
        self.score = Score()
        self.preview = Preview()

    def update_score(self, lines, score, level):
        self.score.lines = lines
        self.score.score = score
        self.score.level = level

        self.gameOver.lines = lines
        self.gameOver.score = score
        self.gameOver.level = level

    def get_next_shape(self):
        next_shape = self.next_shapes.pop(0)
        self.next_shapes.append(choice(self.bag))
        self.bag.remove(self.next_shapes[2])
        if len(self.bag) < 1:
            self.bag = list(TETROMINOS.keys())
        return next_shape

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    # exit everything
                    exit()
            
            #display
            self.display_surface.fill(GRAY)

            # components
            if not self.game.isGameOver:
                self.game.run()
                self.score.run()
                self.preview.run(self.next_shapes)
            else:
                self.gameOver.run()

            # updating game
            pygame.display.update()
            self.clock.tick()

if __name__ == '__main__':
    main = Main()
    main.run()