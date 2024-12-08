import boto3
import cv2
class FaceLandmarkProcessor:
    ''''二重を作成するclass'''
    
    def __init__(self, aws_access_key_id, aws_secret_access_key, region_name='ap-northeast-1'):
        #awsのアクセスキーをosから読み込む
        
        self.rekognition_client = boto3.client(
            'rekognition',
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name=region_name
        )
    
    def detect_faces_landmark(self, image_bytes):
        #顔認証をするための関数
        
        response = self.rekognition_client.detect_faces(
            Image={'Bytes': image_bytes}, 
            Attributes=['ALL']
        )
        return response

    def draw_double_eye_ellipse(self, img, eye_center, size, angle, start_angle, end_angle, color=(68, 92, 135), thickness=2):
        #opencvの描画機能で二重の線を描く
        
        cv2.ellipse(
            img,
            eye_center,
            size,
            angle,
            start_angle,
            end_angle,
            color,
            thickness
        )

    def left_eye_point(self, landmarks):
        #左目、４点の座標を取ってくる
        
        left_eye_left = landmarks['leftEyeLeft']
        left_eye_right = landmarks['leftEyeRight']
        left_eye_up = landmarks['leftEyeUp']
        left_eye_down = landmarks['leftEyeDown']
        return left_eye_left, left_eye_right, left_eye_up, left_eye_down
    
    def right_eye_point(self, landmarks):
        #右目、４点の座標を取ってくる
        
        right_eye_left = landmarks['rightEyeLeft']
        right_eye_right = landmarks['rightEyeRight']
        right_eye_up = landmarks['rightEyeUp']
        right_eye_down = landmarks['rightEyeDown']
        return right_eye_left, right_eye_right, right_eye_up, right_eye_down
    
    def calculate_Eye_Position_Draw(self, image, landmarks, roll_angle, height_factor=0.99):
        #二重線の位置を調整するための関数
        
        left_eye_left, left_eye_right, left_eye_up, left_eye_down = self.left_eye_point(landmarks)
        right_eye_left, right_eye_right, right_eye_up, right_eye_down = self.right_eye_point(landmarks)
        
        left_eye_center = ((left_eye_left[0] + left_eye_right[0]) // 2, 
                           (left_eye_up[1] + left_eye_down[1]) // 2)
        
        right_eye_center = ((right_eye_left[0] + right_eye_right[0]) // 2, 
                            (right_eye_up[1] + right_eye_down[1]) // 2)
        
        left_eye_width = left_eye_right[0] - left_eye_left[0]
        left_eye_height = left_eye_down[1] - left_eye_up[1]
        
        right_eye_width = right_eye_right[0] - right_eye_left[0]
        right_eye_height = right_eye_down[1] - right_eye_up[1]

        right_eyelid_height = int(right_eye_up[1] * height_factor)
        left_eyelid_height = int(left_eye_up[1] * height_factor)
        
        right_double_eyelid_center = (right_eye_center[0] + 8, right_eyelid_height + 12)
        left_double_eyelid_center = (left_eye_center[0] - 4, left_eyelid_height + 13)
        
        double_eye_width = 16
        double_eye_height = 9
        start_angle = 190
        end_angle = 360
        
        self.draw_double_eye_ellipse(image, left_double_eyelid_center, 
                                    (left_eye_width - double_eye_width, left_eye_height + double_eye_height),
                                    roll_angle, start_angle, end_angle, color=(68, 92, 135), thickness=2)
        
        self.draw_double_eye_ellipse(image, right_double_eyelid_center, 
                                    (right_eye_width - double_eye_width, right_eye_height + double_eye_height),
                                    roll_angle, start_angle, end_angle, color=(68, 92, 135), thickness=2)
        
    def draw_landmarks(self, image, face_details, height, width):
        #ランドマークの情報を読み込み、首の傾きから線を傾かせる
        for face_detail in face_details:
            landmarks = {landmark['Type']: (int(landmark['X'] * width), int(landmark['Y'] * height)) 
                        for landmark in face_detail['Landmarks']}
        
        pose = face_detail['Pose']
        roll_angle = pose['Roll']
        
        self.calculate_Eye_Position_Draw(image, landmarks, roll_angle)