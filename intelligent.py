import argparse
import math
import random
from statistics import mean
from tkinter import *



class Field:
    WIDTH = 1000
    HEIGHT = 750


class Coordinate():
    def __init__(self):
        self.reset()

    def reset(self):
        self.x = 0
        self.y = 0


class Bird():
    NUM = 40 
    RADIAN = 3
    SPEED = 4

    # 생성자
    def __init__(self, args):
        self.x = random.randint(50, 100) #start position
        self.y = random.randint(350, 400)
#        self.vx = random.randint(-self.SPEED, self.SPEED)
#        self.vy = random.randint(-self.SPEED, self.SPEED)
        self.vx = 0
        self.vy = 0
        self.r1 = args.r1
        self.r2 = args.r2
        self.r3 = args.r3
        self.center_pull = args.center_pull
        self.view = args.view

        self.neighbors = None

        self.v1 = Coordinate()
        self.v2 = Coordinate()
        self.v3 = Coordinate()

    def find_neighbors(self):
        self.neighbors = [agent for agent in self.birds if agent is not self and self.calc_distance(agent) <= self.view]

    def calc_distance(self, target):
        return math.sqrt((target.x - self.x) ** 2 + (target.y - self.y) ** 2)

    def cohesion(self):
        if not self.neighbors:
            return

        self.v1.x = mean([agent.x for agent in self.neighbors if agent is not self])
        self.v1.y = mean([agent.y for agent in self.neighbors if agent is not self])

        self.v1.x = (self.v1.x - self.x) / self.center_pull
        self.v1.y = (self.v1.y - self.y) / self.center_pull

    def separation(self):
        personal_space = 10
        for bird in self.neighbors:
            if bird == self:
                continue
            dist = self.calc_distance(bird)
            if dist == 0:
                continue
            if dist < personal_space:
                self.v2.x -= (bird.x - self.x) / 2
                self.v2.y -= (bird.y - self.y) / 2

    def alignment(self):
        if not self.neighbors:
            return

        self.v3.x = mean([agent.vx for agent in self.neighbors if agent is not self])
        self.v3.y = mean([agent.vy for agent in self.neighbors if agent is not self])

        self.v3.x = (self.v3.x - self.vx) / 2
        self.v3.y = (self.v3.y - self.vy) / 2

    def intelligent_direction(self):
        #종착지에 맞춰서 계속 바꾸기
        end_x = Field.WIDTH
        end_y = Field.HEIGHT

        self.vx = (end_x-self.x)
            
        self.v3.x = self.vx/self.SPEED

    def _collision_detection(self):
        if self.x - Bird.RADIAN < 0:
            self.vx *= -1
            self.x = Bird.RADIAN
        if self.x + Bird.RADIAN > Field.WIDTH:
            self.vx *= -1
            self.x = Field.WIDTH - Bird.RADIAN

        if self.y - Bird.RADIAN < 0:
            self.vy *= -1
            self.y = Bird.RADIAN
        if self.y + Bird.RADIAN > Field.HEIGHT:
            self.vy *= -1
            self.y = Field.HEIGHT - Bird.RADIAN

    def step(self):
        self.cohesion()
        self.separation()
        self.alignment()

    def intelligent_step(self):
        self.cohesion()
        self.separation()
        self.intelligent_direction()

    def update(self):
        dx = self.r1 * self.v1.x + self.r2 * self.v2.x + self.r3 * self.v3.x
        dy = self.r1 * self.v1.y + self.r2 * self.v2.y + self.r3 * self.v3.y
        self.vx += dx
        self.vy += dy

        distance = (self.vx ** 2 + self.vy ** 2) ** 0.5

        if distance > self.SPEED:
            self.vx = (self.vx / distance) * self.SPEED
            self.vy = (self.vy / distance) * self.SPEED

        self.x += int(self.vx)
        self.y += int(self.vy)

        self._collision_detection()

    def clear_movement(self):
        self.v1.reset()
        self.v2.reset()
        self.v3.reset()

    def draw(self, drawer):
        self.clear_movement()
        self.step()
        self.update()
        drawer.create_oval(self.x - Bird.RADIAN, self.y - Bird.RADIAN, self.x + Bird.RADIAN, self.y + Bird.RADIAN)
        drawer.create_line(self.x, self.y, self.x + self.vx * 3, self.y + self.vy * 3)

    def intelligentdraw(self, drawer):
        self.clear_movement()
        self.intelligent_step()
        self.update()
        drawer.create_oval(self.x - Bird.RADIAN, self.y - Bird.RADIAN, self.x + Bird.RADIAN, self.y + Bird.RADIAN, fill = "red")
        drawer.create_line(self.x, self.y, self.x + self.vx * 3, self.y + self.vy * 3)

def main(args):
    Bird.birds = [Bird(args) for _ in range(Bird.NUM)]
    
    root = Tk()

    canvas = Canvas(root, width=Field.WIDTH, height=Field.HEIGHT)
    canvas.pack()

#   Bird.birds[0].x = 1
#   Bird.birds[0].y = 1

#   Bird.birds[1].x = 1
#   Bird.birds[1].y = 100

#   Bird.birds[2].x = 100
#   Bird.birds[2].y = 1

#    Bird.birds[3].x = 100
#    Bird.birds[3].y = 100

    def animate():
        canvas.delete("all")
        for bird in Bird.birds:    
            bird.find_neighbors()
            bird.draw(canvas)
        
        Bird.birds[0].intelligentdraw(canvas)
        root.after(20, animate)

    animate()
    root.mainloop()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Boids Model parameters')
    parser.add_argument('--r1', type=float, default=2.0, help='cohesion coefficient') #원래는 1.0
    parser.add_argument('--r2', type=float, default=0.8, help='separation coefficient')
    parser.add_argument('--r3', type=float, default=0.3, help='alignment coefficient')
    parser.add_argument('--center-pull', type=int, default=300,
                        help='center pull coefficient for means of neighbors coordinante')
    parser.add_argument('--view', type=int, default=50, help='view of each birds') #150
    args = parser.parse_args()
    main(args)

    