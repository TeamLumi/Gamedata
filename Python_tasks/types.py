from load_files import load_data

def get_types(e):
    if e['type1'] == e['type2']:
        return [get_type_name(e['type1'])]
    else:
        return [get_type_name(e['type1']), get_type_name(e['type2'])]

def get_type_name(typeId):
    type_namedata = full_data['type_namedata']
    return type_namedata["labelDataArray"][typeId]["wordDataArray"][0]["str"]

if __name__ != "__main__":
  full_data = load_data()