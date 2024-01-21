"""
Christian Peterson
Basic User-Account Website - Backend [IN PROGRESS]
(Utilizes FastAPI)
[January 2024]
"""

import pymysql
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel


app = FastAPI()

# Home page
@app.get("/")
def root_page():
    return "Welcome"

# Database connection with `pymysql`
cnx = pymysql.connect(host="_______",
                      user="________",
                      password="_________",
                      database="website_db",
                      charset = "utf8mb4",
                      cursorclass=pymysql.cursors.DictCursor,
                      autocommit = True)


# Data Validation - use Pydantic to maintain schema consistency
class User(BaseModel):
    username: str
    password: str
    f_name: str
    l_name: str
    security_question_answer: str = None # make this a choice to ask or not upon creation


# Create operation
@app.post("/users/", response_model=User)
def create_user_account(user: User):
    """Create an account for the user & obtain their ID number"""
    cursor = cnx.cursor()

    creation_query = "INSERT INTO users (username, passwd, f_name, l_name)\
                    VALUES (%s, %s, %s, %s, %s)"
    cursor.execute(creation_query, (user.username, 
                                    user.password, user.f_name, 
                                    user.l_name))
    cnx.commit()
    cursor.close()

    # Define a new cursor to obtain the `user_id`
    cursor2 = cnx.cursor()
    get_last_id = "SELECT LAST_INSERT_ID()"
    cursor2.execute(get_last_id)

    for row in cursor2.fetchall():
        user.user_id = row["LAST_INSERT_ID()"]
    cursor2.close()

    return user


# Read operation
# Removed password from function to enhance confidentiality
@app.get("/users/{user_id}", response_model=User)
def read_user_info(user_id: int):
    """Obtain information of an account based on unique Primary Key (ID)"""
    cursor = cnx.cursor()

    read_query = "SELECT user_id, username, f_name, l_name \
                  FROM users WHERE user_id=%s"
    cursor.execute(read_query, (user_id))

    user = cursor.fetchall()
    cursor.close()

    # Throw exceptions if a user does not exist/is not found
    if user is None:
        raise HTTPException(status_code=404,
                            detail="Item Not Found")
    
    else:
        user_dct = {"user_id": user[0],
                    "username": user[1],  
                    "f_name": user[3], "l_name": user[4]}

    return user_dct


# Update operation
@app.put("/users/{user_id}", response_model=User)
def update_user_info(user_id: int, user: User):
    """Update a user's information based on Primary Key (ID)"""

    cursor = cnx.cursor()

    update_query = "UPDATE users SET username, passwd, f_name, l_name \
                    WHERE user_id=%s"
    cursor.execute(update_query, (user.username, 
                                  user.password, user.f_name, 
                                  user.l_name, user_id))
    cnx.commit()
    cursor.close()

    user.user_id = user_id

    return user


# Delete operation
@app.delete("/users/{user_id}", response_model=User)
def delete_user(user_id: int):
    """Delete a user's profile based on Primary Key (ID)"""

    cursor = cnx.cursor()

    delete_query = "DELETE FROM users WHERE user_id=%s"
    cursor.execute(delete_query, (user_id))

    cnx.commit()
    cursor.close()

    return {"user_id": user_id}

'''
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="localhost", port=8000)
'''