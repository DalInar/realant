# Licensed under MIT licence, see LICENSE for details.
# Copyright Ote Robotics Ltd. 2020
import math
import random
import zmq
import time

ctx = zmq.Context()
sock = ctx.socket(zmq.PUB)
sock.connect("tcp://127.0.0.1:3002")

leg_def = {
    0: {
        "hip": "s2",
        "knee": "s1"
    },
    1: {
        "hip": "s4",
        "knee": "s3"
    },
    2: {
        "hip": "s6",
        "knee": "s5"
    },
    3: {
        "hip": "s8",
        "knee": "s7"
    }
}

def standup(pause: float):
    sock.send_multipart([b"cmd", b"s1 224 s2 512 s3 224 s4 512 s5 224 s6 512 s7 224 s8 512\n"])
    time.sleep(pause)

def twist(angle: float, pause: float):
    motor_position = int(512+(angle/90)*(512-224))
    motor_position_str = f"s2 {motor_position} s4 {motor_position} s6 {motor_position} s8 {motor_position}\n"
    #sock.send_multipart([b"cmd", b"s2 224 s4 224 s6 224 s8 224\n"])
    sock.send_multipart([b"cmd", bytes(motor_position_str, "utf-8")])
    time.sleep(pause)

def slant(angle:float, pause: float, slant_mag: int=144):
    motor_position = int(512+(angle/90)*(512-224))
    mpos_1  = 368+slant_mag*math.cos(math.radians(angle) - 0)
    mpos_3  = 368+slant_mag*math.cos(math.radians(angle) - math.pi/2)
    mpos_5  = 368+slant_mag*math.cos(math.radians(angle) - math.pi)
    mpos_7  = 368+slant_mag*math.cos(math.radians(angle) - 3*math.pi/2)

    motor_position_str = f"s1 {mpos_1} s3 {mpos_3} s5 {mpos_5} s7 {mpos_7}\n"
    sock.send_multipart([b"cmd", bytes(motor_position_str, "utf-8")])
    time.sleep(pause)

def point(leg:int, pause: float):
    point_leg = leg
    left_leg = (point_leg + 1)%4
    right_leg = (point_leg + 3)%4
    back_leg = (point_leg + 2)%4

    right_leg_cmd = f"{leg_def[right_leg]['hip']} {512+100} {leg_def[right_leg]['knee']} 300"
    left_leg_cmd = f"{leg_def[left_leg]['hip']} {512-100} {leg_def[left_leg]['knee']} 300"
    cmd_str = f"{right_leg_cmd} {left_leg_cmd}\n"
    sock.send_multipart([b"cmd", bytes(cmd_str, "utf-8")])
    time.sleep(0.2)

    point_leg_cmd = f"{leg_def[point_leg]['hip']} 512 {leg_def[point_leg]['knee']} 512"
    back_leg_cmd = f"{leg_def[back_leg]['hip']} 512 {leg_def[back_leg]['knee']} 600"
    cmd_str = f"{point_leg_cmd} {back_leg_cmd}\n"
    sock.send_multipart([b"cmd", bytes(cmd_str, "utf-8")])

    time.sleep(pause)

def wiggle_leg(leg:int, num_rots: int, pause:float):
    angle = 0
    while angle < 360*num_rots:
        hip_pos = 512+70*math.cos(math.radians(angle))
        knee_pos = 512+70*math.sin(math.radians(angle))
        leg_cmd = f"{leg_def[leg]['hip']} {hip_pos} {leg_def[leg]['knee']} {knee_pos}"
        cmd_str = f"{leg_cmd}\n"
        sock.send_multipart([b"cmd", bytes(cmd_str, "utf-8")])
        angle+=20
        time.sleep(0.1)
    time.sleep(pause)

def spin_dance(slant_mag: int=144):
    slant_angle = 0
    slant_increase = 20
    for i in range(0, 100):
        slant(slant_angle, pause=0.1, slant_mag=slant_mag)
        slant_angle += slant_increase

        if i == 50:
            slant_increase *= -1

def twist_dance(angle_mag: float, pause_tempo: float):
    standup(0.5)
    twist(angle_mag, pause=pause_tempo)
    twist(-angle_mag, pause=pause_tempo)
    twist(angle_mag, pause=pause_tempo)
    twist(-angle_mag, pause=pause_tempo)
    time.sleep(1)

time.sleep(0.1)
sock.send_multipart([b"cmd", b"attach_servos\n"])
time.sleep(0.1)
standup(2)

try:
    while True:
        standup(0.1)

        for i in range(0, 3):
            k = random.randint(0,3)
            if k==0:
                twist_dance(40, 0.75)
            elif k==1:
                twist_dance(20, 0.25)
            elif k==2:
                spin_dance(slant_mag=80)
        standup(0.1)
        pause = 10*random.random()+3
        time.sleep(pause)

except KeyboardInterrupt:
    standup(0.2)
    sock.send_multipart([b"cmd", b"detach_servos\n"])
    sock.close()
    ctx.term()
    print("Ending the dance")
