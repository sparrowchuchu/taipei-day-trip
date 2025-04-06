const loginRegisterBtn = document.querySelectorAll(".nav__list li")[1];
const popup = document.querySelector(".popup");
const closeBtn = document.querySelector(".close-btn");

const switchToRegisterBtn = document.getElementById("switch-to-register");
const switchToLoginBtn = document.getElementById("switch-to-login");

const loginForm = document.getElementById("login-form");
const registerForm = document.getElementById("register-form");

const loginErrorMessage = document.getElementById("login-error-message");
const registerErrorMessage = document.getElementById("register-error-message");

// 打開彈出對話框
loginRegisterBtn.addEventListener("click", function () {
    popup.style.display = "flex";
});

// 關閉彈出對話框
closeBtn.addEventListener("click", function () {
    popup.style.display = "none";
});

// 切換到註冊表單
switchToRegisterBtn.addEventListener("click", function () {
    loginForm.style.display = "none";
    registerForm.style.display = "block";
    loginErrorMessage.textContent = ""; // 清空錯誤信息
});

// 切換到登錄表單
switchToLoginBtn.addEventListener("click", function () {
    registerForm.style.display = "none";
    loginForm.style.display = "block";
    registerErrorMessage.textContent = ""; // 清空錯誤信息
});

// 登錄表單提交事件
document.getElementById("login-form-element").addEventListener("submit", function (e) {
    e.preventDefault();
    
    const email = document.getElementById("login-email").value;
    const password = document.getElementById("login-password").value;

    // 假設這裡是向後端發送請求來驗證用戶
    // 使用 fetch 發送 API 請求
    fetch("/api/user/auth", {
        method: "PUT",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ email, password })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            window.location.reload(); // 登入成功後刷新頁面
        } else {
            loginErrorMessage.textContent = data.message; // 顯示錯誤信息
        }
    });
});

// 註冊表單提交事件
document.getElementById("register-form-element").addEventListener("submit", function (e) {
    e.preventDefault();
    
    const username = document.getElementById("register-username").value;
    const email = document.getElementById("register-email").value;
    const password = document.getElementById("register-password").value;

    // 假設這裡是向後端發送請求來註冊用戶
    fetch("/api/user", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ username, email, password })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            window.location.reload(); // 註冊成功後刷新頁面
        } else {
            registerErrorMessage.textContent = data.message; // 顯示錯誤信息
        }
    });
});





