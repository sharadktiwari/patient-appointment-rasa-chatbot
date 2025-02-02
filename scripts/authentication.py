# from passlib.context import CryptContext

# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# class Auth:

#     def verify_password(user_password, db_hashed_password):
#         try:
#             return pwd_context.verify(user_password, db_hashed_password)
#         except Exception as e:
#             raise Exception({'detail':' Chatbot - Authentication Error','status':'failed'})


#     def get_password_hash(password):
#         try:
#             return pwd_context.hash(password)
#         except:
#             raise Exception({'detail':' Chatbot - Authentication Error','status':'failed'})

