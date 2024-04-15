from settings import *
from sys import exit
from os import path

# components
from random import choice

class Tetris:
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
        self.score = Score()
        self.preview = Preview()

    def reset(self):
        pass

    def step(self):
        pass

    def update_score(self, lines, score, level):
        self.score.lines = lines
        self.score.score = score
        self.score.level = level

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
                exit()

            # updating game
            pygame.display.update()
            self.clock.tick()

class Game:
    def __init__(self, get_next_shape, update_score):

        # general
        self.surface = pygame.Surface((GAME_WIDTH, GAME_HEIGHT))
        self.display_surface = pygame.display.get_surface()
        self.rect = self.surface.get_rect(topleft = (PADDING, PADDING))
        self.sprites = pygame.sprite.Group()
        self.update_score = update_score

        self.get_next_shape = get_next_shape

        # lines
        self.line_surface = self.surface.copy()
        self.line_surface.fill((0,255,0))
        self.line_surface.set_colorkey((0,255,0))
        self.line_surface.set_alpha(120)

        # tetromino
        self.field_data = [[0 for x in range(COLUMNS)] for y in range(ROWS)]
        self.tetromino = Tetromino(choice(list(TETROMINOS.keys())), 
                                   self.sprites,
                                   self.create_new_tetromino,
                                   self.field_data)

        # timer

        self.down_speed = UPDATE_START_SPEED
        self.down_speed_faster = self.down_speed * 0.3
        self.down_pressed = False
        self.timers = {
            'vertical move': Timer(self.down_speed, True, self.move_down),
            'horizontal move': Timer(MOVE_WAIT_TIME),
            'rotate': Timer(ROTATE_WAIT_TIME)
        }
        self.timers['vertical move'].activate()

        # score
        self.current_level = 1
        self.current_score = 0
        self.current_lines = 0

        self.isGameOver = False

    def calculate_score(self, num_lines):
        self.current_lines += num_lines
        self.current_score += SCORE_DATA[num_lines] * self.current_level

        # every 10 lines cleared, level += 1
        if self.current_lines/10 > self.current_level:
            self.current_level += 1
            self.down_speed *= 0.75
            self.down_speed_faster = self.down_speed * 0.3
            self.timers['vertical move'].duration = self.down_speed
        self.update_score(self.current_lines, self.current_score, self.current_level)

    def create_new_tetromino(self):
        self.check_game_over()
        self.check_finished_rows()
        self.tetromino = Tetromino(self.get_next_shape(), 
                                   self.sprites,
                                   self.create_new_tetromino,
                                   self.field_data)

    def check_game_over(self):
        for block in self.tetromino.blocks:
            if block.pos.y < 0:
                self.isGameOver = True
                for timer in self.timers.keys():
                    self.timers[timer].repeated = False
                    self.timers[timer].deactivate()
                # exit()

    def timer_update(self):
        for timer in self.timers.values():
            timer.update()

    def move_down(self):
        self.tetromino.move_down()

    def draw_grid(self):

        for col in range(1, COLUMNS):
            x = col * CELL_SIZE
            pygame.draw.line(self.line_surface, LINE_COLOR, (x,0), (x,self.surface.get_height()), 1)

        for row in range(1, ROWS):
            y = row * CELL_SIZE
            pygame.draw.line(self.line_surface, LINE_COLOR, (0,y), (self.surface.get_width(),y), 1)

        self.surface.blit(self.line_surface, (0,0))

    def input(self):
        keys = pygame.key.get_pressed()

        if not self.timers['horizontal move'].active:
            if keys[pygame.K_LEFT]:
                self.tetromino.move_horizontal(-1)
                self.timers['horizontal move'].activate()
            if keys[pygame.K_RIGHT]:
                self.tetromino.move_horizontal(1)
                self.timers['horizontal move'].activate()

        if not self.timers['rotate'].active:
            if keys[pygame.K_UP]:
                self.tetromino.rotate()
                self.timers['rotate'].activate()

        if not self.down_pressed and keys[pygame.K_DOWN]:
            self.down_pressed = True
            self.timers['vertical move'].duration = self.down_speed_faster

        if self.down_pressed and not keys[pygame.K_DOWN]:
            self.down_pressed = False
            self.timers['vertical move'].duration = self.down_speed

    def check_finished_rows(self):
        # get row indicies
        delete_rows = []
        for i, row in enumerate(self.field_data):
            if all(row):
                delete_rows.append(i)

        if delete_rows:
            for delete_row in delete_rows:
                for block in self.field_data[delete_row]:
                    block.kill()

                for row in self.field_data:
                    for block in row:
                        if block and block.pos.y < delete_row:
                            block.pos.y += 1

            self.field_data = [[0 for x in range(COLUMNS)] for y in range(ROWS)]
            for block in self.sprites:
                self.field_data[int(block.pos.y)][int(block.pos.x)] = block

            # update score
            self.calculate_score(len(delete_rows))

    def run(self):

        # update
        self.input()
        self.timer_update()
        self.sprites.update()

        self.surface.fill('black')
        self.sprites.draw(self.surface)

        self.draw_grid()
        self.display_surface.blit(self.surface, (PADDING,PADDING))
        pygame.draw.rect(self.display_surface, LINE_COLOR, self.rect, 2, 2)

