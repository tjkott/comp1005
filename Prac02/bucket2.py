#
# bucket2.py - bucket list builder
#
print('\nBUCKET LIST BUILDER\n')
bucket = []
choice = input('Enter selection: e(X)it, (A)dd, (L)ist, (D)elete...')
while choice.upper()[0] != 'X':
    if choice.upper()[0] == 'A':
        print('Enter list item... ')
        newitem = input()
        bucket.append(newitem)
    elif choice.upper()[0] == 'L':
        for item in bucket:
            print(item)
    elif choice.upper()[0] == 'D':
        print('Enter list item to be deleted...')
        delitem = input()
        if delitem in bucket:
            bucket.remove(delitem)
        else:
            print('Item not found.')
    else:
        print('Invalid selection.')
    choice = input('Enter selection: e(X)it, (A)dd, (L)ist..')
print('\nGOODBYE!\n')  