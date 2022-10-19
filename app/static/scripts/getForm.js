const isCheckboxOrRadio = type => ['checkbox', 'radio'].includes(type);

const {form} = document.forms;

function update_storehouse(values){
        const cartridges = {cartridges:[]};
        for (val in values){
            if (Number.isInteger(+(val))){
                if (values[val]=='')
                    continue
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

function update_count_depart(values){
        const cartridges = {cartridges:[]};
        for (val in values){
            if (Number.isInteger(+(val))){
                if (values[val]=='')
                    continue
                else{
                cartridges.cartridges.push({'id_cartridge':parseInt(val),
                                            'amount':parseInt(values[val]),
                                            'department_id':parseInt(values.department_id)})}
                }
        }
    cartridges.operation = values.operation
    console.log('values:', values)
	console.log('v4', JSON.stringify(cartridges))
	axios.post(window.location.origin + '/API/storehouse/department', cartridges)
        .then((response) => {console.log(response.data);})
        .catch((error)=>{console.log(error);});
}
function router(values){
    if (values.operation === 'replenishment' || values.operation === 'transfer_to_service'){
        update_storehouse(values);
    }
    if (values.operation === 'transfer_to_department_with_return' ||
        values.operation === 'return_from_department' ||
        values.operation === 'replace'){
            update_count_depart(values);
    }

}

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
    router(values);
//    setTimeout(() => {
//          document.location.reload();
//        }, 3000);

}

console.log('work')


form.addEventListener('submit', retrieveFormValue);