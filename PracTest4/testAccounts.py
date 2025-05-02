'''
  Practical Test 4

  testAccounts.py - program to test functions of accounts.py
  
  Student Name   : Thejana Kottawatta Hewage
  Student Number : 22307822
  Date/prac time : 
'''
from accounts import BankAccount, Portfolio

print('\n<--- Bank Accounts Portfolio --->\n')
myAccounts = Portfolio()
# 1. Create "Castle" account
myAccounts.addAccount("Castle", "999999-1", 1000)
# 2. Create Shrubbery account. 
myAccounts.addAccount("Shrubbery", "999999-2", 100)
# 4. Deposit $100 into the Castle account. 
myAccounts.deposit("Castle", 100)
# 5. Withdraw $10 from the Shrubbery account. 
myAccounts.withdraw("Shrubbery", 10)
# 6. Withdraw $1000 from the Shrubbery account. 
myAccounts.withdraw("Shrubbery", 1000)

# 7. Print the balances of the account. 
myAccounts.balances()
