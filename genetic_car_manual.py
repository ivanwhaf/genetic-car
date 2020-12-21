import sys
import time
import math
import copy
import pygame as pg
from pygame.locals import *
from nn import *

pg.init()  # initilize the game
size = width, height = 1060, 700  # screen size
screen = pg.display.set_mode(size)
pg.display.set_caption("Genetic algorithm car")  # set title
background = pg.image.load('resources/bg.png')  # background
font = pg.font.Font(None, 25)  # font setting

num = 150  # samples number per loop
generation = 50  # iteration round number
gen_max_time = 30  # every generation's max time

pm = 0.95  # probability of mutation
mutate_elites_range = (-0.2, 0.2)  # range of mutation value -~+
mutate_range = (-1, 1)  # range of mutation value -~+

FPS = 60  # fps setting

x_init, y_init = 385, 400  # car's initial position
max_speed = 6  # car's max limit speed
min_speed = 3  # car's min limit speed

min_angle_speed_change_frame_interval = 2


def draw_text(text, pos, color):
    img = font.render(
        text, True, color)
    screen.blit(img, pos)


class Car:
    """
    car class, includes position, speed, and some status.
    """

    def __init__(self):
        # position and angle
        self.x = x_init
        self.y = y_init
        self.angle = 45  # init angle
        self.speed = min_speed

        # live status
        self.isAlive = True

        # three distance indicator lines' end point positions
        self.x1, self.y1 = 0, 0
        self.x2, self.y2 = 0, 0
        self.x3, self.y3 = 0, 0

        # three distances from the track boundary
        self.dis1 = 0
        self.dis2 = 0
        self.dis3 = 0

        # total running distance
        self.distance = 0

        # frame counter, angle can change only when counter enough
        self.counter = 0

        self.selected = False

    def update_position(self):
        # update position and distance according to angle and speed
        if not self.isAlive:
            return

        angle = math.pi*(self.angle)/180
        self.x += self.speed*math.cos(angle)
        self.y -= self.speed*math.sin(angle)
        self.distance += math.sqrt((self.speed*math.cos(angle))
                                   ** 2+(self.speed*math.sin(angle))**2)

    def detect_track_boundary(self):
        # if screen.get_at((int(self.x), int(self.y))) == (0, 0, 0, 255):
        try:
            pixel = screen.get_at((int(self.x), int(self.y)))
            if pixel[0] <= 1 and pixel[1] <= 1 and pixel[2] <= 1:
                self.isAlive = False
        except:
            return

    def draw_indicator_line(self):
        # draw three indicator lines of each car
        pg.draw.line(screen, (0, 255, 0), (self.x, self.y),
                     (self.x1, self.y1), 1)
        pg.draw.line(screen, (0, 255, 0), (self.x, self.y),
                     (self.x2, self.y2), 1)
        pg.draw.line(screen, (0, 255, 0), (self.x, self.y),
                     (self.x3, self.y3), 1)

    def calculate_three_distance(self):
        # calculate car's three angles' distances form the track boundary
        if not self.isAlive:
            return

        ang1 = self.angle+55
        ang2 = self.angle
        ang3 = self.angle-55

        # rand
        angle1 = math.pi*(ang1)/180
        angle2 = math.pi*(ang2)/180
        angle3 = math.pi*(ang3)/180

        d = 40  # weight to reduce the distance to a resonable region
        for i in range(1000):
            x1 = self.x+i*math.cos(angle1)
            y1 = self.y-i*math.sin(angle1)
            # detect track boundary (black color) (0, 0, 0, 255) or (0, 1, 0, 255)

            pixel = screen.get_at((int(x1), int(y1)))
            if pixel[0] <= 1 and pixel[1] <= 1 and pixel[2] <= 1:
                self.x1, self.y1 = x1, y1
                self.dis1 = math.sqrt((self.x-x1)**2+(self.y-y1)**2)/d
                break

        for i in range(1000):
            x2 = self.x+i*math.cos(angle2)
            y2 = self.y-i*math.sin(angle2)
            # detect track boundary (black color) (0, 0, 0, 255) or (0, 1, 0, 255)
            pixel = screen.get_at((int(x2), int(y2)))
            if pixel[0] <= 1 and pixel[1] <= 1 and pixel[2] <= 1:
                self.x2, self.y2 = x2, y2
                self.dis2 = math.sqrt((self.x-x2)**2+(self.y-y2)**2)/d
                break

        for i in range(1000):
            x3 = self.x+i*math.cos(angle3)
            y3 = self.y-i*math.sin(angle3)
            # detect track boundary (black color) (0, 0, 0, 255) or (0, 1, 0, 255)
            pixel = screen.get_at((int(x3), int(y3)))
            if pixel[0] <= 1 and pixel[1] <= 1 and pixel[2] <= 1:
                self.x3, self.y3 = x3, y3
                self.dis3 = math.sqrt((self.x-x3)**2+(self.y-y3)**2)/d
                break

    def draw(self, color='blue'):
        # draw car itself
        if color == 'blue':
            pg.draw.circle(screen, (0, 0, 255), (int(
                self.x), int(self.y)), 8, 0)  # replace car as circle
        elif color == 'yellow':
            pg.draw.circle(screen, (255, 255, 0), (int(
                self.x), int(self.y)), 8, 0)  # replace car as circle
        elif color == 'red':
            pg.draw.circle(screen, (255, 0, 0), (int(
                self.x), int(self.y)), 8, 0)  # replace car as circle


def create_car_agents():
    cars = []
    for i in range(num):
        car = Car()
        cars.append(car)
    return cars


