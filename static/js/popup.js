const signinSignupBtn = document.querySelectorAll(".nav__list li")[1];
const signOutBtn = document.querySelectorAll(".nav__list li")[2];
const popup = document.querySelector(".popup");
const closeBtn = document.querySelector(".close-btn");

const switchToSignupBtn = document.querySelector("#switch-to-signup");
const switchToSigninBtn = document.querySelector("#switch-to-signin");

const signin = document.querySelector("#signin");
const signup = document.querySelector("#signup");
const signinForm = document.forms['signin-form'];
const signupForm = document.forms['signup-form'];
const signinMessage = document.querySelector("#signin-message");
const signupMessage = document.querySelector("#signup-message");

document.addEventListener("DOMContentLoaded", async function (e) {
    const token = localStorage.getItem("token");
    if (token) {
        let response = await fetch("/api/user/auth", {
            method: "GET",
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${localStorage.getItem("token")}`
            }
        });
        let data = await response.json();
        if (data) {
            signinSignupBtn.style.display = "none";
            signOutBtn.style.display = "list-item";
        } else {
            signinSignupBtn.style.display = "list-item";
            signOutBtn.style.display = "none";
            localStorage.removeItem("token");
        }
    }
});


signinSignupBtn.addEventListener("click", function () {
    popup.style.display = "flex";
});
closeBtn.addEventListener("click", function () {
    popup.style.display = "none";
});

switchToSignupBtn.addEventListener("click", function () {
    signin.style.display = "none";
    signup.style.display = "block";
    signinMessage.textContent = ""; 
});
switchToSigninBtn.addEventListener("click", function () {
    signup.style.display = "none";
    signin.style.display = "block";
    signupMessage.textContent = ""; 
});

signinForm.addEventListener("submit", async function (e) {
    e.preventDefault();
    const email = signinForm.email.value;
    const password = signinForm.password.value;
    let response = await fetch("/api/user/auth", {
        method: "PUT",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ email, password })
    })
    let data = await response.json();
    console.log(data);
    if (data.token) {
        console.log("登入成功");
        const token = data.token;
        localStorage.setItem("token", token);
        signinMessage.textContent = "登入成功"; 
        signinMessage.style.color = "green";
        window.location.reload();
    } else {
        console.log("登入失敗");
        signinMessage.textContent = data.message; 
        signinMessage.style.color = "red"; 
    }
});

signupForm.addEventListener("submit", async function (e) {
    e.preventDefault();
    const name = signupForm.name.value;
    const email = signupForm.email.value;
    const password = signupForm.password.value;
    let response = await fetch("/api/user", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ name, email, password })
    });
    let data = await response.json();
    if (data.ok) {
        signupMessage.textContent = "註冊成功，請登入系統"; 
        signupMessage.style.color = "green";
        window.location.reload(); 
    } else {
        signupMessage.textContent = data.message; 
        signupMessage.style.color = "red"; 
    }
});

if(signOutBtn) {
    signOutBtn.addEventListener("click", function () {
        localStorage.removeItem("token");
        signinSignupBtn.style.display = "list-item";
        signOutBtn.style.display = "none";
        window.location.reload();
    });
}          




