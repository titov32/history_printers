from ..schemas import UpdateDepartmentCartridge, UpdateStoreHouseBase, StoreHouseBase, CounterCartridgeBase


def convert_from_depart_to_store(schema: UpdateDepartmentCartridge,
                                 unused: bool,
                                 operation: str) -> UpdateStoreHouseBase:
    if operation == '+':
        list_for_new_schema = [StoreHouseBase(id_cartridge=i.id_cartridge,
                                              amount=i.amount,
                                              unused=unused) for i in schema.cartridges]
        return UpdateStoreHouseBase(operation=schema.operation,
                                    cartridges=list_for_new_schema)
    elif operation == '-':
        list_for_new_schema = [StoreHouseBase(id_cartridge=i.id_cartridge,
                                              amount=-i.amount,
                                              unused=unused) for i in schema.cartridges]
        return UpdateStoreHouseBase(operation=schema.operation,
                                    cartridges=list_for_new_schema)
    else:
        raise ValueError('Не верно указано операция')


def convert_from_store_to_depart(schema: UpdateStoreHouseBase,
                                 department_id: int,
                                 operation: str) -> UpdateDepartmentCartridge:
    if operation == '+':
        list_for_new_schema = [CounterCartridgeBase(id_cartridge=i.id_cartridge,
                                                    amount=i.amount,
                                                    department_id=department_id) for i in schema.cartridges]
        return UpdateDepartmentCartridge(operation=schema.operation,
                                         cartridges=list_for_new_schema)
    elif operation == '-':
        list_for_new_schema = [CounterCartridgeBase(id_cartridge=i.id_cartridge,
                                                    amount=-i.amount,
                                                    department_id=department_id) for i in schema.cartridges]
        return UpdateDepartmentCartridge(operation=schema.operation,
                                         cartridges=list_for_new_schema)
    else:
        raise ValueError('Не верно указано операция')