def main():
    fps = 0
    count = 0
    alive = 0

    start = time.time()
    begin = time.time()
    last_round_time = begin
    current_gen = 1
    clock = pg.time.Clock()

    run = True  # running status
    pause = False  # pause status

    mannual_select = False
    flag_next_gen = False

    # create cars
    cars = create_car_agents()

    # create networks
    nets = []
    for i in range(num):
        nets.append(NeuralNetwork())

    # main loop
    while run:
        clock.tick(FPS)  # set fps

        for event in pg.event.get():
            if event.type == pg.QUIT:
                run = False
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_p:  # Key 'P' to pause
                    pause = not pause
                if event.key == pg.K_SPACE:  # Key 'Space' to enter next gen
                    if alive == 0 and mannual_select == True:
                        mannual_select = False
                        flag_next_gen = True
                        print('Next generation!')
                        # top elites' networks
                        elites = get_elites2(nets, cars)

                        # next generation's networks list
                        next_gen_nets = []

                        # add this generation's elites directly to next generation
                        next_gen_nets.extend(elites)

                        # add this generation's elites' children to next generation
                        while len(next_gen_nets) < int(1*len(cars)/4):
                            temp_elites = copy.deepcopy(elites)
                            temp_elites = mutate(
                                temp_elites, pm, mutate_elites_range)
                            next_gen_nets.extend(temp_elites)

                        # create hybrid children and add them to next geration until enough
                        temp_elites = copy.deepcopy(elites)
                        for i in range(len(cars)-len(next_gen_nets)):
                            child = crossover2(temp_elites)
                            child = mutate(child, pm, mutate_range)
                            next_gen_nets.append(child)

                        # mutate next generation's each network including elites and children
                        # next_gen_nets = mutate(next_gen_nets, pm, mutate_range)

                        # recreate new cars
                        cars = create_car_agents()

                        nets = next_gen_nets
                        last_round_time = time.time()

                        # quit when gen was enough
                        current_gen += 1

                        if current_gen > generation:
                            run = False

            if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:  # 按下鼠标左键
                if alive == 0:
                    x, y = pg.mouse.get_pos()
                    for i in range(len(cars)):
                        if cars[i].x - 8 <= x <= cars[i].x+8 and cars[i].y - 8 <= y <= cars[i].y+8:
                            cars[i].selected = True
                            mannual_select = True

        if pause:
            continue

        # calculate fps
        count += 1
        now = time.time()
        if now-start > 0.1:
            fps = count/(now-start)
            start = now
            count = 0

        screen.blit(background, (0, 0))  # draw background

        for i in range(len(cars)):
            if cars[i].isAlive:
                # calculate distance from car to track boundary
                try:
                    cars[i].calculate_three_distance()
                except:
                    continue

                angle, speed = nets[i].feedforward(
                    [cars[i].dis1, cars[i].dis2, cars[i].dis3])  # get network's output

                # normalize speed and angle
                if speed < min_speed:
                    speed = min_speed
                if speed > max_speed:
                    speed = max_speed

                # if angle < -180:
                #     angle = -180
                # if angle > 180:
                #     angle = 180

                # update speed and angle only every time interval
                if cars[i].counter >= min_angle_speed_change_frame_interval:
                    cars[i].counter = 0
                    cars[i].angle += angle*12
                    cars[i].speed = speed
                else:
                    cars[i].counter += 1

                cars[i].update_position()  # update position
                cars[i].detect_track_boundary()  # detect collide

        # change to dead if time beyond 30 seconds
        if time.time()-last_round_time > gen_max_time:
            for i in range(len(cars)):
                if cars[i].isAlive:
                    cars[i].isAlive = False

        # ========================== drawing part ==========================
        alive = 0  # survive numbers
        for i in range(len(cars)):
            if i == 0:
                if cars[i].selected:
                    cars[i].draw('red')  # draw car itself
                else:
                    cars[i].draw('yellow')  # No.1 car marked yellow
            else:
                if cars[i].selected:
                    cars[i].draw('red')  # draw car itself
                else:
                    cars[i].draw('blue')  # draw car itself
            if cars[i].isAlive:
                alive += 1  # calculate alive members
                cars[i].draw_indicator_line()  # draw three indicator lines

        # draw params on the screen
        draw_text("Gen: "+str(current_gen), (900, 10), (0, 0, 255))
        draw_text("All: "+str(len(cars)), (900, 30), (0, 0, 255))
        draw_text("Alive: "+str(alive), (900, 50), (0, 0, 255))
        draw_text("Top1 distance: " +
                  str(int(cars[0].distance)), (900, 70), (0, 0, 255))
        draw_text("Total time: " +
                  str(int(time.time()-begin)), (900, 90), (0, 0, 255))
        draw_text("This round time: " +
                  str(int(time.time()-last_round_time)), (900, 110), (0, 0, 255))
        draw_text("Fps:"+str(round(fps, 5)), (10, 10), (0, 0, 255))
        mouse_pos_x, mouse_pos_y = pg.mouse.get_pos()  # get mouse's position
        draw_text('pos_x:'+str(mouse_pos_x)+'  pos_y:' +
                  str(mouse_pos_y), (10, 30), (0, 0, 255))
        draw_text(str(screen.get_at((mouse_pos_x, mouse_pos_y))),
                  (10, 70), (0, 0, 255))
        draw_text("Press 'p' to pause!", (10, 50), (0, 0, 255))

        pg.display.update()

        # when this gen was over
        if alive == 0:
            if flag_next_gen == False:
                continue

    pg.quit()


if __name__ == "__main__":
    main()
