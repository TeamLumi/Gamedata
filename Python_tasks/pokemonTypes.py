from load_files import load_data

def get_types(e):
    if e['type1'] == e['type2']:
        return [get_type_name(e['type1'])]
    else:
        return [get_type_name(e['type1']), get_type_name(e['type2'])]

def get_type_name(typeId):
    type_namedata = full_data['type_namedata']
    return type_namedata["labelDataArray"][typeId]["wordDataArray"][0]["str"]

def get_type_id(type_name):
    type_namedata = full_data['type_namedata']

    for type_id, type_data in enumerate(type_namedata["labelDataArray"]):
        word_data_array = type_data["wordDataArray"]
        for word_data in word_data_array:
            if type_name in word_data.get("str", "").lower():
                return type_id

    print(f"{type_name} not found")
    # Return None or handle the case where the type name is not found
    return None

if __name__ != "__main__":
  full_data = load_data()