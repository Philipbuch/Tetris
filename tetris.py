import pygame
import random
from pygame import mixer

#Kilde for grunnlaget til tetrisen: https://levelup.gitconnected.com/writing-tetris-in-python-2a16bddb5318

# Initialize the game engine
pygame.init()

mixer.init()
toggleM = False
        

boom_sound = pygame.mixer.Sound("tetrisbooom.mp3")
kick_sound = pygame.mixer.Sound("tetriskick.mp3")
pling_sound = pygame.mixer.Sound("tetrispling.mp3")
wjom_sound = pygame.mixer.Sound("tetriswjomwjom.mp3")
plong_sound = pygame.mixer.Sound("tetrisplong.mp3")


# Litt ulike farger
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
LIGHTBLUE = (120, 200, 200)
ENDCOLOR = (7, 204, 147)
RED = (220, 80, 90)
MENUCOLOR = (120, 80, 100)

WIDTH = 1000
HEIGHT = 600
size = (WIDTH, HEIGHT)
screen = pygame.display.set_mode(size)

colors = [
    (0, 0, 0), #Svart
    (138, 112, 179), #Lilla
    (90, 130, 179), #Blå
    (252, 140, 67), #Orange
    (252, 180, 67), #Gul
    (220, 80, 90), #Rød
    (226, 106, 140), #Rosa
]


class Figure:
    def __init__(self, x, y, zoom, game):
        self.x = x
        self.y = y
        self.px = game.x
        self.py = game.y
        self.zoom = zoom
        self.figureTemplates = [
            [[1, 5, 9, 13], [4, 5, 6, 7]],
            [[4, 5, 9, 10], [2, 6, 5, 9]],
            [[6, 7, 9, 10], [1, 5, 6, 10]],
            [[1, 2, 5, 9], [0, 4, 5, 6], [1, 5, 9, 8], [4, 5, 6, 10]],
            [[1, 2, 6, 10], [5, 6, 7, 9], [2, 6, 10, 11], [3, 5, 6, 7]],
            [[1, 4, 5, 6], [1, 4, 5, 9], [4, 5, 6, 9], [1, 5, 6, 9]],
            [[1, 2, 5, 6]],
        ]

        self.type = random.randint(0, len(self.figureTemplates) - 1)
        self.color = random.randint(1, len(colors) - 1)
        self.rotation = 0
        
    def draw(self):
        for i in range(4):
            for j in range(4):
                p = i * 4 + j
                if p in self.image():
                    pygame.draw.rect(screen, colors[self.color],
                                     [self.px + self.zoom * (j + self.x) + 1,
                                      self.py + self.zoom * (i + self.y) + 1,
                                      self.zoom - 2, self.zoom - 2])

    def image(self):
        return self.figureTemplates[self.type][self.rotation]

    def rotate(self):
        self.rotation = (self.rotation + 1) % len(self.figureTemplates[self.type])


