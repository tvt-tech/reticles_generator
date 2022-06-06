import cv2

ub = cv2.CascadeClassifier("venv/Lib/site-packages/cv2/data/haarcascade_upperbody.xml")
lb = cv2.CascadeClassifier("venv/Lib/site-packages/cv2/data/haarcascade_lowerbody.xml")
fb = cv2.CascadeClassifier("venv/Lib/site-packages/cv2/data/haarcascade_fullbody.xml")
face = cv2.CascadeClassifier("venv/Lib/site-packages/cv2/data/haarcascade_frontalface_default.xml")

# cap = cv2.VideoCapture(1)
#


def draw(cv2, src, dst):
    fbs = fb.detectMultiScale(src, 1.1, 4)
    ubs = ub.detectMultiScale(src, 1.1, 4)
    # lbs = lb.detectMultiScale(img_gray, 1.1, 4)
    # faces = face.detectMultiScale(inverted_image, 1.1, 4)


    for (x, y, w, h) in fbs:
        cv2.rectangle(dst, (x, y), (x + w, y + h), (0, 0, 255), 1)
        cv2.line(dst, (x - 3 + int(w / 2), y + int(h / 2)), (x + 3 + int(w / 2), y + int(h / 2)), (0, 0, 255), 1)
        cv2.line(dst, (x + int(w / 2), y - 3 + int(h / 2)), (x + int(w / 2), y + 3 + int(h / 2)), (0, 0, 255), 1)

        distance = int(1000 * 1.75 / (h / 7))
        cv2.putText(dst, f'{distance}m', (x, y + h + 10), cv2.FONT_HERSHEY_SIMPLEX, 0.4, thickness=1, color=(0, 0, 255))

    for (x, y, w, h) in ubs:
        cv2.rectangle(dst, (x, y), (x + w, y + h), (255, 0, 255), 1)
        cv2.line(dst, (x - 3 + int(w / 2), y + int(h / 2)), (x + 3 + int(w / 2), y + int(h / 2)), (255, 0, 255), 1)
        cv2.line(dst, (x + int(w / 2), y - 3 + int(h / 2)), (x + int(w / 2), y + 3 + int(h / 2)), (255, 0, 255), 1)

        distance = int(1000 * 0.9 / (h / 7))
        cv2.putText(dst, f'{distance}m', (x, y - 3), cv2.FONT_HERSHEY_SIMPLEX, 0.4, thickness=1, color=(255, 0, 255))

    # for (x, y, w, h) in lbs:
    #     cv2.rectangle(dst, (x, y), (x + w, y + h), (255, 0, 0), 1)
    #     cv2.line(dst, (x - 3 + int(w / 2), y + int(h / 2)), (x + 3 + int(w / 2), y + int(h / 2)), (255, 0, 0), 1)
    #     cv2.line(dst, (x + int(w / 2), y - 3 + int(h / 2)), (x + int(w / 2), y + 3 + int(h / 2)), (255, 0, 0), 1)
    # for (x, y, w, h) in faces:
    #     cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 1)
    #     cv2.line(dst, (x - 3 + int(w / 2), y + int(h / 2)), (x + 3 + int(w / 2), y + int(h / 2)), (0, 255, 0), 1)
    #     cv2.line(dst, (x + int(w / 2), y - 3 + int(h / 2)), (x + int(w / 2), y + 3 + int(h / 2)), (0, 255, 0), 1)

import os
import numpy as np

files = os.listdir(os.getcwd())
files = [f for f in files if f.endswith('.jpg') or f.endswith('.png')]

for f in files:

    img = cv2.imread(f)

    # lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
    # l_channel, a, b = cv2.split(lab)
    # clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    # cl = clahe.apply(l_channel)
    # limg = cv2.merge((cl, a, b))
    # enhanced_img = cv2.cvtColor(limg, cv2.COLOR_LAB2BGR)
    # img = np.vstack((img, enhanced_img))

    # while True:
    # success, img = cap.read()

    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    inverted_image = cv2.bitwise_not(img_gray)

    draw(cv2, img_gray, img)
    draw(cv2, inverted_image, img)

    cv2.imshow('rez', img)

    cv2.waitKey()

    # cv2.imshow('rez', img_gray)
    #
    # cv2.waitKey()
    #
    # cv2.imshow('rez', inverted_image)
    #
    # cv2.waitKey()

# cv2.imshow('rez', inverted_image)
# if cv2.waitKey(1) & 0xff == ord('q'):
#     break
# pass

# cap.release()
# cv2.destroyAllWindows()