class Tetromino:
    def __init__(self, shape, group, create_new_tetromino, field_data):
        self.shape = shape
        self.block_positions = TETROMINOS[shape]['shape']
        self.color = TETROMINOS[shape]['color']
        self.create_new_tetromino = create_new_tetromino
        self.field_data = field_data

        # create blocks
        self.blocks = [Block(group, pos, self.color) for pos in self.block_positions]

    # collisions
    def next_move_horizontal_collide(self, blocks, amount):
        collision_list = [block.horizontal_collide(int(block.pos.x + amount), self.field_data) for block in self.blocks]
        return True if any(collision_list) else False
    
    def next_move_vertical_collide(self, blocks, amount):
        collision_list = [block.vertical_collide(int(block.pos.y + amount), self.field_data) for block in self.blocks]
        return True if any(collision_list) else False

    # movement
    def move_horizontal(self, amount):
        if not self.next_move_horizontal_collide(self.blocks, amount):
            for block in self.blocks:
                block.pos.x += amount

    def move_down(self):
        if not self.next_move_vertical_collide(self.blocks, 1):
            for block in self.blocks:
                block.pos.y += 1
        else:
            for block in self.blocks:
                self.field_data[int(block.pos.y)][int(block.pos.x)] = block
            self.create_new_tetromino()

    def rotate(self):
        if self.shape != 'O':
            pivot_pos = self.blocks[0].pos

            new_block_positions = [block.rotate(pivot_pos) for block in self.blocks]

            for pos in new_block_positions:
                if pos.x < 0 or pos.x >= COLUMNS:
                    return
                
                if self.field_data[int(pos.y)][int(pos.x)]:
                    return
                        
                if pos.y >= ROWS:
                    return

            for i, block in enumerate(self.blocks):
                block.pos = new_block_positions[i]

class Block(pygame.sprite.Sprite):
    def __init__(self, group, pos, color):
        # general
        super().__init__(group)
        self.image = pygame.Surface((CELL_SIZE, CELL_SIZE))
        self.image.fill(color)

        # position
        self.pos = pygame.Vector2(pos) + BLOCK_OFFSET
        self.rect = self.image.get_rect(topleft = self.pos*CELL_SIZE)

    def rotate(self, pivot_pos):
        # distance = self.pos - pivot_pos
        # rotated = distance.rotate(90)
        # new_pos = pivot_pos + rotated
        # return new_pos
        return pivot_pos + (self.pos - pivot_pos).rotate(90)

    def horizontal_collide(self, x, field_data):
        if not 0 <= x < COLUMNS:
            return True
        
        if field_data[int(self.pos.y)][x]:
            return True
        
    def vertical_collide(self, y, field_data):
        if y >= ROWS:
            return True
        
        if y >= 0 and field_data[y][int(self.pos.x)]:
            return True

    def update(self):
        self.rect.topleft = self.pos*CELL_SIZE

class Preview:
    def __init__(self):
        self.surface = pygame.Surface((SIDEBAR_WIDTH, GAME_HEIGHT * PREVIEW_HEIGHT_FRACTION))
        self.rect = self.surface.get_rect(topright = (WINDOW_WIDTH - PADDING, PADDING))
        self.display_surface = pygame.display.get_surface()

        self.shape_surfaces = {shape: pygame.image.load(path.join(path.dirname(__file__), '..', 'graphics', f'{shape}.png')).convert_alpha() for shape in TETROMINOS.keys()}
    
        self.increment_height = self.surface.get_height() / 3
    
    def display_pieces(self, shapes):
        for i, shape in enumerate(shapes):
            shape_surface = self.shape_surfaces[shape]
            x = self.surface.get_width()/2
            y = self.increment_height/2 + i*self.increment_height
            rect = shape_surface.get_rect(center = (x,y))
            self.surface.blit(shape_surface, rect)

    def run(self, next_shapes):
        self.surface.fill('black')
        self.display_pieces(next_shapes)
        self.display_surface.blit(self.surface, self.rect)
        pygame.draw.rect(self.display_surface, LINE_COLOR, self.rect, 2, 2)

class Score:
    def __init__(self):
        self.surface = pygame.Surface((SIDEBAR_WIDTH, GAME_HEIGHT * SCORE_HEIGHT_FRACTION - PADDING))
        self.rect = self.surface.get_rect(bottomright = (WINDOW_WIDTH - PADDING, WINDOW_HEIGHT - PADDING))
        self.display_surface = pygame.display.get_surface()

        self.font = pygame.font.Font(path.join(path.dirname(__file__), '..', 'graphics','Russo_One.ttf'), 20)

        self.increment_height = self.surface.get_height()/3

        self.score = 0
        self.level = 1
        self.lines = 0
    
    def display_text(self, pos, text):
        text_surface = self.font.render(f'{text[0]}: {text[1]}', True, LINE_COLOR)
        text_rect = text_surface.get_rect(center = pos)
        self.surface.blit(text_surface, text_rect)

    def run(self):
        self.surface.fill('black')
        for i, text in enumerate([('Score', self.score),('Level', self.level),('Lines', self.lines)]):
            x = self.surface.get_width()/2
            y = self.increment_height/2 + i*self.increment_height
            self.display_text((x,y), text)

        self.display_surface.blit(self.surface, self.rect)
        
        pygame.draw.rect(self.display_surface, LINE_COLOR, self.rect, 2, 2)

class Timer:
    def __init__(self, duration, repeated = False, func = None):
        self.repeated = repeated
        self.func = func
        self.duration = duration

        self.start_time = 0
        self.active = False

    def activate(self):
        self.active = True
        self.start_time = pygame.time.get_ticks()

    def deactivate(self):
        self.active = False
        self.start_time = 0

    def update(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.start_time >= self.duration and self.active:

            # call function
            if self.func and self.start_time != 0:
                self.func()

            # reset timer
            self.deactivate()

            # repeat timer
            if self.repeated:
                self.activate()

class Main:
    def __init__(self):
        self.tetris = Tetris()

    def run(self):
        self.tetris.reset()

if __name__ == '__main__':
    main = Main()
    main.run()