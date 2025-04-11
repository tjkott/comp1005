class Address():
    def __init__(self, number, street, suburb, postcode): 
        self.number = number
        self.street = street
        self.suburb = suburb
        self.postcode = postcode
        
    def __str__(self):
        return(self.number + ' ' + self.street + ', ' + self.suburb + ', ' + self.postcode)

class Person():
    def __init__(self, name, dob, address): 
        self.name = name
        self.dob = dob
        self.address = address
        
    def displayPerson(self):
        print('Name: ', self.name, '\tDOB: ', self.dob) 
        print(' Address: ', str(self.address))

class Student():
    myclass = "Student"
    def __init__(self, name, dob, address, studentID): 
        self.name = name
        self.dob = dob
        self.address = address
        self.studentID = studentID

class Postgrad(Student):
    myclass = "Postgrad"
    def __init__(self, name, dob, address, studentID): 
        super().__init__(name, dob, address, studentID)

class Undergrad(Student):
    myclass = "Undergrad"
    def __init__(self, name, dob, address, studentID): 
        super().__init__(name, dob, address, studentID)

print('#### People Test Program ###')
testAdd = Address('10', 'Downing St', 'Carlisle', '6101') 
testPerson = Person('Winston Churchill', '30/11/1874', testAdd) 
testPerson.displayPerson()


# Activity 5 - Universal People Reader
fileobj = open(r'C:\Users\theja\OneDrive\Documents\comp1005\Prac07\people.csv', 'r')
#fileobj = open('people.csv','r') 
peopleList = [line.strip().split(':')[1] for line in fileobj]
print(peopleList)
for person in peopleList:
    testAdd2 = Address(peopleList[person], peopleList[person], peopleList[person], peopleList[person])
    testPerson2 = Person(peopleList[person], ).displayPerson()
    testPerson2.displayPerson()
fileobj.close()
