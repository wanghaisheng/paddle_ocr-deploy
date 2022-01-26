
import cv2
import time
import numpy as np

def detect_blur(image, threshold=500):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    fm = variance_of_laplacian(gray)
    result = 'NORMAL'
    if fm < threshold:
        result = 'BLUR'
    return result, fm

def detect_motion(frame1, frame2, threshold=5):
    # 帧间距离
    dist = distance(frame1, frame2)
    gaussionBlur = cv2.GaussianBlur(dist, (9,9), 0)
    _, cv_thresh = cv2.threshold(gaussionBlur, 100, 255, 0)
    # 方差
    _, standard = cv2.meanStdDev(gaussionBlur)
    result = 'Motionless'
    f_standard = standard[0][0]
    if f_standard > threshold:
        result = 'Motion'
    return result, f_standard

def variance_of_laplacian(image):
  # compute the Laplacian of the image and then return the focus
  # measure, which is simply the variance of the Laplacian
  return cv2.Laplacian(image, cv2.CV_64F).var()

def distance(frame1, frame2):
    diff = np.subtract(frame1, frame2)
    dist = np.sqrt(np.sum(np.square(diff), 1)) / np.sqrt(3 * (255**2))
    dist = np.uint8(dist*255)
    return dist

def detect_video(video, blur_threshold=500, motion_threshold=10, output_type='cv_frame'):
    print('开始解析摄像头视频流')
    start = time.time()
    lastFrame = None
    currentFrame = None

    while True:
        # 抓取每一帧图像
        # ret， 返回值，表示视频是否读完
        # frame， 实际图像帧
        ret, frame = video.read()    
        # 等比缩小图片，提高处理速度
        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

        lastFrame = currentFrame
        currentFrame = small_frame
        if lastFrame is None:
            lastFrame = currentFrame
        motion, motion_score= detect_motion(lastFrame, currentFrame, threshold=motion_threshold)

        # 检测运动

        # 检测模糊
        blur, blur_score = detect_blur(small_frame, threshold=blur_threshold)

        # 处理完成计算fps
        end = time.time()
        seconds = end - start
        fps  = 1 / seconds
        start = time.time()

        cv2.putText(frame, "FPS: {:.2f}, {}: {:.2f}, {}: {:.2f}".format(fps, blur, blur_score, motion, motion_score), (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

        # 输出播放
        if (output_type == 'cv_frame'):
            yield frame, fps, blur_score, motion_score
        else: 
            ret, jpeg = cv2.imencode('.jpg', frame)
            yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n\r\n'), fps, blur_score, motion_score

if __name__ == '__main__':
    import paddlehub as hub
    yolo = hub.Module(name="yolov3_mobilenet_v1_coco2017")
    np.random.seed(42)
    box_color = (255,0,255)
    label_color=(255, 255, 255)
    detected = False

    video_captures = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    frameGenerator = detect_video(video_captures, blur_threshold=2000, motion_threshold=5)
    results = list()
    for frame, fps, blur_score, motion_score in frameGenerator:
        output_frame = frame
        if (blur_score > 2000 and motion_score < 5):
            if not detected:
                detected = True
                results = yolo.object_detection(paths=None,
                    images=[output_frame],
                    batch_size=1,
                    use_gpu=False,
                    output_dir='output',
                    score_thresh=0.35,
                    visualization=False)
        else:
            detected = False

        for result in results:
            data = results[0].get('data')
            if len(data) > 0:
                for d in data:
                    left, top, right, bottom = int(d.get('left')), int(d.get('top')), int(d.get('right')), int(d.get('bottom'))
                    label = d.get('label')
                    cv2.rectangle(output_frame, (left, top), (right, bottom), color=box_color, thickness=2)
                    text = "{}: {:.4f}".format(label, d.get('confidence'))
                    cv2.putText(output_frame, text, (left, top - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, label_color, 2)

        # if (blur_score > 2000 and motion_score < 5):
        #     results = paddleDishes.dishesClassify([frame])
        #     for image, data in zip([frame], results):
        #         detected_frame = image
        #     output_frame = paddleDishes.draw_boxes(detected_frame, data)
        #     result = data['data']
        # else:
        #     result = None

        cv2.imshow('Video Detect', output_frame)
        # Hit 'q' on the keyboard to quit!
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    # When everything is done, release the capture
    print('正在关闭摄像头')
    video_captures.release()
    cv2.destroyAllWindows()