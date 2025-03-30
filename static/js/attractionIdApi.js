const bookingForm = document.forms['booking-form'];
const prevBtn = document.querySelector('.carousel__previous-flipper');
const nextBtn = document.querySelector('.carousel__next-flipper');
// const carousel = document.querySelector('.carousel');
const imgContainer = document.querySelector('.carousel__container');
const dotContainer = document.querySelector('.carousel__dotlist');
const url = new URL(window.location.href);
let currentIndex = 0;

const setAttractionInfo = async (attraction) => {
    let data = attraction.data;
    // let imgContainer = document.querySelector('.carousel__container');
    // let dotContainer = document.querySelector('.carousel__dotlist');
    data.images.forEach((src, index) => {
        let img = document.createElement("img");
        img.className = "carousel__item";
        img.src = src;
        if (index === 0) {
            img.classList.add("active");
        }
        imgContainer.appendChild(img);

        let dot = document.createElement("div");
        dot.className = "dotlist__dot";
        dot.innerHTML = `
            <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <circle cx="12" cy="12" r="11" stroke="${index === 0 ? 'rgba(255, 255, 255, 0.75)' : 'none'}" stroke-width="2" fill="${index === 0 ? 'rgba(0, 0, 0, 0.75)' : 'rgba(255, 255, 255, 0.75)'}"/>
            </svg>
        `;
        dot.addEventListener("click", () => updateCarousel(index)); // 點擊 dot 切換圖片
        dotContainer.appendChild(dot);
    });
    document.querySelector('.right__title').innerText = data.name;
    document.querySelector('.right__sub-title').innerText = data.category + ' at ' + data.mrt;
    document.querySelectorAll('.article__info')[0].innerText = data.description;
    document.querySelectorAll('.article__info')[1].innerText = data.address;
    document.querySelectorAll('.article__info')[2].innerText = data.transport;
};

const updateCarousel = (index) => {
    let dotList = document.querySelectorAll('.dotlist__dot svg circle');
    currentIndex = index;

    imgContainer.style.transform = `translateX(-${currentIndex * 100}%)`;

    dotList.forEach((dot, i) => {
        dot.setAttribute("stroke", i === currentIndex ? "rgba(255, 255, 255, 0.75)" : "none");
        dot.setAttribute("fill", i === currentIndex ? "rgba(0, 0, 0, 0.75)" : "rgba(255, 255, 255, 0.75)");
    });
};

// const updateCarousel = (index) => {
//     let imgList = document.querySelectorAll('.carousel__item');
//     let dotList = document.querySelectorAll('.dotlist__dot svg circle');
//     imgList[currentIndex].classList.remove("active"); 
//     imgList[currentIndex].classList.add("fade-out");
//     dotList[currentIndex].setAttribute("stroke", "none");
//     dotList[currentIndex].setAttribute("fill", "rgba(255, 255, 255, 0.75)");
//     setTimeout(() => {
//         imgList[currentIndex].classList.remove("fade-out");
//         imgList[currentIndex].style.display = "none";
//         currentIndex = index;
//         imgList[currentIndex].style.display = "block";
//         imgList[currentIndex].classList.add("active");
//         dotList[currentIndex].setAttribute("stroke", "rgba(255, 255, 255, 0.75)");
//         dotList[currentIndex].setAttribute("fill", "rgba(0, 0, 0, 0.75)");
//     }, 200); // 時間與 CSS `transition` 一致
// };

nextBtn.addEventListener('click', () => {
    let nextIndex = (currentIndex + 1) % document.querySelectorAll('.carousel__item').length;
    updateCarousel(nextIndex);
});

prevBtn.addEventListener('click', () => {
    let prevIndex = (currentIndex - 1 + document.querySelectorAll('.carousel__item').length) % document.querySelectorAll('.carousel__item').length;
    updateCarousel(prevIndex);
});

bookingForm.addEventListener('change', () => {
    let infoPrice = document.querySelector('.info__price');
    if(bookingForm.time.value === 'morning'){
        infoPrice.textContent = '新台幣 2000 元';
    }else if (bookingForm.time.value === 'afternoon') {
        infoPrice.textContent = '新台幣 2500 元';
    }
});

window.addEventListener('DOMContentLoaded', async () => {
    let apiUrl = url.pathname.replace('/attraction/', '/api/attraction/');
    attraction = await getApiAttractions(apiUrl);
    setAttractionInfo(attraction);
});






