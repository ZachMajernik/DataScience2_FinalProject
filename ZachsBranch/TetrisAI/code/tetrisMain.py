from settings import *
from sys import exit

# components
from game import Game
from gameOver import GameOver
from score import Score
from preview import Preview
from random import choice

class TetrisMain:
    def __init__(self):

        # general
        pygame.init()
        self.display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.clock = pygame.time.Clock()
        pygame.display.set_caption('Tetris')

        # shapes
        self.next_shapes = [choice(list(TETROMINOS.keys())) for shape in range(3)]

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
        self.next_shapes.append(choice(list(TETROMINOS.keys())))
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
                # self.gameOver.run()
                pygame.quit()
                return (self.score.score, self.score.level, self.score.lines)

            # updating game
            pygame.display.update()
            self.clock.tick()