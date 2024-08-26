import cv2
import numpy as np
import pytesseract
from queue import Queue

pytesseract.pytesseract.tesseract_cmd = 'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'
CONFIG = '--oem 3 --psm 6 outputbase digits'

CANNOT_DETECT_BOARD = 2

def compute_origin(lr_point, peri):
    cell_width = peri//4//9
    origin = lr_point+10
    return origin, cell_width

def detect_board(image):
    WIDTH = HEIGHT = 1080
    AREA_THRES = 200000

    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blur_image = cv2.GaussianBlur(gray_image, (5, 5), 3)
    canny_image = cv2.Canny(blur_image, 50, 50)

    contours, hierachy = cv2.findContours(canny_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    max_contour = max(contours, key = lambda contour : cv2.contourArea(contour))

    if cv2.contourArea(max_contour) < 200000:
        return (None, None), None

    peri = cv2.arcLength(max_contour, True)
    approx = cv2.approxPolyDP(max_contour, 0.02*peri, True) # l-t, l-d, r-d, r-t

    origin, cell_width = compute_origin(approx[0][0], peri)

    points_src = np.float32([approx[0], approx[3], approx[1], approx[2]])
    points_dst = np.float32([[0, 0], [WIDTH, 0], [0, HEIGHT], [WIDTH, HEIGHT]])

    matrix = cv2.getPerspectiveTransform(points_src, points_dst)
    board_image = cv2.warpPerspective(gray_image, matrix, (WIDTH, HEIGHT))

    return (origin, cell_width), board_image

def extract_board(board_image):
    OFFSET = 10
    BOARD_SIZE = 9
    CELL_SIZE = 120

    board = np.zeros((BOARD_SIZE, BOARD_SIZE), dtype=np.int8)
    _, binary_image = cv2.threshold(board_image, 127, 255, cv2.THRESH_BINARY)

    for row in range(9):
        for col in range(9):
            cell = binary_image[row*CELL_SIZE+OFFSET : (row+1)*CELL_SIZE-OFFSET,
                                col*CELL_SIZE+OFFSET : (col+1)*CELL_SIZE-OFFSET]
            text = pytesseract.image_to_string(cell, config=CONFIG).replace('\n', '')
            board[row][col] = int(text) if text.isdigit() else 0
    
    return board

# use for thread, return board and origin (x, y) in image
def get_board(image, queue : Queue):
    (origin, cell_width), board_image = detect_board(image)

    if type(board_image) != np.ndarray:
        queue.put(((None, None), None))
    else:
        board = extract_board(board_image)
        queue.put(((origin, cell_width), board))
