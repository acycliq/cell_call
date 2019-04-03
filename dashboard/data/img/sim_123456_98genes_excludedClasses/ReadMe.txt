Spots from spots_DEFAULT_99GENES_123456.csv but the cell mapping algorithm
was run after 
excluding Gene: Vsnl1
AND
these classes
'Calb2.Vip.Nos1', 
'Cck.Cxcl14.Calb1.Tac2', 
'Cck.Cxcl14.Slc17a8', 
'Cck.Lmo1.Vip.Tac2',
'Eryth.1', 
'Microglia.2', 
'Oligo.3', 
'Sst.Nos1', 
'Vip.Crh.C1ql1', 
'Vip.Crh.Pcp4'
These classes never come up as best (most probable) class in the cell calling algo

I did that by adding these lines before line:
	nG = length(GeneNames); 
and after line:
	ClassNames = vertcat(unique(gSet.Class, 'stable'), {'Zero'}); 
in call_cells_sims.m (matlab script)

*******************
ExcludeClasses = {'Calb2.Vip.Nos1', 'Cck.Cxcl14.Calb1.Tac2', 'Cck.Cxcl14.Slc17a8', 'Cck.Lmo1.Vip.Tac2', ...
                    'Eryth.1', 'Microglia.2', 'Oligo.3', 'Sst.Nos1', 'Vip.Crh.C1ql1', 'Vip.Crh.Pcp4'};
IncludeClass = ~ismember(ClassNames, ExcludeClasses);             
ClassNames = ClassNames(IncludeClass);
*******************

