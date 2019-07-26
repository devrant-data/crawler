import shelfdb
import requests
import sys
from random import randrange

## CONFIG ##
api_base = "https://devrant.com/api"

app_id = 3
plat_id = 2
############


## HELPERS ##

def getUserId(username):
    response = requests.get(api_base + "/get-user-id", params={"app": app_id, "plat": plat_id, "username": username}).json()
    
    # Check for a failed response
    if not response["success"]:
        return 0
    
    return response["user_id"]

def getProfile(user):
    # Check for user input type
    if type(user) == str:
        user = getUserId(user)

    # Read the user's profile
    response = requests.get(api_base + "/users/" + str(user), params={"app": app_id, "plat": plat_id}).json()

    # Check for a failed response
    if not response["success"]:
        return None
    
    return response["profile"]

def hasUserEntered(user, db):
    return user in [e["username"] for e in db.shelf('countries').filter(lambda u: u)]

## MAIN PROGRAM ##

if len(sys.argv) != 2:
    print("Must provide a username in the args")
    exit(1)

starting_user = sys.argv[1]

db = shelfdb.open('./data/db')
db.shelf('users')
db.shelf('countries')

# Loop through one user at a time to crawl
current_user = starting_user
while True:
    user_data = getProfile(current_user)
    print("Processing "+ user_data["username"])

    # Calculate upvote offset if user has been read before
    if hasUserEntered(user_data["username"], db):
        offset = randrange(len(user_data["content"]["content"]["upvoted"]))
        print("Using offset " +str(offset))
    else:
        offset = 0

        # Add location info to DB
        db.shelf('countries').insert({"username": user_data["username"], "location": user_data["location"]})
        
        # Add full profile info to DB
        stripped_user = user_data.copy()
        del stripped_user["content"]

        db.shelf("users").insert(stripped_user)

    # Set the next user to crawl
    try:
        current_user = user_data["content"]["content"]["upvoted"][offset]["user_id"]
    except:
        print("Crawler has hit the end of the chain with user: "+ user_data["username"])
        break

