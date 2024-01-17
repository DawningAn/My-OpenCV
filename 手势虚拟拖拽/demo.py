import cv2
import numpy as np
import math

import mediapipe as mp

# mediapipe获取手指关键点坐标
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_hands = mp.solutions.hands

# 设置方块颜色
square_color = (255, 255, 0)

hands = mp_hands.Hands(
    model_complexity=0,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5)

# 获取摄像头视频流
cap = cv2.VideoCapture(0)

# 获取画面宽度、高度
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

square_x = 100
square_y = 100
square_width = 100
square_high = 100

L1 = 0
L2 = 0
on_square = False
while True:
    ret, frame = cap.read()

    # 镜像
    frame = cv2.flip(frame, 1)

    frame.flags.writeable = False
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    # 识别
    results = hands.process(frame)

    frame.flags.writeable = True
    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

    # 如果有结果（有手出现）
    if results.multi_hand_landmarks:

        # 遍历双手
        for hand_landmarks in results.multi_hand_landmarks:
            # 绘制关键点
            mp_drawing.draw_landmarks(
                frame,
                hand_landmarks,
                mp_hands.HAND_CONNECTIONS,
                mp_drawing_styles.get_default_hand_landmarks_style(),
                mp_drawing_styles.get_default_hand_connections_style())

            # 使用这两句看一下里面到底是什么？
            # print(type(hand_landmarks))
            # print(hand_landmarks)
            # exit()

            # 21 个关键点的x,y坐标列表
            x_list = []
            y_list = []
            for landmark in hand_landmarks.landmark:  # x y z
                x_list.append(landmark.x)
                y_list.append(landmark.y)

            # 获取食指指尖坐标，坐标位置查看：https://google.github.io/mediapipe/solutions/hands
            index_finger_x = int(x_list[8] * width)
            index_finger_y = int(y_list[8] * height)

            # 获取中指坐标
            middle_finger_x = int(x_list[12] * width)
            middle_finger_y = int(y_list[12] * height)

            # 计算两指距离
            # finger_distance =math.sqrt( (middle_finger_x - index_finger_x)**2 + (middle_finger_y-index_finger_y)**2)
            finger_distance = math.hypot((middle_finger_x - index_finger_x), (middle_finger_y - index_finger_y))  #
            print("distence:", finger_distance)

            # 如果距离小于30算激活，否则取消激活，不跟随
            if finger_distance < 30:
                # 判断食指指尖是否在方块内
                if ((index_finger_x > square_x and index_finger_x < square_x + square_width) and
                        (index_finger_y > square_y and index_finger_y < square_y + square_high)):
                    if on_square == False:
                        print("在方块上")
                        L1 = abs(index_finger_x - square_x)
                        L2 = abs(index_finger_y - square_y)
                        on_square = True
                        square_color = (0, 0, 255)
                else:
                    # print("不在方块上")
                    pass

            else:
                # 取消激活
                square_color = (255, 255, 0)
                on_square = False

            # 如何跟随移动
            if on_square:
                square_x = index_finger_x - L1
                square_y = index_finger_y - L2

        # 画方块
        # cv2.rectangle(frame, (square_x, square_y), (square_x + square_width, square_y + +square_high),
        #               (0, 255, 0), -1)
        # 半透明处理
        overlay = frame.copy()
        cv2.rectangle(frame, (square_x, square_y), (square_x + square_width, square_y + square_high), square_color, -1)
        frame = cv2.addWeighted(overlay, 0.5, frame, 1 - 0.5, 0)
        cv2.imshow("Video", frame)
        if cv2.waitKey(10) & 0xFF == 27:
            break

cap.release()
cv2.destroyAllWindows()
