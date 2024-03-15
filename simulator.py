import mujoco
import mujoco_viewer
import dm_control.mujoco
import time
import numpy
import math
import xml.etree.ElementTree as XMLTree

DEF_WAVE_SIZE = 360

class Simulator:
    environment = None
    m = None
    d = None

    def __init__(self):
        pass

    # environment is of type Environment
    def load_env(self, environment):
        self.environment = environment
        envXML = XMLTree.tostring(self.environment.root)
        self.m = mujoco.MjModel.from_xml_string(envXML)
        self.d = mujoco.MjData(self.m)

    def activate_motors(self, step):
        # activate all motors
        for mname in self.environment.motor_data:
            motor = self.environment.motor_data[mname]
            id = dm_control.mujoco.mj_name2id(self.m, mujoco.mjtObj.mjOBJ_ACTUATOR, mname)
            self.d.ctrl[id] = motor.strength*math.sin((step*int(motor.frequency) + motor.offset) /-(DEF_WAVE_SIZE/(2*numpy.pi)))

    def run_sim(self, num_steps):
        for step in range(num_steps):
            self.activate_motors(step)
            mujoco.mj_step(self.m, self.d)

    def view_sim(self, num_steps):

        viewer = mujoco_viewer.MujocoViewer(self.m, self.d)

        # set camera view
        viewer.cam.azimuth = 200
        viewer.cam.elevation = -16
        viewer.cam.distance = 3.5
        viewer.cam.lookat[:] = [0.0, 0.0, 0.75]
        
        # start sim
        step = 0
        while viewer.is_alive and step < num_steps:

            self.activate_motors(step)
            mujoco.mj_step(self.m, self.d)
            step += 1

            viewer.render()
            time.sleep(0.01)

        viewer.close()
        
    
    def score(self):
        return self.d.body("rootnode").xpos[0]
