const isCheckboxOrRadio = type => ['checkbox', 'radio'].includes(type);

const {form} = document.forms;
const values = {};
function retrieveFormValue(event){
	event.preventDefault();

	const {elements} = form;


	for (let i=0; i<elements.length; i++){
		const formElement = elements[i];
		const {name} = formElement

		if (name){
			const {value, type, checked} = formElement;

			values[name] = isCheckboxOrRadio(type) ? checked :value;
		}
	}

	console.log('v4', values)

}
	
console.log('work')




form.addEventListener('submit', retrieveFormValue);