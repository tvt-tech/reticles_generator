import cv2

ub = cv2.CascadeClassifier("venv/Lib/site-packages/cv2/data/haarcascade_upperbody.xml")
lb = cv2.CascadeClassifier("venv/Lib/site-packages/cv2/data/haarcascade_lowerbody.xml")
fb = cv2.CascadeClassifier("venv/Lib/site-packages/cv2/data/haarcascade_fullbody.xml")
face = cv2.CascadeClassifier("venv/Lib/site-packages/cv2/data/haarcascade_frontalface_default.xml")

# cap = cv2.VideoCapture(1)
#
img = cv2.imread('pic.jpg')

# while True:
# success, img = cap.read()

img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
inverted_image = cv2.bitwise_not(img_gray)

fbs = fb.detectMultiScale(inverted_image, 1.1, 4)
ubs = ub.detectMultiScale(inverted_image, 1.1, 4)
lbs = lb.detectMultiScale(inverted_image, 1.1, 4)
# faces = face.detectMultiScale(inverted_image, 1.1, 4)

for (x, y, w, h) in fbs:
    cv2.rectangle(img, (x, y), (x + w, y + h), (0, 0, 255), 1)
    cv2.line(img, (x - 3 + int(w / 2), y + int(h / 2)), (x + 3 + int(w / 2), y + int(h / 2)), (0, 0, 255), 1)
    cv2.line(img, (x + int(w / 2), y - 3 + int(h / 2)), (x + int(w / 2), y + 3 + int(h / 2)), (0, 0, 255), 1)

    distance = round(1000 * 2 / (h / 7), 2)
    print(distance, h)
    cv2.putText(img, f'{distance}m', (x, y - 3), cv2.FONT_HERSHEY_SIMPLEX, 0.4, thickness=1, color=(255, 255, 255))

for (x, y, w, h) in ubs:
    cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 255), 1)
    cv2.line(img, (x - 3 + int(w / 2), y + int(h / 2)), (x + 3 + int(w / 2), y + int(h / 2)), (255, 0, 255), 1)
    cv2.line(img, (x + int(w / 2), y - 3 + int(h / 2)), (x + int(w / 2), y + 3 + int(h / 2)), (255, 0, 255), 1)
for (x, y, w, h) in lbs:
    cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 1)
    cv2.line(img, (x - 3 + int(w / 2), y + int(h / 2)), (x + 3 + int(w / 2), y + int(h / 2)), (255, 0, 0), 1)
    cv2.line(img, (x + int(w / 2), y - 3 + int(h / 2)), (x + int(w / 2), y + 3 + int(h / 2)), (255, 0, 0), 1)
# for (x, y, w, h) in faces:
#     cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 1)
#     cv2.line(img, (x - 3 + int(w / 2), y + int(h / 2)), (x + 3 + int(w / 2), y + int(h / 2)), (0, 255, 0), 1)
#     cv2.line(img, (x + int(w / 2), y - 3 + int(h / 2)), (x + int(w / 2), y + 3 + int(h / 2)), (0, 255, 0), 1)

cv2.imshow('rez', img)
# if cv2.waitKey(1) & 0xff == ord('q'):
#     break
# pass
cv2.waitKey()
# cap.release()
# cv2.destroyAllWindows()
