The same spots were used (from spots_123456.csv) but the cell mapping algorithm
was run after excluding these classes:
{
 'Cck.Cxcl14.Calb1.Tac2k',
 'Cck.Cxcl14.Slc17a8',
 'Cck.Lmo1.Vip.Tac2',
 'Eryth.1',
 'Microglia.1',
 'Microglia.2',
 'Oligo.3',
 'Pvalb.C1ql1.Cpne5',
 'Sst.Erbb4.Th',
 'Sst.Nos1',
 'Vip.Crh.Pcp4',
 'Vsmc'
};

These classes never come up as best (most probable) class in the cell calling algo

I did that by adding these lines after line 60 in call_cells_sims.m (matlab script)

*******************
ExcludeClasses = {'Cck.Cxcl14.Calb1.Tac2k', 'Cck.Cxcl14.Slc17a8', 'Cck.Lmo1.Vip.Tac2', ...
                  'Eryth.1', 'Microglia.1', 'Microglia.2', 'Oligo.3', 'Pvalb.C1ql1.Cpne5', ...
                  'Sst.Erbb4.Th', 'Sst.Nos1', 'Vip.Crh.Pcp4', 'Vsmc'};
              
IncludeClass = ~ismember(ClassNames, ExcludeClasses);             
ClassNames = ClassNames(IncludeClass);
*******************

