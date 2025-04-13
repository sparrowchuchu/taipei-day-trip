const deleteBtn = document.querySelector(".info__del-icon");

const renderBooking = (data) => {
    console.log(data);
    if(data.attraction === null) {
        console.log("沒有預訂資料");
        const user = data.user;
        let bookingContainer = document.querySelector(".booking__container")
        let newContainer = document.createElement("div");
        let newLastContainer = document.createElement("div");
        let titleDiv = document.createElement("div");
        let infoDiv = document.createElement("div");
        newContainer.className = "booking__item";
        // newContainer.style.marginRight = "110px";
        titleDiv.className = "booking__title";
        titleDiv.textContent = `您好，${user}，待預定的行程如下`;  
        infoDiv.textContent = "目前沒有任何待預訂的行程";
        
        while (bookingContainer.firstChild) {
            console.log(bookingContainer.firstChild);
            bookingContainer.removeChild(bookingContainer.firstChild);
        }
        newContainer.appendChild(titleDiv);
        newContainer.appendChild(infoDiv);
        bookingContainer.appendChild(newContainer);
        bookingContainer.appendChild(newLastContainer);
    } else {
        const {
            user, 
            attraction,
            date,
            time,
            price
        } = data;

        const timeText = time === "morning" ? "早上9點到下午2點" : "下午2點到晚上7點";
        document.querySelector(".booking__title").textContent = `您好，${user}，待預定的行程如下`;
        document.querySelector(".attraction__img").src = attraction.image;
        document.querySelector(".info__title").textContent = `台北一日遊：${attraction.name}`;
        document.querySelectorAll(".info__data")[0].textContent = date;
        document.querySelectorAll(".info__data")[1].textContent = timeText;
        document.querySelectorAll(".info__data")[2].textContent = price;
        document.querySelectorAll(".info__data")[3].textContent = attraction.address;
        document.querySelectorAll(".info__subtitle")[5].querySelector("span").textContent = `總價：新台幣 ${price} 元`;
    }
}
const deleteBooking = async() => {
    try {
        const response = await fetch("/api/booking", {
        method: "DELETE",
        headers: {
            "Authorization": `Bearer ${token}`
        }
        });

        const result = await response.json();
        if (result.ok) {
        location.reload(); // 成功刪除後重新載入頁面
        }
    } catch (error) {
        console.error("Error deleting booking:", error);
    }
}

deleteBtn.addEventListener("click", () => {
    const confirmDelete = confirm("確定要刪除這筆預訂嗎？");
    if (confirmDelete) {
        deleteBooking();
    }
});

document.addEventListener("DOMContentLoaded", async() => {
    if (!token) {
        window.location.href = "/";
    }
    try {
        const response = await fetch("/api/booking", {
        method: "GET",
        headers: {
            "Authorization": `Bearer ${token}`
        }
        });
        const result = await response.json();
        console.log(result);
        renderBooking(result.data);
    } catch (error) {
        console.error("Error fetching booking data:", error);
    }
});



  


