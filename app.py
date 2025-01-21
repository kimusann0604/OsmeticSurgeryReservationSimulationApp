from flask import Flask, render_template, redirect, session, url_for, jsonify, request
import cv2
import numpy as np
import os
from io import BytesIO
from PIL import Image
import base64
from FaceLandmarkProcessor import EyeLandmarkProcessor
from PtosisCorrection import PtosisCorrection
from functools import wraps
import boto3
from datetime import datetime
from flask_cors import CORS
from flask_socketio import SocketIO, emit
from boto3.dynamodb.conditions import Key
import requests
from flask_session import Session
import dlib
from imutils import face_utils






app = Flask(__name__)
app.config['SECRET_KEY'] = 'aP5k8Jc3Lz9Qx7Vb6Nf4Gd2Sh1Xc0Zr' 
CORS(app)

socketio = SocketIO(app)
app.config['SESSION_TYPE'] = 'filesystem'  # ファイルにセッションを保存
app.config['SESSION_PERMANENT'] = False
Session(app)


def adjust_brightness(original_color, factor):
    r, g, b = original_color
    r = max(0, int(r * factor))
    g = max(0, int(g * factor))
    b = max(0, int(b * factor))
    return (r, g, b)

# 顔検出と鼻のRGB値を計算する関数
def face_rbg(image):
    detector = dlib.get_frontal_face_detector()
    predictor = dlib.shape_predictor('/Users/kimurahotaka/Documents/profile/a/register/shape_predictor_68_face_landmarks.dat 3')

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    faces = detector(gray)
    if len(faces) == 0:
        print("顔が検出されませんでした。")
        return None

    for face in faces:
        shape = predictor(gray, face)
        shape = face_utils.shape_to_np(shape)

        # 鼻の領域の座標を計算
        nose_points = shape[[28, 29, 30, 31, 32, 33, 34, 35, 36]]
        x_coords = nose_points[:, 0]
        y_coords = nose_points[:, 1]
        x_min = max(0, np.min(x_coords) - 5)
        y_min = max(0, np.min(y_coords) - 5)
        x_max = min(image.shape[1], np.max(x_coords) + 5)
        y_max = min(image.shape[0], np.max(y_coords) + 5)

        nose_roi = image[y_min:y_max, x_min:x_max]

        if nose_roi.size > 0:
            average_b = np.mean(nose_roi[:, :, 0])
            average_g = np.mean(nose_roi[:, :, 1])
            average_r = np.mean(nose_roi[:, :, 2])
            return (int(average_r), int(average_g), int(average_b))

    print("鼻の領域が抽出されませんでした。")
    return None


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # セッションに 'usr' が設定されていなければログインしていない
        if 'usr' not in session or not session['usr']:
            # ログインページにリダイレクトし、nextパラメータで元のURLを渡す
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function


@app.route('/', methods=['GET', 'POST'])
def hello():
    usr = session.get('usr')
    print(f"usrの値: {usr}")  # usrの内容をログに出力
    return render_template('home.html', usr=usr)

@app.route('/business')
def business():
    google_form_url = "https://docs.google.com/forms/d/1I9mZq3OCbmeKt92phxJntnn2AkP_-rNg97GV5uBIxYE/prefill"
    return render_template('business.html', google_form_url=google_form_url)



@app.route('/reservation', methods=['POST'])
def reservation():
    dynamodb = boto3.resource('dynamodb', region_name='ap-northeast-1')  # リージョンを適切に設定
    table = dynamodb.Table('reservations')  
    
    clinic_name = request.form.get('clinic_name')
    print(f"受け取ったクリニック名: {clinic_name}")
    if clinic_name:
        reservation_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        table.put_item(
            Item={
                'clinic_name': clinic_name,
                'reservation_date': reservation_date,
                'status': 'カウンセリング'
            }
        )
    else:
        print("クリニック名が送信されていません")
        
        print(f"DynamoDBに保存されました: {clinic_name} ({reservation_date})")
    return redirect(url_for('show_reservations'))
    

@app.route('/reservations')
@login_required
def show_reservations():
    dynamodb = boto3.resource('dynamodb', region_name='ap-northeast-1')  # リージョンを適切に設定
    table = dynamodb.Table('reservations') 
    response = table.scan()
    reservations = response['Items']
    return render_template('index2.html', reservations=reservations)

