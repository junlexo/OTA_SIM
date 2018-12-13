def save(fileName, data):
    file = open(fileName, 'w')
    file.write(data)
    file.close()


def load(fileName):
    file = open(fileName, 'r')
    data = file.read()
    file.close()
    return data
