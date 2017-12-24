P2MP reliable File Transfer Protocol  
Version 1.0 11/27/2017

GENERAL USAGE NOTES
===================

- The code is tested on latest Ubuntu distribution.

Code Execution
--------------

#Executing server code
---------------------
python server.py <serverport> <destinationFilename> <lossProbability>

#Executing client code
----------------------
python client.py <server1IP> <server2IP> ... <servernIP> <serverport> <sourceFilename> <MSS>

====================================================================================================================================
