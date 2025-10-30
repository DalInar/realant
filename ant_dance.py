# Licensed under MIT licence, see LICENSE for details.
# Copyright Ote Robotics Ltd. 2020
import math

import zmq
import time

ctx = zmq.Context()
sock = ctx.socket(zmq.PUB)
sock.connect("tcp://127.0.0.1:3002")

def standup(pause: float):
    sock.send_multipart([b"cmd", b"s1 224 s2 512 s3 224 s4 512 s5 224 s6 512 s7 224 s8 512\n"])
    time.sleep(pause)

def twist(angle: float, pause: float):
    motor_position = int(512+(angle/90)*(512-224))
    print(motor_position)
    motor_position_str = f"s2 {motor_position} s4 {motor_position} s6 {motor_position} s8 {motor_position}\n"
    #sock.send_multipart([b"cmd", b"s2 224 s4 224 s6 224 s8 224\n"])
    sock.send_multipart([b"cmd", bytes(motor_position_str, "utf-8")])
    time.sleep(pause)

def slant(angle:float, pause: float):
    motor_position = int(512+(angle/90)*(512-224))
    mpos_1  = 368+144*math.cos(math.radians(angle) - 0)
    mpos_3  = 368+144*math.cos(math.radians(angle) - math.pi/2)
    mpos_5  = 368+144*math.cos(math.radians(angle) - math.pi)
    mpos_7  = 368+144*math.cos(math.radians(angle) - 3*math.pi/2)

    motor_position_str = f"s1 {mpos_1} s3 {mpos_3} s5 {mpos_5} s7 {mpos_7}\n"
    sock.send_multipart([b"cmd", bytes(motor_position_str, "utf-8")])
    time.sleep(pause)

time.sleep(0.1)
sock.send_multipart([b"cmd", b"attach_servos\n"])
time.sleep(0.1)
#sock.send_multipart([b"cmd", b"s1 512 s2 512 s3 512 s4 512 s5 512 s6 512 s7 512 s8 512\n"])
#time.sleep(1)
#sock.send_multipart([b"cmd", b"s1 224 s2 512 s3 512 s4 512 s5 512 s6 512 s7 512 s8 512\n"])
#time.sleep(1)
standup(1)

slant_angle = 0
slant_increase = 20
for i in range(0, 100):
    print(slant_angle)
    slant(slant_angle, pause=0.1)
    slant_angle += slant_increase

    if i==50:
        slant_increase *= -1
# slant(0, 1)
# slant(90, 1)
# slant(180, 1)
# slant(270, 1)
# slant(0, 1)
#twist(45, 1)
#twist(-45, 1)
sock.send_multipart([b"cmd", b"reset\n"])
time.sleep(1)
sock.send_multipart([b"cmd", b"detach_servos\n"])

sock.close()
ctx.term()
