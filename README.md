# Instrument-Monitor
This was a side project that I completed on my first co-op. 
It goes through a network drive to connect to 6 different UPLC/HPLC instruments and reads a .ini file that they generate.
These instruments are named titanium (Ti), platinum (Pt), gold (Au), neon (Ne), nickel (Ni), and cobalt (Co).
Since the instruments are from two different manufacturers, it splits and then processes these .ini files depending on the manufacturer.
Then, it uses these files to determine the status of the instruments 
(i.e. which modules are running, which are stopped, what is in the queue, etc.). 
It then puts this information into two HTML files:
one with all of the instruments (Monitor_HTML_Location) and one with only the open access instruments (Monitor_OA). 
The HTML files are updated every 15 seconds to provide live updates for any scientists in the laboratory. 
The HTML files additionally allow users to email the individuals in charge of the instruments if there is a problem. 
To help draw attention to the errors, if an error is detected, the instument name is highlighted red.
Since these instruments are finicky and sometimes report being paused when they are not,
it also starts a timer to tell you how long ago the errror occured to allow a user to decide if it is a real problem or not and how
long an instrument has been down for. 
And since these HTML files are constantly open on numerous computers, 
it changes background colors every season, just to add a little diversity.
