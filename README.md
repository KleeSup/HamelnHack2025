# Complete project from Hameln Hackathon 2025

## Event
Type: Hackathon
Location: Hameln, Germany
Date: 30. October 2025
Time: 12 hours
Group size: 2 people

## Task
Building a software for [Lenze SE](https://www.lenze.com/de-de) that notifies workers in machine rooms once a machine stops working due to an error or other problems and give the worker a way to understand and find the problem directly without needing to read through a manual with an error code.

## Our solution
Build a backend written in Go which uses OPC-UA to connect to the machines MCP server and create a heartbeat looking for updates. Furthermore a mobile app for Android was built in Kotlin using Firebase for push notifications. At last we also created an agent system in python with our own orchestrator and different models. This will be used for reading the manual of all machines and using the information to directly establish solution prompting to the worker.
Once an exception is thrown, the backend will send push notifications via Firebase and simultaneously warm up the agent system.
In the app the user has the ability to "chat with the error" meaning a fully updated chat conversation will be initiated in which the user can ask the AI for the next steps.
The user can also send the error via e-mail to an e-mail specified in the backend by requesting it to the chatbot.
Messages and chats will be stored in a Postgres database, the connection between the app and the backend is done by using REST.

## Tech-Stack
Golang
Python
Kotlin
OPC-UA / MCP
REST
Postgres / SQL
Firebase

## Learnings
It was great building something meaningful and actually required in the real world while still being under stress of time but looking forward to accomplishing what's wanted. The teamwork was what made it possible and everyone had much to learn. The fun we had was greater than the stress we felt for building it completely, which was all that mattered.
