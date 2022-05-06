## SLIM Pickins: An Interactive Circuit Layout Tool for Planar Traveling Wave Ion Guides
* BHC 01.Feb.2022
* [GNU General Public License v3.0](https://www.gnu.org/licenses/gpl-3.0.en.html)
* This research product was developed with the support of the [NIGMS](https://www.nigms.nih.gov/) R01-GM140129

This is to be placed in the KiCAD 6 plugins folder. 

### BEWARE -- The correct number of SLIM monomers MUST be present on the board in order for this to occur. 

### SAVE A COPY OF YOUR WORK BEFORE EXECUTING THIS SCRIPT

For example if you need 70 SLIM monomers total
* 40 SLIM Monomers with the guard on top
* 30 SLIM monomers with the guard on bottom 

(These numbers will be output by the SLIM Pickins layout tool)

Select all of these monomers and starte the layout plugin.  

### IF YOU DON'T HAVE THE CORRECT NUMBER OF MONOMERS, THIS WILL FAIL.

Known Issue: This script aims to layout the monomers based upon their sequential numbering. If the numbering is wonky through some sort of
KiCAD annotation setting you can get odd results where the monomers get placed in positions that were not originally intended.  Generally, it
is best to start with the fresh KiCAD project when running this script. 

Finally, this does not wire the tracks for you.  That is something that you must do, though the wiring template can surely help as KiCAD
supports Copy and Paste along with grouping. 
 
