let offset = -200;

window.addEventListener("DOMContentLoaded", () => {
    let strHtml = `\n`;
    strHtml += `\t<img src="static/image/humbergerIcon.svg" id="menuIcon" class="menuIcon"/>\n`;
    strHtml += `\t<div id="sideBar">\n`;
    strHtml += `\t\t<img src="static/image/humbergerIcon.svg" id="menuIcon2" class="menuIcon"/>\n`;
    strHtml += `\t\t<div id="menuList">\n`;
    strHtml += `\t\t\t<div id="home" class="menuItem">ホーム</div>\n`;
    strHtml += `\t\t\t<div id="reservation" class="menuItem">予約</div>\n`;
    strHtml += `\t\t\t<div id="simulate" class="menuItem">シミュレート</div>\n`;
    strHtml += `\t\t\t<div id="mypage" class="menuItem">マイページ</div>\n`;
    strHtml += `\t\t\t<a href="https://docs.google.com/forms/d/1I9mZq3OCbmeKt92phxJntnn2AkP_-rNg97GV5uBIxYE/prefill" id="business" class="menuItem">事業者</a>\n`; // Googleフォームへのリンク
    strHtml += `\t\t</div>\n`;
    strHtml += `\t</div>\n`;
    strHtml += `\t<div id="cover" class="cover"></div>\n`;
    menuSideBar.insertAdjacentHTML("beforeend", strHtml);

    // メニューアイコンのクリックイベント
    document.getElementById("menuIcon").addEventListener("click", () => {
        toggleSideBar();
    });

    document.getElementById("menuIcon2").addEventListener("click", () => {
        toggleSideBar();
    });

    // その他のクリックイベント
    document.getElementById("home").addEventListener("click", () => {
        toggleSideBar();
        setTimeout(() => {
            location.href = "/";
        }, 300);
    });

    document.getElementById("reservation").addEventListener("click", () => {
        toggleSideBar();
        setTimeout(() => {
            location.href = "/reservation";
        }, 300);
    });

    document.getElementById("simulate").addEventListener("click", () => {
        toggleSideBar();
        setTimeout(() => {
            location.href = "/simulate";
        }, 300);
    });

    document.getElementById("mypage").addEventListener("click", () => {
        toggleSideBar();
        setTimeout(() => {
            location.href = "/mypage";
        }, 300);
    });

    // サイドバーの開閉をトグルする関数
    const toggleSideBar = () => {
        document.getElementById("cover").classList.toggle("coverVisible");
        document.getElementById("sideBar").classList.toggle("open");
    };
});
