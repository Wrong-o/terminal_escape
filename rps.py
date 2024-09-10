def get_choice():
    options = range(1, 4)
    print(list(options))
    
    for i in options:
        print(i)
    
    try:
        choice = int(input("1 = rock, 2 = paper, 3 = scissors: "))
        if choice in options:
            return choice
        else:
            print("wrong")
    except ValueError:
        print("wrong")

get_choice()