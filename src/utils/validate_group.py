def val_gr_n(group_name:str) -> tuple[bool, str]:
    if not group_name:return False, "Название не обработано. Повторите попытку"
    elif len(group_name) < 3:return False, "Название слишком короткое. Введите еще раз:"
    elif len(group_name) > 20:return False, "Слишком длинное название. Введите название группы" 
    else:return True, group_name