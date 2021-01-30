
from pytesseract import image_to_string
import cv2
import re


def resize_img(img, scale_percentage):
    w = int(img.shape[1] * scale_percentage / 100)
    h = int(img.shape[0] * scale_percentage / 100)
    dsize = (w, h)
    resized = cv2.resize(img, dsize)
    return resized


def erosion_img(erosion_size, img):
    element = cv2.getStructuringElement(
        cv2.MORPH_RECT,
        (2 * erosion_size + 1, 2 * erosion_size + 1),
        (erosion_size, erosion_size),
    )
    eroded = cv2.erode(img, element)
    return eroded


def binary_img(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
    return thresh


def process_stats(file):
    image = cv2.imread(file)
    output_img = erosion_img(1, binary_img(erosion_img(1, resize_img(image, 200))))
    output = image_to_string(output_img, config="--psm 6")
    """cv2.imshow('output', output_img)
    cv2.waitKey()"""

    pattern = re.compile(r"\s\d+\n")
    matches = re.findall(pattern, output)
    if len(matches) == 18:
        stats = {
            "Bodies Reported": int(matches[0]),
            "Emergencies Called": int(matches[1]),
            "Tasks Completed": int(matches[2]),
            "All Tasks Completed": int(matches[3]),
            "Sabotages Fixed": int(matches[4]),
            "Impostor Kills": int(matches[5]),
            "Times Murdered": int(matches[6]),
            "Times Ejected": int(matches[7]),
            "Crewmate Streak": int(matches[8]),
            "Times Impostor": int(matches[9]),
            "Times Crewmate": int(matches[10]),
            "Games Started": int(matches[11]),
            "Games Finished": int(matches[12]),
            "Impostor Vote Wins": int(matches[13]),
            "Impostor Kill Wins": int(matches[14]),
            "Impostor Sabotage Wins": int(matches[15]),
            "Crewmate Vote Wins": int(matches[16]),
            "Crewmate Task Wins": int(matches[17]),
        }
        """for k, v in stats.items():
            print(f'{k}: {" " * (25 - (len(k)))}{v}')"""
        print("Stats Read Successful")
    else:
        print("incorrect")
        stats = None

    return stats

