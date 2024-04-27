import requests
telebot_token = input('Введите свой токен от BOTfather')
def create_new_token():
    metadata_url = "http://169.254.169.254/computeMetadata/v1/instance/service-accounts/default/token"
    headers = {"Metadata-Flavor": "Google"}
    response = requests.get(metadata_url, headers=headers)
    return response.json()
IAMTOKEN = create_new_token()
MAX_USER_TTS_SYMBOLS = 1000
MAX_TTS_SYMBOLS = 200
FOLDER_ID = input('Введите совй фолдер айди')
