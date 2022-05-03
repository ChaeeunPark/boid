from p5 import setup, draw, size, background, run
import numpy as np
from boid import Boid


width = 1000
height = 1000

start_width = 100
start_height = 100

#left top start
flock = [Boid(*np.random.rand(2)*250, width, height) for _ in range(50)]
#original start
#flock = [Boid(*np.random.rand(2)*1000, width, height) for _ in range(50)]

intell = Boid(*np.random.rand(2)*250, width, height)

def setup():
    #this happens just once
    size(width, height) #instead of create_canvas


def draw():
    global flock
    
    background(30, 30, 47)
    
    intell.intelligent()
    intell.intelligent_v()
    intell.direction()
    intell.update()

    for boid in flock:
        boid.edges()
        boid.apply_behaviour(flock)
        boid.update()
        boid.show()
        




#run(frame_rate=100)
#run(frame_rate=200)
run()