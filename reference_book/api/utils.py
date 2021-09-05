from django.contrib.auth import get_user_model


User = get_user_model()


def set_username(email):
    username = email.split('@')[0]
    counter = 1
    while User.objects.filter(username=username):
        username = username + str(counter)
        counter += 1
    return username