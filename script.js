const products = [
  {id:1, name_ru:"Филадельфия", name_uz:"Filadelfiya", price:45000},
  {id:2, name_ru:"Калифорния", name_uz:"Kaliforniya", price:40000},
  {id:3, name_ru:"Дракон", name_uz:"Ajdarho", price:50000}
];

let cart = {};
let lang = "ru";

function renderMenu(){
  const menu = document.getElementById("menu");
  menu.innerHTML = "";

  products.forEach(p=>{
    const div = document.createElement("div");
    div.className="item";
    div.innerHTML = `
      <h3>${lang=="ru"?p.name_ru:p.name_uz}</h3>
      <p>${p.price} UZS</p>
      <button onclick="add(${p.id})">+</button>
      <button onclick="remove(${p.id})">-</button>
      <span>${cart[p.id]||0}</span>
    `;
    menu.appendChild(div);
  });
}

function add(id){
  cart[id]=(cart[id]||0)+1;
  renderMenu();
}

function remove(id){
  if(cart[id]) cart[id]--;
  renderMenu();
}

function checkout(){
  let text="";
  products.forEach(p=>{
    if(cart[p.id]){
      text+=`${p.name_ru} x${cart[p.id]}\n`;
    }
  });
  Telegram.WebApp.sendData(text);
}

function changeLang(){
  lang=document.getElementById("lang").value;
  renderMenu();
}

renderMenu();
