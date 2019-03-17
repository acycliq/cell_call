This has been created by
1) getting spots simulated for all 99 genes
2) excluding spots from Vsnl1 only
3) feeding the remaining spots in the cell calling algorithm

However the simulator doesnt pick up gene: Chodl. That happens because Chodl is 
typically expressed in the Sst.Nos1 class. This class however is not the most likely 
class for any of the cells. This together with the shrinkage step result in the 
gene not getting picked up by the simulator, hence now spots are simulated from Chodl.

Therefore in theory I am excluding only Vsnl1 but in practice, Chodl is ignored too.

