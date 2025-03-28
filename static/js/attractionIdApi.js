const bookingForm = document.forms['booking-form'];
const infoPrice = document.querySelector('.info__price');

bookingForm.addEventListener('change', async () => {
    if(bookingForm.time.value === 'morning'){
        infoPrice.textContent = '新台幣 2000 元';
    }else if (bookingForm.time.value === 'afternoon') {
        infoPrice.textContent = '新台幣 2500 元';
    }
});



