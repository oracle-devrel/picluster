----------------------------------------------------------------------



----------------------------------------------------------------------
Pi Cluster

This documents how to turn on the Pi Cluster. Everything can be remotely automated. Only 126 (or in one scenario 168) Pi can be turned on at any given time. You must be careful to turn on only what is needed because I do not have unlimited power and to turn it off when you are done because I pay the power bill.

NOTE: Every night at midnight PDT the cluster will do an automatic shutdown.

Public gateway: SSH into this server. An admin must add your key to this machine to grant you access and your gateway's public IP address.

ssh <BASTION>

Once you have SSHed to the public gateway, you need to SSH to the jump computer that is within my home subnet and spans both the cluster's network and my home subnet:

ssh <JUMPBOX>

There are three PUDs that control power to the cluster:

PDU1:
1 bottom bank 2 (has server so must be on if cluster is to function, requires an additional manual step, automating...)
2 top bank 2
3 bottom bank 1
4 top bank 1

PDU2
1 back switch (required to turn on any of these banks)
2 bottom bank 3
3 top bank 3
4 bottom bank 4
5 top bank 4

PDU3:
1 42 Pi currently connected to bottom bank 2
2 42 Pi currently connected to bottom bank 2
3 42 Pi currently connected to bottom bank 2
4 (If bank 1, then this is an additional 42 Pi)
5 Misc (currently Arduino to turn on server)

Solenoid
curl http://<SOLENOID>\?reset=0\&power=1

NOTE: PDU1 bank 1 must be turned on as this has the server

NOTE: If you turn on banks 2 or 4, you must turn on PDU2 bank 1 to turn on the switch that services those two banks.


You must turn on the server on PDU 1 first:

> telnet <PDU3>
> pshow
Port | Name       |Status
   1 |      Pi #1 |   OFF|
   2 |      Pi #2 |   OFF|
   3 |      Pi #3 |   OFF|
   4 | Pi#4 (N/A) |   OFF|
   5 |       Misc |   ON |
Port | Name       |Status
   1 |  #2 Server |   ON |   2 |     #2 Top |   ON |   3 |  #1 Bottom |   ON |   4 |     #1 Top |   ON |   5 |    Outlet5 |   ON |
> pset 1 1
> logout

NOTE: You can type 'help' at any point to get a list of options.

NOTE: PDU documentation can be found here:
https://www.synaccess-net.com/np-05b
https://static1.squarespace.com/static/54d27fb4e4b024eccdd9e569/t/6259cbade66b71218d8284ed/1650052014555/1094_NPStartup_V14.pdf


Once the server is turned on from the PDU1, the power button is a physical button. You turn this on by sending the curl command:

curl http://<SOLENOID>\?reset=0\&power=1


Wait a little bit then the server will boot up. Then ssh into the server with:

ssh <SERVER>

Turn on the first group of Pi by turning on the PDU 3:

> telnet <PDU3>
> pshow
Port | Name       |Status
   1 |      Pi #1 |   OFF|
   2 |      Pi #2 |   OFF|
   3 |      Pi #3 |   OFF|
   4 | Pi#4 (N/A) |   OFF|
   5 |       Misc |   ON |
> pset 1 1
> logout



----------------------------------------------------------------------


----------------------------------------------------------------------
