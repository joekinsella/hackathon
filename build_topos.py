"""
THIS IS ALL OUTDATED AN NOW USELESS, WILL PROBABLY DELETE SOON
def build_linear(length: int) -> dict:
    my_dict = {}
    for i in range(length):
        my_dict[i] = []
        if i > 0:
            my_dict[i].append(i - 1)
        if i < length - 1:
            my_dict[i].append(i + 1)
    return my_dict


def build_complete(length: int) -> dict:
    my_dict = {}
    for i in range(length):
        my_dict[i] = []
        for j in range(length):
            if i != j:
                my_dict[i].append(j)
    return my_dict


def create_star(length: int) -> dict:
    my_dict = {}
    for i in range(length):
        my_dict[i] = []
        if i == 0:
            for j in range(1, length):
                my_dict[i].append(j)
        else:
            my_dict[i].append(0)
    return my_dict
"""