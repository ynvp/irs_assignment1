# irs_assignment1

# Installing Dependencies
```pip install -r requirements.txt```

# Start development server
```flask run -h 127.0.0.1 -p 3456```

# Start Production Grade server using WSGI
```waitress-serve --host 0.0.0.0 --port 3456 app:app```

# Processing Steps

1. User visits irs.pradeep.win
2. User can use their own text files or sample text files provided on site to test
3. User uploads documents and clicks on Submit button
4. User enters query on the query page
5. System takes query and ranks documents based on the query terms
6. Documents Stemming and Lemmatization are done in ```query_result()``` in app.py
7. Results are returned to results.html template to show the score and ranking of 
the documents uploaded for the provided query


# Running Waitress Server as a Linux Service
store in irs.service file in /etc/systemd/system/
```
[Unit]
Description=irs service
StartLimitIntervalSec=300
StartLimitBurst=5

[Service]
WorkingDirectory=/root/irs
ExecStart=/root/irs/venv/bin/waitress-serve --host 0.0.0.0 --port 3456 app:app
Restart=always
RestartSec=1s

[Install]
WantedBy=multi-user.target
```
To start service
1. `sudo systemctl enable irs.service` --> enable service
2. `sudo systemctl start irs.service` --> start service
3. `sudo systemctl status irs.service` --> monitor status of service