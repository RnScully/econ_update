**Hello and welcome to the Econ Changes script.**

What this script does is read goods.ini, marketcommodities.ini, and the file Econ_changes.txt to execute the changes listed in Econ_changes. It then writes a new copy of the market_commodities.ini file. 

It produces a warning when the preffered route has a closer start point, BUT WILL insert new sale points at the base multiple if you tell it to make routes from bases that aren't already selling bases. Be aware of that, because you can wildly unbalance the economy if you set up Econ_changes poorly. 


The Econ_changes file is likely to have the most use to laypersons. 

It should read:
Start Base, End Base, Commodity, CR/sec

So a line of the Econ_changes.txt ought read:
"Graves Station, Planet New London, commodity_gold, 300"



To run Econ_changes, open your command prompt and navigate to the containing folder, and run update_econ.py


**Dependencies:**

Python with Pandas. (installing python from anaconda will give you python with pandas)
market_commodities, dump.csv and goods.ini in the same folder as update_econ.py
Properly formatted Econ_changes.txt

market_commodities.ini: freelancer game file, data/missions/market_commodities.ini
goods.ini: freelancer game file, data/missons/goods.ini *citation needed
dump.csv: the base to base travel times exported by flcomp

**Changelog**
Version .01: initial program
Version .02: update_econ.py now inserts new sell points wherever you tell to start routes from in Econ_changes.txt. 


**Further Steps**
0: Add whatever the economy team asks for
1: Build a function that will populate a blank market_commodities.ini with bases.
2: wrap in previous technology for sorting buying bases to the closest sellers. 
3: Improve this with a gui


