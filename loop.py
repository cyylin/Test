count=0

while True:
    str=input("Enter quit: ")
    if str == "quit":
        break
    count=count+1
    if count%3>0:
        continue
    print("Please input quit!")

print("Quit loop successfully!")