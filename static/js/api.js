const itemList = document.querySelector('.list-bar__items');
const leftBtn = document.querySelector('.list-bar__left-btn');
const rightBtn = document.querySelector('.list-bar__right-btn');
const attractionGrid = document.querySelector('.attraction-grid');
const loadTrigger = document.querySelector('.load-trigger');
const searchInput = document.querySelector('.search-bar__input');
const searchBtn = document.querySelector('.search-bar__button');
let keyword = '';
let nextPage = 0;
let isLoading = false;

const getApiMrts = async () =>{
  try{
      let src = "./api/mrts";
      let response = await fetch(src);  // 回傳promise
      let results = await response.json(); 
      return results;
  }catch(err){
      console.log("error: ", err);
  }
}

const getApiAttractions = async (apiUrl) =>{
  try{
      let response = await fetch(apiUrl);  // 回傳promise
      let results = await response.json(); 
      return results;
  }catch(err){
      console.log("error: ", err);
  }
}

const setListItem = (data) => {
  data['data'].forEach((mrt) => {
    let newDiv = document.createElement('div');
    newDiv.className = 'list-bar__mrt';
    newDiv.innerText = mrt;
    itemList.appendChild(newDiv);
  });
};
  
const setAttractionItem = (data) => {
  if (data['error']){
    let newDiv = document.createElement('div');
    newDiv.innerText = data['message'];
    attractionGrid.appendChild(newDiv);
  }
  nextPage = data['nextPage'];
  data['data'].forEach((attraction) => {
    let newDivCard = document.createElement('div');
    let newA = document.createElement('a');
    let attractionId = attraction['id'];
    let newDivImg = document.createElement('div');
    let newImg = document.createElement('img');
    let newDivTitle = document.createElement('div');
    let newDivContent = document.createElement('div');
    let newDivMrt = document.createElement('div');
    let newDivCategory = document.createElement('div');
    newDivCard.className = 'attraction-card';
    newA.href = `./attraction/${attractionId}`; 
    newDivImg.className = 'attraction-card__image';
    newImg.src = attraction['images'][0];
    newDivTitle.className = 'attraction-card__title';
    newDivTitle.innerText = attraction['name'];
    newDivContent.className = 'attraction-card__content';
    newDivMrt.className = 'attraction-card__mrt';
    newDivMrt.innerText = attraction['mrt'];
    newDivCategory.className = 'attraction-card__category';
    newDivCategory.innerText = attraction['category'];
    attractionGrid.appendChild(newDivCard);
    newDivCard.appendChild(newA);
    newA.appendChild(newDivImg);
    newDivImg.appendChild(newImg);
    newDivImg.appendChild(newDivTitle);
    newDivCard.appendChild(newDivContent);
    newDivContent.appendChild(newDivMrt);
    newDivContent.appendChild(newDivCategory);
  });
}

const observer = new IntersectionObserver(async (entries) => {
  // console.log(entries);
  if (entries[0].isIntersecting && !isLoading) {
    if (nextPage === null) {
      observer.disconnect();  // 若無更多資料，自動停止監聽
      return;
    }
    isLoading = true;  // 開始請求，避免重複觸發
    let apiUrl = '';
    keyword = searchInput.value.trim(); 
    if (keyword){
      apiUrl = `./api/attractions?page=${nextPage}&keyword=${keyword}`;
    }else{
      apiUrl = `./api/attractions?page=${nextPage}`;
    }
    let attractions = await getApiAttractions(apiUrl);
    setAttractionItem(attractions);
    isLoading = false;  // 請求結束
  }
});

const searchKeyword = async () =>{
  keyword = searchInput.value.trim(); 
  nextPage = 0;
  let apiUrl = `./api/attractions?page=${nextPage}&keyword=${keyword}`;
  let attractions = await getApiAttractions(apiUrl);
  while (attractionGrid.firstChild) {
    attractionGrid.removeChild(attractionGrid.firstChild);
  }
  setAttractionItem(attractions);
  observer.observe(loadTrigger);
}

if (window.location.pathname === '/') {
  window.addEventListener('DOMContentLoaded', async () => {
    let mrtsData = await getApiMrts();
    let apiUrl = `./api/attractions?page=${nextPage}`;
    let attractions = await getApiAttractions(apiUrl);
    setListItem(mrtsData);
    setAttractionItem(attractions);
    observer.observe(loadTrigger);
  });
  
  itemList.addEventListener('click', (event) =>{
    if(event.target.className === 'list-bar__mrt'){
      let keyword = event.target.innerText;
      searchInput.value = keyword;
      searchKeyword();
    }
  });
  
  leftBtn.addEventListener('click', () => {
    itemList.scrollBy({ left: -200, behavior: 'smooth' });
  });
  
  rightBtn.addEventListener('click', () => {
    itemList.scrollBy({ left: 200, behavior: 'smooth' });
  });
}

if(searchBtn && searchInput){
  searchBtn.addEventListener('click', searchKeyword);
  searchInput.addEventListener('keydown', function(event){
    if(event.key === "Enter"){
      searchKeyword();
    }
  });
}

