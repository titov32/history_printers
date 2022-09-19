const isCheckboxOrRadio = type => ['checkbox', 'radio'].includes(type);

const {form} = document.forms;

function retrieveFormValue(event){
    const cartridges = {cartridges:[]};
	event.preventDefault();

	const {elements} = form;

    const values = {}
	for (let i=0; i<elements.length; i++){
		const formElement = elements[i];
		const {name} = formElement

		if (name){
			const {value, type, checked} = formElement;

            values[name] = isCheckboxOrRadio(type) ? checked :value;

    }}
    for (val in values){
    if (Number.isInteger(+(val))){
        if (values[val]=='') continue
        else{
        if (values.operation === 'replenishment'){
            values.unused = 'True'
        }
        else if (values.operation === 'transfer_to_service'){
            values.unused = 'False'
              }
        cartridges.cartridges.push({'id_cartridge':parseInt(val),
                                    'amount':parseInt(values[val]),
                                    'unused':values.unused})}
        }
    }
    cartridges.operation = values.operation
    console.log('values:', values)
	console.log('v4', JSON.stringify(cartridges))
	axios.post(window.location.origin + '/API/storehouse/replenishment', cartridges)
        .then((response) => {console.log(response.data);})
        .catch((error)=>{console.log(error);});

}



console.log('work')




form.addEventListener('submit', retrieveFormValue);