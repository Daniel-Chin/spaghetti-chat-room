# Spaghetti chat room
Final project for Computer Networking @ NYU Shanghai

## The general idea
I did not use any third party library.  
Python backend is built directly on socket.  
Frontend is a JS-HTML spaghetti mess.  
My friend saw me and was like "Use React PLEASE"  
This is my personal first web app.  

## Highlight
* Real-time preview of what the others are typing.  
* Low-traffic low-latency polling from js client. How? Deliberately block a backend response until fresh data come. I probably reinvented some wheels here.  

## How to run
* Run the python backend `server.py`.  
* Use browser to go to the displayed IP.  
* Invite a friend to test it with you, or open another tab.  

## misc
See `Hack.txt` for snippets I used to stress-test classmates' projects on the presentation day
