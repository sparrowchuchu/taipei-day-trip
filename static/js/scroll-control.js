const itemList = document.querySelector('.list-bar__items');
const leftBtn = document.querySelector('.list-bar__left-btn');
const rightBtn = document.querySelector('.list-bar__right-btn');

// 左按鈕 - 往左滾動
leftBtn.addEventListener('click', () => {
  itemList.scrollBy({ left: -200, behavior: 'smooth' });
});

// 右按鈕 - 往右滾動
rightBtn.addEventListener('click', () => {
  itemList.scrollBy({ left: 200, behavior: 'smooth' });
});