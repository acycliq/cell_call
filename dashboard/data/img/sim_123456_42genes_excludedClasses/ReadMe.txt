The same spots were used (from spots_123456.csv) but the cell mapping algorithm
was run after excluding these classes:
{
'Astro.1', 
'Astro.2', 
'Astro.5', 
'Cck.Calca', 
'Cck.Cxcl14.Calb1.Tac2', 
'Cck.Lmo1.Npy',
'Cck.Lmo1.Vip.Tac2', 
'Eryth.1', 
'Microglia.1', 
'Microglia.2', 
'Sst.Nos1', 
'Vsmc'
};

These classes never come up as best (most probable) class in the cell calling algo

I did that by adding these lines before line:
	nG = length(GeneNames); 
and after line:
	ClassNames = vertcat(unique(gSet.Class, 'stable'), {'Zero'}); 
in call_cells_sims.m (matlab script)

*******************
ExcludeClasses = {'Astro.1', 'Astro.2', 'Astro.5', 'Cck.Calca', 'Cck.Cxcl14.Calb1.Tac2', 'Cck.Lmo1.Npy', ... 
                  'Cck.Lmo1.Vip.Tac2', 'Eryth.1', 'Microglia.1', 'Microglia.2', 'Sst.Nos1', 'Vsmc'};       
IncludeClass = ~ismember(ClassNames, ExcludeClasses);             
ClassNames = ClassNames(IncludeClass);
*******************

