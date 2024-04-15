from settings import *
from os import path

class GameOver:
    def __init__(self):
        self.surface = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.display_surface = pygame.display.get_surface()

        self.font = pygame.font.Font(path.join(path.dirname(__file__), '..', 'graphics','Russo_One.ttf'), 20)
        self.gameOverFont = pygame.font.Font(path.join(path.dirname(__file__), '..', 'graphics','Russo_One.ttf'), 40)

        self.increment_height = self.surface.get_height()/3

        self.score = 0
        self.level = 1
        self.lines = 0
    
    def display_text(self, pos, text, fntType):
        if fntType == 'GAMEOVER':
            text_surface = self.gameOverFont.render(text, True, LINE_COLOR)
        else:
            text_surface = self.font.render(text, True, LINE_COLOR)            
        text_rect = text_surface.get_rect(center = pos)
        self.surface.blit(text_surface, text_rect)

    def run(self):
        self.surface.fill('black')
        for i, text in enumerate(['GAME OVER',f'score: {self.score}',f'level: {self.level}',f'lines cleared: {self.lines}']):
            x = self.surface.get_width()/2
            self.fntType = None
            if i == 0:
                y = 0.75*self.increment_height
                self.fntType = 'GAMEOVER'
            else:
                y = (1.25*self.increment_height) + (i-1)*(self.increment_height/4)
                self.fntType = 'REG'
            self.display_text((x,y), text, self.fntType)
        self.display_surface.blit(self.surface, (0,0))