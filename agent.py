import pyautogui

class Agent:
    def __init__(self, origin, cell_width):
        self.origin = origin
        self.cell_width = cell_width

    def get_pos(self, coor):
        pos = (self.origin[0] + coor[1]*self.cell_width,
               self.origin[1] + coor[0]*self.cell_width)
        return pos

    def fill(self, coor, value):
        pos = self.get_pos(coor)
        pyautogui.click(pos[0], pos[1])
        pyautogui.press(str(value))