<<<<<<< HEAD
const isCheckboxOrRadio = type => ['checkbox', 'radio'].includes(type);

const {form} = document.forms;

function login(values){
        console.log(values);
	axios.post(window.location.origin + '/auth/jwt/login', values,{
        headers: {
            'Content-Type': 'multipart/form-data',
        },
    },)
        .then((response) => {console.log(response.data);
                localStorage.setItem("access_token", response.data.access_token);
                addElement();
                })
        .catch((error)=>{console.log(error);});
    }
//}
//}

function retrieveFormValue(event){
	event.preventDefault();
	const {elements} = form;
    const values = {}
	for (let i=0; i<elements.length; i++){
		const formElement = elements[i];
		const {name} = formElement
		if (name){
			const {value, type, checked} = formElement;
            values[name] = isCheckboxOrRadio(type) ? checked :value;
        }
    }
    login(values);
    }


const message = {}

function addElement() {
  // create a new div element
  const newDiv = document.createElement("div");

 get_resource(window.location.origin+'/authenticated-route', message)

  // and give it some content
  setTimeout(() => {
  console.log("Delayed for 1 second.");
  const newContent = document.createTextNode(message.text);

  // add the text node to the newly created div
  newDiv.appendChild(newContent);

  // add the newly created element and its content into the DOM
  const currentDiv = document.getElementById("div2");
  document.body.insertBefore(newDiv, currentDiv);
}, "1000")
//  const newContent = document.createTextNode(message.text);
//
//  // add the text node to the newly created div
//  newDiv.appendChild(newContent);
//
//  // add the newly created element and its content into the DOM
//  const currentDiv = document.getElementById("div2");
//  document.body.insertBefore(newDiv, currentDiv);
}


function get_resource(path, message){
    const TOKEN = localStorage.getItem('access_token');
    axios.get(
        path, {
=======


// 1. Registration
function registration(email, password){
    axios.post('http://localhost:8000/auth/register', {
        email: email,
        password: password,
    })
    .then((response) => console.log(response))
    .catch((error) => console.log(error));
}
// 2. Login
function login(login, password){
    const formData = new FormData();
    formData.set('username', login);
    formData.set('password', password);
    axios.post(
        'http://localhost:8000/auth/jwt/login',
        formData,
        {
            headers: {
                'Content-Type': 'multipart/form-data',
            },
        },
    )
    .then((response) => {console.log(response.data);
                         localStorage.setItem('token', response.data.access_token)})
    .catch((error) => console.log(error));
}

// loging cookie +JWT
function login_cookie(login, password){
    const formData = new FormData();
    formData.set('username', login);
    formData.set('password', password);
    axios.post(
        'http://localhost:8000/auth/cookie/login',
        formData,
        {
            headers: {
                'Content-Type': 'multipart/form-data',
            },
        },
    )
    .then((response) => console.log(response))
    .catch((error) => console.log(error));
}

//3. Get my profile
function get_my_profile(){
    const TOKEN = localStorage.getItem('token')
    axios.get(
        'http://localhost:8000/users/me', {
>>>>>>> 1dd15f8 (feat: added logging module for logging. Logging main function)
        headers: {
            'Authorization': `Bearer ${TOKEN}`,
        },
    })
<<<<<<< HEAD
    .then((response) => {console.log(response.data);
                            message.text=response.data.message
                            })
    .catch((error) => console.log(error));
}
console.log('work')


form.addEventListener('submit', retrieveFormValue);
=======
    .then((response) => console.log(response.data))
    .catch((error) => console.log(error));
    }
// 4. Update my profile
function update_my_profile(){
    const TOKEN = localStorage.getItem('token')
    axios.patch(
        'http://localhost:8000/users/me',
        {
            password: 'lancelot',
        },
        {
            headers: {
                'Authorization': `Bearer ${TOKEN}`,
            },
        },
    )
    .then((response) => console.log(response))
    .catch((error) => console.log(error));
}

// 5. Become a superuser
function become_superuser(TOKEN){
    axios.get(
        'http://localhost:8000/users/4fd3477b-eccf-4ee3-8f7d-68ad72261476', {
        headers: {
            'Authorization': `Bearer ${TOKEN}`,
        },
    })
    .then((response) => console.log(response))
    .catch((error) => console.log(error));
}
//5.1. Get the profile of any user
function get_my_profile_any_user(TOKEN){
    axios.get(
        'http://localhost:8000/users/4fd3477b-eccf-4ee3-8f7d-68ad72261476', {
        headers: {
            'Authorization': `Bearer ${TOKEN}`,
        },
    })
    .then((response) => console.log(response))
    .catch((error) => console.log(error));
}

//5.1. Update any user
function update_user(TOKEN){
    axios.patch(
        'http://localhost:8000/users/4fd3477b-eccf-4ee3-8f7d-68ad72261476',
        {
            is_superuser: true,
        },
        {
            headers: {
                'Authorization': `Bearer ${TOKEN}`,
            },
        },
    )
    .then((response) => console.log(response))
    .catch((error) => console.log(error));
}
//5.2. Delete any user
function delete_user(TOKEN){
    axios.delete(
        'http://localhost:8000/users/4fd3477b-eccf-4ee3-8f7d-68ad72261476',
        {
            headers: {
                'Authorization': `Bearer ${TOKEN}`,
            },
        },
    )
    .then((response) => console.log(response))
    .catch((error) => console.log(error));
}
//6. Logout
function logout(){
    const TOKEN = localStorage.getItem('token')
    axios.post('http://localhost:8000/auth/cookie/logout',
        null,
        {
            headers: {
                'Cookie': `fastapiusersauth=${TOKEN}`,
            },
        }
    )
    .then((response) => console.log(response))
    .catch((error) => console.log(error));
}

export = {
    login,
    registration,
    get_my_profile,
    logout,
    update_my_profile,
    become_superuser,
    get_my_profile_any_user,
    update_user
}
>>>>>>> 1dd15f8 (feat: added logging module for logging. Logging main function)
