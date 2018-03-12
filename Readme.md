## Python Keylogger

#### Basic usage

```bash
python monitor.py
```

this will start listening and log keys on file called keys.log in current directory

#### Arguments

```
-l --log
	path of log file
-e --send
    prompt for email and password and send logs on mail
-d --delay
    delay for sending email (default 60 seconds)
```

#### Full example
```
python monitor.py --logs keys.txt --send -d 40
```
