# Appoint Ease
Appoint Ease

## Want to use this project?

1. Fork/Clone

1. Create and activate a virtual environment:

    ```sh
    $ python3 -m venv venv && source venv/bin/activate
    ```
1. Create a .env file in folder where domain is placed
    ```sh
    DB_HOST = 
    DB_USER = 
    DB_PASSWORD = 
    DB_DATABASE = 
    DB_Connection_String = 
    TWILIO_ACCOUNT_SID = 
    TWILIO_AUTH_TOKEN = 
    ```
1. Install the requirements:

    ```sh
    (venv)$ pip3 install -r requirements.txt / pip install --no-cache-dir --upgrade -r requirements.txt
    ```

1. Run the bot:

    ```sh
    Requires Two terminals at the same time
    1. To start API
    (venv)$ rasa run --enable-api --cors="*"
    2. To start Action Server
    (venv)$ rasa run actions
    ```

1. Bind URL [http://0.0.0.0:5005] with Frontend
