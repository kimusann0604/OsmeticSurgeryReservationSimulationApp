from flask import Flask,render_template,redirect
from flask import Flask, request
import cv2
import numpy as np
import os
from io import BytesIO
from PIL import Image
import base64
from FaceLandmarkProcessor import *
from PtosisCorrection import *

app = Flask(__name__)

@app.route('/', methods=['GET','POST'])
def hello():
    return render_template('home.html')

@app.route('/business')
def business():
    google_form_url = "https://docs.google.com/forms/d/1I9mZq3OCbmeKt92phxJntnn2AkP_-rNg97GV5uBIxYE/prefill"
    return render_template('business.html', google_form_url=google_form_url)

@app.route('/reservation', methods=['GET'])
def reservation():
    return render_template('index2.html')

@app.route('/search')
def search():
    query = request.args.get('query').strip()  # 入力された検索クエリを取得
    
    # 条件に基づいてページ遷移
    if query == "二重":
        return redirect('/double-eyelid-surgery')# 二重整形のページにリダイレクト
    else:
        return "該当するページが見つかりません", 404

@app.route('/double-eyelid-surgery')
def double_eyelid_surgery():
    return render_template('double_eyelid_surgery.html')


@app.route('/simulate')
def simulate():
    return render_template('index.html')

@app.route('/process-image', methods=['GET', 'POST'])
#/process-imageにアクセスし、ボタンを押すことでPOSTを実行。その後画像処理

def process_image():
    if request.method == 'GET':
        return render_template('results.html')
    
    elif request.method == 'POST':
        try:
            if 'example' not in request.files:
                return render_template('results.html', img_data=None, result="ファイルがアップロードされていない")
                
            file = request.files['example']
            if file.filename == '':
                return render_template('results.html', img_data=None, result="ファイルが選択されていない")

            # ファイルをバイナリデータに変換
            image_bytes = file.read()
            
            # AWS認証情報の確認
            aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
            aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')
            if not aws_access_key_id or not aws_secret_access_key:
                return render_template('results.html', img_data=None, result="AWS認証情報が設定されていません")

            # Rekognitionによる顔認識
            face_processor = FaceLandmarkProcessor(
                aws_access_key_id=aws_access_key_id,
                aws_secret_access_key=aws_secret_access_key
            )
            response = face_processor.detect_faces_landmark(image_bytes)
            
            # PILで画像を読み込み、OpenCV形式に変換
            image = Image.open(BytesIO(image_bytes))
            image_np = np.array(image)
            image_np = cv2.cvtColor(image_np, cv2.COLOR_RGB2BGR)

            if 'FaceDetails' in response and len(response['FaceDetails']) > 0:
                height, width = image_np.shape[:2]
                face_processor.draw_landmarks(image_np, response['FaceDetails'], height, width)

                # 処理済み画像をbase64にエンコードして埋め込み表示
                _, buffer = cv2.imencode('.png', image_np)
                img_base64 = base64.b64encode(buffer).decode('utf-8')
                img_data_uri = f"data:image/png;base64,{img_base64}"

                return render_template('results.html', img_data=img_data_uri, result="顔認識処理が完了しました")
        
        except Exception as e:
            return render_template('results.html', img_data=None, result=f"エラーが発生しました: {str(e)}")
        
@app.route('/eye-process', methods=['GET', 'POST'])
#/eye-processにアクセスし、画像をアップロードすることでPOSTを実行その後顔認証
def process():
    if request.method == 'GET':
        return render_template('results2.html',
                             img_data=None,
                             result="ファイルをアップロードしてください")
    
    try:
        if 'example' not in request.files:
            return render_template('results2.html',
                                 img_data=None,
                                 result="ファイルがアップロードされていません")
        # print(request.files)
        #出力：ImmutableMultiDict([('example', <FileStorage: 'image.jpg' ('image/jpeg')>)])
        # request.filesの中に画像のデータが入っている
        file = request.files['example']
        print(file)
        # 出力：<FileStorage: 'bbc6c9066fa41d8de797b46e34d91a39.jpg' ('image/jpeg')>
        if file.filename == '':
            # もしファイルの中にファイルが選択されていなかったら
            return render_template('results2.html',
                                 img_data=None,
                                 result="ファイルが選択されていません")
        
        # ファイルをバイナリデータとして読み込み
        image_bytes = file.read()
        
        # AWS認証情報の取得
        aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
        aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')
        
        if not aws_access_key_id or not aws_secret_access_key:
            return render_template('results2.html',
                                 img_data=None,
                                 result="AWS認証情報が設定されていません")
        
        # 画像処理の実行
        processor = PtosisCorrection(
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key
        )
        
        processed_image = processor.process_image(image_bytes)
        
        # 画像をbase64エンコードし、HTMLに読み込む
        _, buffer = cv2.imencode('.png', processed_image)
        img_base64 = base64.b64encode(buffer).decode('utf-8')
        img_data_uri = f"data:image/png;base64,{img_base64}"
        
        return render_template('results2.html',
                             img_data=img_data_uri,
                             result="画像処理が完了しました")
    
    except Exception as e:
        return render_template('results2.html',
                             img_data=None,
                             result=f"エラーが発生しました: {str(e)}")


@app.route('/details_page')
def details_page():
    return render_template('details_page.html')

if __name__ == "__main__":
    app.run(debug=False, port=5004)