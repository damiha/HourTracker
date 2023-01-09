import hashlib

# at the momemt there can only be one user
print("Create a new user (overrides current user)")
decision = input("Do you want to continue ?[y/n]")

if decision != "y":
    exit()

username = input("username:\t")
password = input("password:\t")

# hash password and write to txt files users
hashed_password = hashlib.md5(password.encode())

f = open("users.txt", "w")
f.write(username + "\n" + hashed_password.hexdigest())
f.close()

print("Sucessfully written user data to file!")

f = open("secret_key.txt", "w")
f.write(hashlib.sha256().hexdigest())
f.close()

print("Sucessfully created secret session key")