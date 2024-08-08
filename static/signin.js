let pwd = document.getElementById('password');
let repwd = document.getElementById('repassword');  
let form_validate = document.getElementById('form');
let show = document.getElementById('show');
form_validate.onsubmit(e);{
    if(pwd.innerHTML!=repwd.innerHTML){
        e.preventDefault();
        show.classList.toggle('show');
    }
}