@app.route('/details_page2')
def details_page2():
    dynamodb = boto3.resource('dynamodb', region_name='ap-northeast-1')  # リージョンを適切に設定
    table = dynamodb.Table('reservations') 
    response = table.scan()
    reserve = response['Items']
    return render_template('details_page2.html', reserve=reserve)

@app.route('/search')
def search():
    query = request.args.get('query', '').strip()
    if query == "二重":
        return redirect('/double-eyelid-surgery')
    else:
        return "該当するページが見つかりません", 404

@app.route('/double-eyelid-surgery')
def double_eyelid_surgery():
    return render_template('double_eyelid_surgery.html')

@app.route('/simulate')
def simulate():
    return render_template('index.html')

@app.route('/process-image', methods=['GET', 'POST'])
def process_image():
    if request.method == 'GET':
        return render_template('results.html', img_data=None, original_img=None, result=None)

    elif request.method == 'POST':
        try:
            if 'example' not in request.files:
                return render_template('results.html', img_data=None, original_img=None, result="ファイルがアップロードされていません")

            file = request.files['example']
            if file.filename == '':
                return render_template('results.html', img_data=None, original_img=None, result="ファイルが選択されていません")

            # 元画像の保存パス
            original_path = '/tmp/original_image.jpg'
            file.save(original_path)

            # 元画像をテンプレートに渡すためにBase64エンコード
            with open(original_path, "rb") as img_file:
                original_base64 = base64.b64encode(img_file.read()).decode('utf-8')
            original_img_uri = f"data:image/jpeg;base64,{original_base64}"

            # OpenCVで画像を読み込む
            image = cv2.imread(original_path)
            if image is None:
                return render_template('results.html', img_data=None, original_img=original_img_uri, result="画像が見つかりません。")

            # 鼻のRGB色を取得
            original_color = face_rbg(image)
            if original_color is None:
                return render_template('results.html', img_data=None, original_img=original_img_uri, result="鼻の領域の色が計算できませんでした。")

            # 明るさを調整
            processor = EyeLandmarkProcessor()
            face_mesh = processor.initialize_face_mesh()
            img_rgb = processor.image_path(original_path)
            factor = 0.2
            darker_color = adjust_brightness(original_color, factor)

            # ランドマークを処理し、結果画像を生成
            blended_img = processor.process_landmarks_and_create_mask(
                face_mesh, img_rgb, image.copy(), image, color=darker_color
            )

            if blended_img is not None:
                _, buffer = cv2.imencode('.png', blended_img)
                img_base64 = base64.b64encode(buffer).decode('utf-8')
                img_data_uri = f"data:image/png;base64,{img_base64}"
                return render_template('results.html', img_data=img_data_uri, original_img=original_img_uri)
            else:
                return render_template('results.html', img_data=None, original_img=original_img_uri, result="処理結果がありません。")
        except Exception as e:
            return render_template('results.html', img_data=None, original_img=None, result=f"エラーが発生しました: {str(e)}")


@app.route('/eye-process', methods=['GET', 'POST'])
def process():
    if request.method == 'GET':
        return render_template('results2.html', img_data=None, original_img=None, result="ファイルをアップロードしてください")
    
    try:
        if 'example' not in request.files:
            return render_template('results2.html', img_data=None, original_img=None, result="ファイルがアップロードされていません")

        file = request.files['example']
        if file.filename == '':
            return render_template('results2.html', img_data=None, original_img=None, result="ファイルが選択されていません")
        
        # 元画像のBase64エンコード
        image_bytes = file.read()
        original_img_base64 = base64.b64encode(image_bytes).decode('utf-8')
        original_img_uri = f"data:image/jpeg;base64,{original_img_base64}"
        
        # AWS認証情報の取得
        aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
        aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')
        
        if not aws_access_key_id or not aws_secret_access_key:
            return render_template('results2.html', img_data=None, original_img=original_img_uri, result="AWS認証情報が設定されていません")
        
        # 画像処理
        processor = PtosisCorrection(
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key
        )
        
        processed_image = processor.process_image(image_bytes)
        
        # 加工画像のBase64エンコード
        _, buffer = cv2.imencode('.png', processed_image)
        img_base64 = base64.b64encode(buffer).decode('utf-8')
        img_data_uri = f"data:image/png;base64,{img_base64}"
        
        return render_template('results2.html', img_data=img_data_uri, original_img=original_img_uri, result="画像処理が完了しました")
    
    except Exception as e:
        return render_template('results2.html', img_data=None, original_img=None, result=f"エラーが発生しました: {str(e)}")


  # DynamoDBのテーブル名