class Tetris:
    def __init__(self, x, y, width, height):
        # Initialiserer variabler
        self.width = width
        self.height = height
        self.x = x
        self.y = y
        self.zoom = 20
        self.broke = 0
        self.space_between = 2
        
        # Lager et tomt rutenett og intialiserer andre variabler
        self.reset()

    def reset(self):
        self.score = 0
        self.lost = False
        self.figures = []
        self.new_figure_force()
        self.queue = []
        self.spawn_ready = self.space_between + 2
        self.pressing_down = False
        self.pressing_side = 0
        self.collided = False
        self.clear()
        #restarter ikke levelet

    def clear(self):
        # Clearer hele rutenettet
        self.field = []
        for i in range(self.height):
            new_line = []
            for j in range(self.width):
                new_line.append(0)
            self.field.append(new_line)
    
    def draw(self):
        for i in range(self.height):
            for j in range(self.width):
                pygame.draw.rect(screen, WHITE, [self.x + self.zoom * j, self.y + self.zoom * i, self.zoom, self.zoom], 1)
                if self.field[i][j] > 0:
                    pygame.draw.rect(screen, colors[self.field[i][j]],
                                     [self.x + self.zoom * j + 1, self.y + self.zoom * i + 1, self.zoom - 2, self.zoom - 2])

        self.draw_figures()

    def draw_figures(self):
        # Tegn alle figurer for denne spilleren
        for figure in self.figures:
            figure.draw()

    def new_figure(self):
        fig = Figure(3, 0, self.zoom, self)
        
        # Hvis figuren intersects, legg den i køen
        if self.spawn_ready <= 0 or self.intersects(fig) or self.figure_overlap(fig):
            self.spawn_ready = self.space_between + 1
            self.queue.append(fig)
        else:
            self.spawn_ready = self.space_between + 1
            self.figures.append(fig)

    def new_figure_force(self):
        fig = Figure(3, 0, self.zoom, self)
        self.figures.append(fig)

    def new_figure_random(self):
        x = random.randrange(0, WIDTH // self.zoom - 4)
        fig = Figure(x, 0, self.zoom, self)
        
        # Dont spawn
        if not (self.spawn_ready <= 0 or self.intersects(fig) or self.figure_overlap(fig)):
            self.figures.append(fig)

    def intersects(self, figure):
        for i in range(4):
            for j in range(4):
                if i * 4 + j in figure.image():
                    if i + figure.y > self.height - 1 or \
                            j + figure.x > self.width - 1 or \
                            j + figure.x < 0 or \
                            self.field[i + figure.y][j + figure.x] > 0:
                        self.collided = True
                        return True
        return False

    def figure_overlap(self, figure):
        for i in range(4):
            for j in range(4):
                if i * 4 + j in figure.image():
                    for fig in self.figures:
                        if fig == figure:
                            continue
                        
                        for fi in range(4):
                            for fj in range(4):
                                if fi * 4 + fj in fig.image():
                                    if figure.x + j == fig.x + fj and figure.y + i == fig.y + fi:
                                        return True

        return False

    def break_lines(self):
        lines = 0
        for i in range(1, self.height):
            zeros = 0
            for j in range(self.width):
                if self.field[i][j] == 0:
                    zeros += 1
            if zeros == 0:
                lines += 1
                for i1 in range(i, 1, -1):
                    for j in range(self.width):
                        self.field[i1][j] = self.field[i1 - 1][j]
                        
        self.score += 10 * lines ** 2
        if lines > 0:
            self.broke = lines
            pygame.mixer.Sound.play(boom_sound)

        
    #space teleporter
    def go_space(self):
        self.collided = False
        while not self.collided:
            self.go_down()
        self.collided = False
    
    def move_from_queue(self):
        if len(self.queue) == 0:
            return
        
        self.spawn_ready -= 1
        
        fig = self.queue[0]
        
        if self.intersects(fig) or self.figure_overlap(fig):
            self.spawn_ready = self.space_between + 1
        else:
        #if not self.intersects(fig) and not self.figure_overlap(fig):
            if self.spawn_ready <= 0:
                self.spawn_ready = self.space_between + 1
                self.figures.append(fig)
                self.queue.pop(0)

    # Flytter alle figurer som kan en ned
    def go_down(self):
        old_figures = self.figures
        for figure in old_figures.copy():
            figure.y += 1
            
            # Hvis brikken er truffet bunnen eller andre festede brikker
            if self.intersects(figure):
                figure.y -= 1
                
                self.score += 10
                
                # Oppdater farger
                for i in range(4):
                    for j in range(4):
                        if i * 4 + j in figure.image():
                            self.field[i + figure.y][j + figure.x] = figure.color

                self.figures.remove(figure)

                # Fjerner komplette linjer hvis det er komplette linjer
                self.break_lines()
                
                if len(self.figures) + len(self.queue) == 0:
                    
                    # Lager en ny figur
                    self.new_figure_force()
                    
                    # Hvis den nye figuren treffer noe er det game over
                    if self.intersects(self.figures[-1]):
                        self.lost = True
        
        self.move_from_queue()

    def go_side(self, dx):
        for figure in self.figures:
            old_x = figure.x
            figure.x += dx
            if self.intersects(figure):
                figure.x = old_x

    def rotate(self):
        for figure in self.figures:
            old_rotation = figure.rotation
            figure.rotate()
            if self.intersects(figure):
                figure.rotation = old_rotation

        


pygame.display.set_caption("Tetris")


defaultFont = pygame.font.SysFont('Calibri', 25, True, False)
titleFont = pygame.font.SysFont('Calibri', 65, True, False)
smallFont = pygame.font.SysFont('Calibri', 15, True, False)

def singleplayer(playing_music):
    done = False
    clock = pygame.time.Clock()
    fps = 30
    game = Tetris(400, 60, 10, 25)

    sideTimer = 0
    timer1 = 0.0
    timer2 = 0
    timer3 = 0
    level = 1
    
    firstTime = True
    username = ""
    typingName = False
    newHighscore = False
    highscoreIndex = 0
    state = "playing"
    
    if playing_music:
        pygame.mixer.music.rewind()
    
    while not done:
        deltaTime = clock.tick(fps)
        
        if state == "playing":
            if game.lost:
                state = "gameover"
            
            screen.fill(LIGHTBLUE)
            
            timer1 += deltaTime / 1000.0
            timer2 += deltaTime / 1000.0

            # Øk level
            if timer2 > 30:
                level += 1
                timer2 = 0

            if timer1 > (1 / level) or game.pressing_down:
                game.go_down()
                
            if timer1 > (1 / level):
                timer1 = 0
                

            # Sjekk knapper for P1 og P2
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    done = True
                    pygame.quit()
                 
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        done = True

                    # P1
                    if event.key == pygame.K_w:
                        game.rotate()
                    if event.key == pygame.K_s:
                        game.pressing_down = True
                    if event.key == pygame.K_a:
                        game.go_side(-1)
                        game.pressing_side -= 1
                    if event.key == pygame.K_d:
                        game.go_side(1)
                        game.pressing_side += 1
                        
                        
                    if event.key == pygame.K_w:
                        pygame.mixer.Sound.play(pling_sound)
                        
                    if event.key == pygame.K_a or event.key == pygame.K_d:
                        pygame.mixer.Sound.play(plong_sound)            
                        
                        
                # Hvis man stopper aa trykke paa en knapp
                if event.type == pygame.KEYUP:
                    # P1
                    if event.key == pygame.K_s:
                        game.pressing_down = False
                    
                    if event.key == pygame.K_a:
                        game.pressing_side += 1
                        sideTimer = 0
                    
                    if event.key == pygame.K_d:
                        game.pressing_side -= 1
                        sideTimer = 0
            
            # Legg til score for komplette linjer
            game.score += game.broke * 100
            game.broke = 0
            
            if game.pressing_side != 0:
                sideTimer += deltaTime / 1000
                        
            if sideTimer > 0.3:
                game.go_side(game.pressing_side)
            
            # Gi poeng for aa holde nedover
            
            # P1
            if game.pressing_down:
                game.score += 1
            

            #P1 draw
            game.draw()

            scoreText = defaultFont.render(f"Score: {game.score}", True, BLACK)
            levelText = defaultFont.render(f"Level: {level}", True, BLACK)
            esc_Text = smallFont.render(f"Press Esc to end game", True, WHITE) 
            
            screen.blit(scoreText, (200, 20))
            screen.blit(levelText, (400, 20))
            screen.blit(esc_Text, [430, 570])

        elif state == "gameover":
            if firstTime:
                firstTime = False
                highscores = []
                with open("highscores.txt", "r") as f:
                    lines = f.readlines()
                    i = 0
                    while i < len(lines):
                        name = lines[i].strip()
                        score = int(lines[i+1].strip())
                        i += 2
                        highscores.append((name, score))
                
                highscores.append((0, game.score))
                highscores.sort(key=lambda t: t[1], reverse=True)
                highscores = highscores[:3] # Only 3 highest
                
                for i, (name, score) in enumerate(highscores):
                    # The player is in the list
                    if name == 0:
                        highscoreIndex = i
                        newHighscore = True
                        typingName = True
                        break
                
                if newHighscore:
                    highscores[highscoreIndex] = ("", game.score)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    done = True
                    pygame.quit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        # Returner til menyen
                        done = True
                    elif event.key == pygame.K_SPACE and not typingName:
                        state = "playing"
                        game.reset()
                        level = 1
                        timer1 = 0
                        timer2 = 0
                        sideTimer = 0
                        firstTime = True
                        username = ""
                        typingName = False
                        newHighscore = False
                        highscoreIndex = 0
                    elif typingName and event.key == pygame.K_BACKSPACE:
                        username = username[:-1]
                        highscores[highscoreIndex] = (username, game.score)
                    elif event.key == pygame.K_RETURN:
                        typingName = False
                        with open("highscores.txt", "w+") as f:
                            for name, score in highscores:
                                f.write(f"{name}\n{score}\n")
                    elif typingName and (pygame.key.get_mods() == 0 or (pygame.key.get_mods() & pygame.KMOD_SHIFT and event.key != pygame.K_LSHIFT)):
                        if pygame.key.get_mods() & pygame.KMOD_SHIFT:
                            username += pygame.key.name(event.key).upper()
                        elif event.key == pygame.K_SPACE:
                            username += " "
                        else:
                            username += pygame.key.name(event.key)
                        highscores[highscoreIndex] = (username, game.score)
            
            game_over_text = titleFont.render(f"Game over!", True, WHITE)
            endscore = defaultFont.render(f"Score: {game.score}", True, BLACK)
            press_esc_text = defaultFont.render("Press ESC to quit or SPACE to restart", True, WHITE)
            highscore_text = defaultFont.render("Highscores", True, WHITE)

            screen.fill(ENDCOLOR)
            screen.blit(game_over_text, (320, 40))
            screen.blit(endscore, (20, 250))
            screen.blit(press_esc_text, (20, 350))
            screen.blit(highscore_text, (340, 120))
            
            if newHighscore:
                new_highscore_text = defaultFont.render("Congratulations! You made it onto top 3. Please type in your name and press enter", True, WHITE)
                screen.blit(new_highscore_text, (60, 400))
            
            for i, (name, score) in enumerate(highscores):
                s = f"{i+1}. {name} {score}"
                text = defaultFont.render(s, True, WHITE)
                screen.blit(text, (350, 150 + 30*i))
        
        pygame.display.flip()

def pvp(playing_music):
    done = False
    clock = pygame.time.Clock()
    fps = 30
    gameP1 = Tetris(200, 60, 10, 25)
    gameP2 = Tetris(600, 60, 10, 25)

    sideTimerP1 = 0
    sideTimerP2 = 0

    timer1 = 0.0
    timer2 = 0
    timer3 = 0
    level = 1
    state = "playing"
    whowon = "Draw"
    kanduspace = False
    
    if playing_music:
        pygame.mixer.music.rewind()
    
    while not done:
        deltaTime = clock.tick(fps)
        
        if state == "playing":
            if gameP1.lost:
                state = "gameover"
                gameP1.score -= 200

            if gameP2.lost:
                state = "gameover"
                gameP2.score -= 200
            
            screen.fill(LIGHTBLUE)
            
            timer1 += deltaTime / 1000.0
            timer2 += deltaTime / 1000.0

            # Øk level
            if timer2 > 30:
                level += 1
                timer2 = 0

            if timer1 > (1 / level) or gameP1.pressing_down:
                gameP1.go_down()
            
            if timer1 > (1 / level) or gameP2.pressing_down:
                gameP2.go_down()
                
            if timer1 > (1 / level):
                timer1 = 0
                

            # Sjekk knapper for P1 og P2
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    done = True
                    pygame.quit()
                 
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        done = True
                    
                    # P1
                    if event.key == pygame.K_w:
                        gameP1.rotate()
                    if event.key == pygame.K_s:
                        gameP1.pressing_down = True
                    if event.key == pygame.K_a:
                        gameP1.go_side(-1)
                        gameP1.pressing_side -= 1
                    if event.key == pygame.K_d:
                        gameP1.go_side(1)
                        gameP1.pressing_side += 1
                    
                    if event.key == pygame.K_p:
                        for i in range(4):
                            gameP2.new_figure()
                    
                    # P2
                    if event.key == pygame.K_UP:
                        gameP2.rotate()
                    if event.key == pygame.K_DOWN:
                        gameP2.pressing_down = True
                    if event.key == pygame.K_LEFT:
                        gameP2.go_side(-1)
                        gameP2.pressing_side -= 1
                    if event.key == pygame.K_RIGHT:
                        gameP2.go_side(1)
                        gameP2.pressing_side += 1
                    #if event.key == pygame.K_ESCAPE:
                    #    gameP1.__init__(20, 10)
                    
                    # Begge kan trykke på space
                    if event.key == pygame.K_SPACE:
                        if kanduspace == True:
                            gameP1.go_space()
                            gameP2.go_space()
                            kanduspace = False
                            pygame.mixer.Sound.play(wjom_sound)
                        
                        
                    if event.key == pygame.K_w or event.key == pygame.K_UP:
                        pygame.mixer.Sound.play(pling_sound)
                        
                    if event.key == pygame.K_a or event.key == pygame.K_d or event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                        pygame.mixer.Sound.play(plong_sound)            
                        
                        
                # Hvis man stopper aa trykke paa en knapp
                if event.type == pygame.KEYUP:
                    # P1
                    if event.key == pygame.K_s:
                        gameP1.pressing_down = False
                    
                    if event.key == pygame.K_a:
                        gameP1.pressing_side += 1
                        sideTimerP1 = 0
                    
                    if event.key == pygame.K_d:
                        gameP1.pressing_side -= 1
                        sideTimerP1 = 0
                        
                    
                    # P2
                    if event.key == pygame.K_DOWN:
                        gameP2.pressing_down = False
                    
                    if event.key == pygame.K_LEFT:
                        gameP2.pressing_side += 1
                        sideTimerP2 = 0
                    
                    if event.key == pygame.K_RIGHT:
                        gameP2.pressing_side -= 1
                        sideTimerP2 = 0
            
            # Legg til score for komplette linjer
            gameP1.score += gameP1.broke * 100
            gameP2.score += gameP2.broke * 100
            
            for i in range(gameP1.broke):
                gameP2.new_figure()
            
            for i in range(gameP2.broke):
                gameP1.new_figure()
            
            gameP1.broke = 0
            gameP2.broke = 0
            
            if gameP1.pressing_side != 0:
                sideTimerP1 += deltaTime / 1000
            
            if gameP2.pressing_side != 0:
                sideTimerP2 += deltaTime / 1000
                        
            if sideTimerP1 > 0.3:
                gameP1.go_side(gameP1.pressing_side)
            
            if sideTimerP2 > 0.3:
                gameP2.go_side(gameP2.pressing_side)
            
            # Gi poeng for aa holde nedover
            
            # P1
            if gameP1.pressing_down:
                gameP1.score += 1
            
            # P2
            if gameP2.pressing_down:
                gameP2.score += 1
                
                
            #space cooldown
            if kanduspace == False:
                timer3 += deltaTime / 1000
                
            if timer3 >= 4.99:
                kanduspace = True
                timer3 = 0
            

            #P1 draw
            gameP1.draw()
            
            #P2 draw
            gameP2.draw()

            scoreP1 = defaultFont.render(f"P1 score: {gameP1.score}", True, BLACK)
            scoreP2 = defaultFont.render(f"P2 score: {gameP2.score}", True, BLACK)
            levelText = defaultFont.render(f"Level: {level}", True, BLACK)
            esc_Text = smallFont.render(f"Press Esc to end game", True, WHITE) 
            
            cooldowntimah = "{:.1f}".format(5-timer3)
            cooldown = defaultFont.render(f"Space: {cooldowntimah}", True, BLACK)
            ready = defaultFont.render(f"Space:", True, BLACK)
            readycolor = defaultFont.render(f"Ready!", True, RED)

            screen.blit(scoreP1, [200, 20])
            screen.blit(scoreP2, [600, 20])
            screen.blit(levelText, [420, 20])
            screen.blit(esc_Text, [430, 570])
            
            if timer3 == 0:
                screen.blit(ready, [420, 50])
                screen.blit(readycolor, [495, 50])
            
            else:
                screen.blit(cooldown, [420, 50])

        elif state == "gameover":
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    done = True
                    pygame.quit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        # Returner til menyen
                        done = True
                    if event.key == pygame.K_SPACE:
                        state = "playing"
                        gameP1.reset()
                        gameP2.reset()
                        level = 1
                        timer1 = 0
                        timer2 = 0
                        timer3 = 0
                        sideTimerP1 = 0
                        sideTimerP2 = 0
                        kanduspace = False
                        deltaTime = 0

            if gameP1.score == gameP2.score:
                who_won_text = titleFont.render("It is a tie!", True, WHITE)
            elif gameP1.score > gameP2.score:
                who_won_text = titleFont.render(f"P1 won with {gameP1.score - gameP2.score} points!", True, WHITE)
            elif gameP2.score > gameP1.score:
                who_won_text = titleFont.render(f"P2 won with {gameP2.score - gameP1.score} points!", True, WHITE)
            
            endscore = defaultFont.render(f"P1 Score: {gameP1.score}, P2 Score: {gameP2.score}", True, BLACK)
            press_esc_text = defaultFont.render("Press ESC to quit or SPACE to restart", True, WHITE)

            screen.fill(ENDCOLOR)
            screen.blit(who_won_text, [20, 200])
            screen.blit(endscore, [20, 270])
            screen.blit(press_esc_text, [20, 350])
        
        pygame.display.flip()
    

def menu():
    fps = 60
    
    mixer.music.load("spillmusikk.mp3")
    mixer.music.set_volume(0.7)
    mixer.music.play(loops=-1)
    
    backgroundGame1 = Tetris(0, 0, WIDTH, HEIGHT)
    backgroundGame2 = Tetris(0, 0, WIDTH, HEIGHT)
    backgroundGame2.zoom = 40
    
    # It starts with one but for pretty we remove it
    backgroundGame1.figures = []
    
    deltaTime = 0
    
    clock = pygame.time.Clock()
    
    pygame.time.set_timer(pygame.USEREVENT, 100)
    
    title_text = titleFont.render("PHILIP'S TETRIS", True, WHITE)
    button_text = defaultFont.render("Press 8 for Single Player. Press 9 for PvP", True, WHITE)
    music_text = smallFont.render("Select music track by pressing 1 or 2, or 3 for no music", True, WHITE)
    rules_text = defaultFont.render("Rules:", True, WHITE)
    rules1_text = smallFont.render("1. Win by scoring the most points! ", True, WHITE)
    rules2_text = smallFont.render("2. Moving: P1 and single player: wasd. P2: up,left,down,right ", True, WHITE)
    rules3_text = smallFont.render("3. Breaking lines and holding the down button gives points", True, WHITE)
    rules4_text = smallFont.render("4. In PvP, both players can use the teleporting SPACE button", True, WHITE)
    rules5_text = smallFont.render("5. In Pvp, if you reach the top, you lose 200 points", True, WHITE)
    rules6_text = smallFont.render("6. In Pvp, breaking x lines spawns x figures for the enemy", True, WHITE)
    
    
    
    playing_music = True
    counter = 3
    
    done = False
    while not done:
        deltaTime = clock.tick(fps)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
             
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    done = True
                if event.key == pygame.K_1:
                    mixer.music.load("spillmusikk.mp3")
                    mixer.music.set_volume(0.7)
                    mixer.music.play(loops=-1)
                    playing_music = True
                    
                if event.key == pygame.K_2:
                    mixer.music.load("spillmusikk2.mp3")
                    mixer.music.set_volume(0.5)
                    mixer.music.play(loops=-1)
                    playing_music = True
                
                if event.key == pygame.K_3:
                    mixer.music.stop()
                    mixer.music.unload()
                    playing_music = False
                
                if event.key == pygame.K_8:
                    singleplayer(playing_music)
                    if playing_music:
                        pygame.mixer.music.rewind()
                    
                if event.key == pygame.K_9:
                    pvp(playing_music)
                    if playing_music:
                        pygame.mixer.music.rewind()
            
            if event.type == pygame.USEREVENT:
                backgroundGame1.go_down()
                backgroundGame2.go_down()
                
                for figure in backgroundGame1.figures:
                    if figure.y-10 > HEIGHT // backgroundGame1.zoom:
                        backgroundGame1.figures.remove(figure)
                
                for figure in backgroundGame2.figures:
                    if figure.y-10 > HEIGHT // backgroundGame2.zoom:
                        backgroundGame2.figures.remove(figure)
                
                counter -= 1
                if counter == 0:
                    backgroundGame1.new_figure_random()
                    backgroundGame2.new_figure_random()
                    counter = 3
        
        screen.fill(MENUCOLOR)
        backgroundGame1.draw_figures()
        backgroundGame2.draw_figures()
        
        screen.blit(title_text, [20, 200])
        screen.blit(button_text, [20,280])
        screen.blit(music_text, [20, 310])
        screen.blit(rules_text, [600,200])
        screen.blit(rules1_text, [600,240])
        screen.blit(rules2_text, [600,280])
        screen.blit(rules3_text, [600,320])
        screen.blit(rules4_text, [600,360])
        screen.blit(rules5_text, [600,400])
        screen.blit(rules6_text, [600,440])
        pygame.display.flip()


# Åpne meny skjerm
menu()
    
pygame.quit()

