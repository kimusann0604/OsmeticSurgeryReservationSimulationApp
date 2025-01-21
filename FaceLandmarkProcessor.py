import cv2
import mediapipe as mp
import numpy as np
from scipy.interpolate import CubicSpline

class EyeLandmarkProcessor:
    def initialize_face_mesh(self):
        mp_face_mesh = mp.solutions.face_mesh
        face_mesh = mp_face_mesh.FaceMesh(
            static_image_mode=True,
            max_num_faces=2,
            refine_landmarks=True,
            min_detection_confidence=0.8,
            min_tracking_confidence=0.8
        )
        return face_mesh

    def image_path(self, file_path):
        """
        画像を読み込み、RGB形式に変換します。
        """
        image = cv2.imread(file_path)
        if image is None:
            raise FileNotFoundError(f"画像が見つかりません: {file_path}")
        img = image.copy()
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        print(f"画像を読み込みました")
        return img_rgb

    def process_landmarks_and_create_mask(self, face_mesh, img_rgb, img,image, color=None):
        """
        顔のランドマークを検出し、目の部分にマスクを適用します。
        """
        # 顔のランドマーク検出
        results = face_mesh.process(img_rgb)

        if not results.multi_face_landmarks:
            print("顔が検出されませんでした。")
            return img  # 元の画像を返す

        for face_landmarks in results.multi_face_landmarks:
            # 左目と右目のランドマークインデックス
            left_eye_indices = [159, 158, 157, 173, 133, 246, 161, 160]
            right_eye_indices = [386, 385, 384, 398, 362, 263, 466]
            
            # 画像のサイズを取得
            h, w, _ = img.shape
            

            # 左目の座標を取得
            upper_left_eyelid_coords = np.array([
                [int(face_landmarks.landmark[i].x * w), int(face_landmarks.landmark[i].y * h)]
                for i in left_eye_indices
            ])


            # 右目の座標を取得
            upper_right_eyelid_coords = np.array([
                [int(face_landmarks.landmark[i].x * w), int(face_landmarks.landmark[i].y * h)]
                for i in right_eye_indices
            ])

            # シフト値を設定
            shift_value = -8

            # 左目の座標とシフト適用
            x = upper_left_eyelid_coords[:, 0]
            y = upper_left_eyelid_coords[:, 1] + shift_value

            # 右目の座標とシフト適用
            x2 = upper_right_eyelid_coords[:, 0]
            y2 = upper_right_eyelid_coords[:, 1] + shift_value

            # x と y をソート
            sorted_indices = np.argsort(x)
            x = x[sorted_indices]
            y = y[sorted_indices]

            # x2 と y2 をソート
            sorted_indices2 = np.argsort(x2)
            x2 = x2[sorted_indices2]
            y2 = y2[sorted_indices2]

            # スプライン補間
            cs = CubicSpline(x, y)
            cs2 = CubicSpline(x2, y2)

            # 補間用の細かいx値を生成
            x_fine = np.linspace(x.min(), x.max(), 10)
            x_fine2 = np.linspace(x2.min(), x2.max(), 15)

            # 補間されたy値を計算
            y_fine = cs(x_fine)
            y_fine2 = cs2(x_fine2)

            # ポイントを整数に変換
            points_left = np.vstack((x_fine, y_fine)).astype(np.int32).T
            points_right = np.vstack((x_fine2, y_fine2)).astype(np.int32).T

            # マスクに線を描画（指定色、アルファチャンネルも設定）
            if color is None:
                color = (126, 146, 165)
            alpha = 0.2    
            cv2.polylines(img, [points_left], isClosed=False, color=color, thickness=1, lineType=cv2.LINE_AA)
            cv2.polylines(img, [points_right], isClosed=False, color=color, thickness=1, lineType=cv2.LINE_AA)
            
            blended = cv2.addWeighted(image, 1 - alpha, img, alpha, 0)

        return blended  # 処理済み画像を返す

    def result(self, blended):
        """
        処理結果の画像を表示します。
        """
        cv2.imshow('Result',  blended)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
