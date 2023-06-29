import scipy.io as sio


def create_matlabStruct(filename) -> dict:
    """
    Funcion para facilitar la lectura de structs de matlab desde python.
    Utiliza internamente las herramientas de scipy y numpy.
    Devuelve diccionario con los datos del struct.
    """

    container = sio.loadmat(filename, squeeze_me=True)

    # returns a tuple with the name of the fields the struct contains
    fields = container['data'].dtype.names
    data = [item for item in container['data'][()]]
    struct_data = {key: value for key, value in zip(fields, data)}

    # las pasadas son campos enumerados con una S (ej: S1, S2, S3, ...)
    for pasada in [field for field in fields if field[0] == 'S']:
        # get names of subfields in a tuple
        subfields = struct_data[pasada][()].dtype.names
        subdata = [item for item in struct_data[pasada][()]]
        struct_data[pasada] = {k: v for k, v in zip(subfields, subdata)}

        # separo los eventos de toe-off y heel-strike ('LTO', 'LHS', 'RTO', 'RHS')
        event_names = struct_data[pasada]['events'][()].dtype.names  # name of events in tuple
        event_data = [item for item in struct_data[pasada]['events'][()]]
        struct_data[pasada]['events'] = {k: v for k, v in zip(event_names, event_data)}
        # decrease indexes in one because in matlab enumeration starts at 1
        for event in event_names:
            struct_data[pasada]['events'][event][:, 1] -= 1

    # extraccion de los labels
    label_categories = struct_data['var_labels'][()].dtype.names
    label_data = [item for item in struct_data['var_labels'][()]]
    struct_data['var_labels'] = {k: v for k, v in zip(label_categories, label_data)}

    return struct_data


if __name__ == '__main__':
    Sujeto1 = create_matlabStruct('sujetos/AB09_mine_excluded.mat')


