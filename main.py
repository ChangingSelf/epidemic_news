import json

def main():
    pass
    with open('test.json') as f:
        data = json.load(f)
        #print(data)
        for k in data:
            print(k)





if __name__ == '__main__':
    main()
    