import cv2
import hyperlpr3 as lpr3
import datetime
target_width = 800
target_height = 640
pause_frame_list = []
# cap = cv2.VideoCapture("C:/Users/41384/Desktop/0bdf-ixkvvuc2483767.jpg")  # 参数0表示使用默认摄像头，如果有多个摄像头可以选择其他参数

cap = cv2.VideoCapture(0)
catcher = lpr3.LicensePlateCatcher()
cap1 = cv2.VideoCapture(1)
def read_txt():
    while True:
        ret, frame = cap.read()  # 读取视频帧
        if not ret:
            break
        frame_list = catcher(frame)

        if frame_list:
            return frame_list


def read_frames():
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frame = cv2.resize(frame, (target_width, target_height))
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

def read_txtout():
    while True:
        ret, frame = cap1.read()  # 读取视频帧
        if not ret:
            break
        frame_list = catcher(frame)

        if frame_list:
            return frame_list

def read_out():
    while True:
        ret, frame = cap1.read()
        if not ret:
            break
        frame = cv2.resize(frame, (target_width, target_height))
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

# cap.release()  # 释放摄像头资源
cv2.destroyAllWindows()
if __name__ == '__main__':
    data = read_txt()
    print(data)
    # 把{'frame_list': [['京AHK666', 0.81118625, 0, [261, 28, 366, 65]]],
    #  'time': datetime.datetime(2023, 11, 6, 7, 19, 25, 878208)}变成字典
    f_list = data['frame_list'][0]

    time = data['time']

    time = time.strftime('%Y-%m-%d %H:%M:%S')
    print(time)  # 2023-11-06 07:19:25.878208

    print(f_list)
    print(f_list[0])

    data = {
        "v": f_list[0],
        "time": time
    }
