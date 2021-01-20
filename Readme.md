**Hello and welcome to the Econ Changes script.**

What this script does is read goods.ini, marketcommodities.ini, and the file Econ_changes.txt to execute the changes listed in Econ_changes. It then writes a new copy of the market_commodities.ini file. 

It produces a warning when the preffered route has a closer start point, BUT WILL insert new sale points at the base multiple if you tell it to make routes from bases that aren't already selling bases. Be aware of that, because you can wildly unbalance the economy if you set up Econ_changes poorly. 


The Econ_changes file is likely to have the most use to laypersons. 

It should read:
Start Base, End Base, Commodity, CR/sec

So a line of the Econ_changes.txt ought read:
`Graves Station, Planet New London, commodity_gold, 300`


To run Econ_changes, open your command prompt and navigate to the containing folder, and run update_econ.py


**Dependencies:**

* Python with Pandas. (installing python from anaconda will give you python with pandas)

* Properly formatted Econ_changes.txt

* market_commodities.ini: freelancer game file, data/equipment/market_commodities.ini
* goods.ini: freelancer game file, data/equipment/goods.ini 
* dump.csv: the base to base travel times exported by flcomp



**Further Steps**
* Add whatever the economy team asks for
* Build a function that will populate a blank market_commodities.ini with bases.
* wrap in previous technology for sorting buying bases to the closest sellers. 
* update the bat and paths to find a specified repo
* Improve this with a gui


**Changelog**
1. Version .01: initial program
2. Version .02: update_econ.py now inserts new sell points wherever you tell to start routes from in Econ_changes.txt. 
3. Version .03 includes a clickable bat for ease of use. 