@app.route('/details_page')
def details_page():
    dynamodb = boto3.resource('dynamodb', region_name='ap-northeast-1')  # リージョンを適切に設定
    table = dynamodb.Table('clinics')
    
    try:
        # DynamoDBからデータを取得
        response = table.scan()
        items = response['Items']
        print(items)# テーブル内のデータを取得
    except Exception as e:
        print(f"Error: {e}")
        items = []

    # HTMLにデータを渡してレンダリング
    return render_template('details_page.html', data=items)

@app.route('/login')
def login():
    # CognitoのHosted UIへ直接リダイレクト
    cognito_login_url = (
        "https://ap-northeast-1upcr6stpu.auth.ap-northeast-1.amazoncognito.com/login?"
        "client_id=7kupl40v4q23san92br093bfro&"
        "response_type=code&"
        "scope=email+openid&"
        "redirect_uri=http://localhost:5004/callback"
    )
    return redirect(cognito_login_url)

@app.route('/callback')
def callback():
    code = request.args.get('code')
    if not code:
        return "認証コードが見つかりません。", 400

    # トークン取得用のリクエスト
    token_url = "https://ap-northeast-1upcr6stpu.auth.ap-northeast-1.amazoncognito.com/oauth2/token"
    response = requests.post(
        token_url,
        data={
            "grant_type": "authorization_code",
            "client_id": "7kupl40v4q23san92br093bfro",
            "client_secret": "g8tbit685i1phrs65vurstmtu0udsgmndptm1dr0obueum4pjek",
            "code": code,
            "redirect_uri": "http://localhost:5004/callback"
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )

    if response.status_code == 200:
        tokens = response.json()
        session['access_token'] = tokens['access_token']
        session['id_token'] = tokens['id_token']
        session['refresh_token'] = tokens['refresh_token']

        # ユーザー情報取得
        user_info_url = "https://ap-northeast-1upcr6stpu.auth.ap-northeast-1.amazoncognito.com/oauth2/userInfo"
        user_info_response = requests.get(
            user_info_url,
            headers={"Authorization": f"Bearer {tokens['access_token']}"}
        )

        if user_info_response.status_code == 200:
            user_info = user_info_response.json()
            session['usr'] = user_info.get('email', 'Unknown User')
        else:
            session['usr'] = "Unknown User"

        # ログイン後に元のページに戻る処理
        next_url = request.args.get('next')
        return redirect(next_url or url_for('hello'))

    else:
        return f"トークン取得エラー: {response.text}", 400

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('hello'))



    
@app.route('/chat-history/<chat_room_id>', methods=['GET'])
def chat_history(chat_room_id):
    dynamodb = boto3.resource('dynamodb', region_name='ap-northeast-1')
    table = dynamodb.Table('chat_messages')

    # DynamoDBからチャット履歴を取得
    response = table.query(
        KeyConditionExpression=Key('chat_room_id').eq(chat_room_id)
    )
    messages = response.get('Items', [])
    messages.sort(key=lambda x: x['timestamp'])  # タイムスタンプ順にソート
    return jsonify(messages)

# メッセージの送信
@socketio.on('message')
def handle_message(data):
    dynamodb = boto3.resource('dynamodb', region_name='ap-northeast-1')
    table = dynamodb.Table('chat_messages')

    # データの取得
    chat_room_id = data.get('chat_room_id', 'default_room')
    message = data.get('message', '')

    # DynamoDBにメッセージを保存
    table.put_item(Item={
        'chat_room_id': chat_room_id,
        'timestamp': datetime.now().isoformat(),
        'message': message
    })

    # メッセージを送信
    emit('message', {'chat_room_id': chat_room_id, 'message': message}, broadcast=True, include_self=False)

@app.route('/chat', methods=['GET'])
def index():
    return render_template('chat.html')




if __name__ == "__main__":
    app.run(debug=True, port=5004)
