const todos_container = document.getElementById('todos_container')
const loginForm = document.getElementById('loginForm')
const loginButton = document.getElementById('loginButton')
const signUpButton = document.getElementById('signUpButton')
const SERVER_URL = 'http:/127.0.0.1:8000'

async function login(event){
    event.preventDefault()
    try {
        const response = await fetch(`${SERVER_URL}/login`, {
            method: 'POST',  
            body: JSON.stringify({})
        })
        if(response.ok){
            console.log('http request sent')
        }
        
    } catch(error) {
        console.error('Request failed:', error)
    }
}





loginButton.addEventListener('click', login)

function add_todo(text){
    const div = createElement('div');
    div.textContent = text;
    todos_container.appendChild(div)
}
