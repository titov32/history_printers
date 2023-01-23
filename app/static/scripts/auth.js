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
        headers: {
            'Authorization': `Bearer ${TOKEN}`,
        },
    })
    .then((response) => {console.log(response.data);
                            message.text=response.data.message
                            })
    .catch((error) => console.log(error));
}
console.log('work')


form.addEventListener('submit', retrieveFormValue);