#!/usr/bin/env python3
import argparse
import re
import sys
from getpass import getpass
import requests
import pickle
headers = {
    'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 12_3_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 Instagram 105.0.0.11.118 (iPhone11,8; iOS 12_3_1; en_US; en-US; scale=2.00; 828x1792; 165586599)',
}

BASE_URL = 'https://www.instagram.com/'
LOGIN_URL = BASE_URL + 'accounts/login/ajax/'
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko)\
Chrome/59.0.3071.115 Safari/537.36'

#Setting some headers and refers
session = requests.Session()

def setCredentials():
    try:
        with open('cookie', 'rb') as f:
            session.cookies.update(pickle.load(f))
    except:
        print("Generating Cookies")
        print("--------------------")
        print("Enter your login details->")
        USERNAME=input("Enter username: ")
        PASSWD = getpass()
        session.headers = {'user-agent': USER_AGENT}
        session.headers.update({'Referer': BASE_URL})
        try:
            #Requesting the base url. Grabbing and inserting the csrftoken
            req = session.get(BASE_URL)
            session.headers.update({'X-CSRFToken': req.cookies['csrftoken']})
            login_data = {'username': USERNAME, 'password': PASSWD}
            #Finally login in
            login = session.post(LOGIN_URL, data=login_data, allow_redirects=True)
            session.headers.update({'X-CSRFToken': login.cookies['csrftoken']})
            cookies = login.cookies
            if '"authenticated": false' in login.text:
                print("\n!!! Incorrect Login Details","\nLogin Again->\n")
                return setCredentials()
            else:
                with open('cookie', 'wb') as f:
                    pickle.dump(session.cookies, f)
                print("Successfully logged in!")
        except requests.exceptions.ConnectionError:
            print("Connection refused")


def getID(username):
    url = "https://www.instagram.com/{}/?__a=1"
    r = requests.get(url.format(username))
    try:
        data=r.json()
        data=data['logging_page_id'].replace("profilePage_","")
        return data
    except:
        print("\033[91m✘ Invalid username\033[0m")
        sys.exit()


def fetchDP(userID):
    url = "https://i.instagram.com/api/v1/users/{}/info/"
    r = session.get(url.format(userID),headers=headers)
    if r.ok:
        data = r.json()
        return data['user']['hd_profile_pic_url_info']['url']
    else:
        print("\033[91m✘ Cannot find user ID \033[0m")
        sys.exit()


def main():
    setCredentials()
    username=input("\nEnter Username of the profile: ")
    user_id = getID(username)
    file_url = fetchDP(user_id)
    print("\nDP URL:-",file_url)
    down=input("\nWant to download(y/n)?(default=n)")
    if(down=="y"):
        fname = username+".jpg"
        r = requests.get(file_url, stream=True)
        if r.ok:
            with open(fname, 'wb') as f:
                f.write(r.content)
                print("\033[92m✔ Downloaded:\033[0m {}".format(fname))
        else:
            print("Cannot make connection to download image")
if __name__ == "__main__":
    main()
