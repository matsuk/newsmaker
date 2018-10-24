# Newsmaker
Newsmaker is a tool for automatic web pages changes search. It consists of a program and a web interface for configuring it. 
## Getting started
### Download
To download the project use:
```bash
git clone https://github.com/matsuk/newsmaker.git
```
### Prerequisites
Before using you should install all needed requirements:
```bash
cd newsmaker
pip3 install -r requirements.txt
```
### Configuring
Then, the program should be configured via web interface:
```bash
cd configure
python3 control.py
```
Go to your browser and open localhost:5000 (by default).
First, the group must be created. E-mails is a list of addresses where the results will be sent.
Second, pages must be added for each group. Specify URLs, name and amount of copies of each page to store.
After that, the server can be killed.
Also, you should specify your e-mail in configure/mail file to send notifications to recipients.

## Run
Now the program is ready to run:
```bash
cd ..
python3 newsmaker.py
```

