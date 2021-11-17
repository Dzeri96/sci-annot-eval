def delete_multiple_elements(list_object, indices):
    indices = sorted(indices, reverse=True)
    for idx in indices:
        list_object.pop(idx)