document.addEventListener('DOMContentLoaded', () => {
    const buttons = document.querySelectorAll('.button-tag');
    const container = document.getElementById('procedure-container');

    const defaultProcedure = 'futemaibotsu';
    displayProcedure(defaultProcedure);

    const defaultButton = document.querySelector(`.button-tag[data-procedure="${defaultProcedure}"]`);
    if (defaultButton) {
        defaultButton.classList.add('active');
    }

    // ボタンがクリックされたときの処理
    buttons.forEach(button => {
        button.addEventListener('click', () => {
            buttons.forEach(btn => btn.classList.remove('active'));
            button.classList.add('active');
            const procedure = button.getAttribute('data-procedure');
            displayProcedure(procedure);
        });
    });


    // 施術内容を表示する関数
    function displayProcedure(procedure) {
        let content = '';

        if (procedure === 'futemaibotsu') {
            content = `
                <div class="white-box">
                <div class="names">
                <h2 class="name">二重埋没</h2>
                <p class="sabname">ふたえまいぼつ</p>
                </div>
                <img src="/static/image/2ba0ea3106656216a12b1f1689bbb0c9.jpg" alt="画像1の説明" class="image-item">
                <img src="/static/image/スクリーンショット 2024-11-28 11.31.03.png" alt="画像2の説明" class="image-item">
                    <div class="tags-item">
                        <p class="tags-item1">人気No.1</p>
                        <p class="tags-item2">糸・埋没</p>
                        <p class="tags-item3">平均価格</p>
                        <p class="tags-item4">13.8万円</p>
                        <p class="tags-item5">ダウンタイム</p>
                        <p class="tags-item6">3〜7日</p>
                    </div>
                    <p class="asterisk">※平均価格は掲載中のメニューの合計から集計</p>
                        <button class="reservation">解説・口コミ・メニューを見る</button>
                </div>
            `;
        }else if (procedure === 'shizenYuchaku') {
            content = `
                <!-- 自然癒着法のHTMLコンテンツ -->
            `;
        }
        

        // 他の施術内容も同様に追加
        // if (procedure === 'shizenYuchaku') { ... }

        // container に HTML を設定
        container.innerHTML = content;

        const reservationButton = container.querySelector('.reservation');
    reservationButton.addEventListener('click', () => {
        window.location.href = detailsPageURL;
        });
        }
        });
