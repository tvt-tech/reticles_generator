import cv2


body_cascade_db = cv2.CascadeClassifier("venv/Lib/site-packages/cv2/data/haarcascade_upperbody.xml")
lowerbody = cv2.CascadeClassifier("venv/Lib/site-packages/cv2/data/haarcascade_lowerbody.xml")
full_body = cv2.CascadeClassifier("venv/Lib/site-packages/cv2/data/haarcascade_fullbody.xml")
face = cv2.CascadeClassifier("venv/Lib/site-packages/cv2/data/haarcascade_frontalface_default.xml")

cap = cv2.VideoCapture(0)

# img = cv2.imread('peshehodi.jpg')

while True:
    success, img = cap.read()

    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # bodies = body_cascade_db.detectMultiScale(img_gray, 1.1, 4)
    # lowerb = lowerbody.detectMultiScale(img_gray, 1.1, 4)
    # fb = full_body.detectMultiScale(img_gray, 1.1, 4)
    faces = face.detectMultiScale(img_gray, 1.1, 4)

    # for (x, y, w, h) in bodies:
    #     cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 255), 1)
    # for (x, y, w, h) in lowerb:
    #     cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 1)
    # for (x, y, w, h) in fb:
    #     cv2.rectangle(img, (x, y), (x + w, y + h), (0, 0, 255), 1)
    for (x, y, w, h) in faces:
        cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 1)

    cv2.imshow('rez', img)
    if cv2.waitKey(1) & 0xff == ord('q'):
        break
        # pass
# cv2.waitKey()
cap.release()
cv2.destroyAllWindows()
