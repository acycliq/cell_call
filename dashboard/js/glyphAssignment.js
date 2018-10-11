

function glyphAssignment()
{
    var out = [

        {gene: 'Snca', taxonomy: 'in_general', glyphSymbol:   '+', glyphName: 'plus', glyphColor:  '#5C33FF' },
        {gene: 'Cplx2', taxonomy: 'in_general', glyphSymbol:   '.', glyphName: 'point', glyphColor:  '#5C33FF' },
        {gene: 'Lhx6', taxonomy: 'in_general', glyphSymbol:   's', glyphName: 'square', glyphColor:  '#5C33FF' },
        {gene: 'Col25a1', taxonomy: 'in_general', glyphSymbol:   '^', glyphName: 'triangleUp', glyphColor:  '#5C33FF' },
        {gene: 'Pnoc', taxonomy: 'in_general', glyphSymbol:   '>', glyphName: 'triangleRight', glyphColor:  '#5C33FF' },
        {gene: 'Rab3c', taxonomy: 'in_general', glyphSymbol:   '<', glyphName: 'triangleLeft', glyphColor:  '#5C33FF' },
        {gene: 'Gad1', taxonomy: 'in_general', glyphSymbol:   'p', glyphName: 'star5', glyphColor:  '#5C33FF' },
        {gene: 'Slc6a1', taxonomy: 'in_general', glyphSymbol:   'h', glyphName: 'star6', glyphColor:  '#5C33FF' },
        {gene: 'Th', taxonomy: 'sst', glyphSymbol:   '+', glyphName: 'plus', glyphColor:  '#995C00' },
        {gene: 'Crhbp', taxonomy: 'sst', glyphSymbol:   'o', glyphName: 'circle', glyphColor:  '#995C00' },
        {gene: 'Sst', taxonomy: 'sst', glyphSymbol:   '*', glyphName: 'asterisk', glyphColor:  '#995C00' },
        {gene: 'Npy', taxonomy: 'sst', glyphSymbol:   '.', glyphName: 'point', glyphColor:  '#995C00' },
        {gene: 'Synpr', taxonomy: 'sst', glyphSymbol:   'x', glyphName: 'cross', glyphColor:  '#995C00' },
        {gene: 'Chodl', taxonomy: 'sst', glyphSymbol:   's', glyphName: 'square', glyphColor:  '#995C00' },
        {gene: 'Cort', taxonomy: 'sst', glyphSymbol:   'd', glyphName: 'diamond', glyphColor:  '#995C00' },
        {gene: 'Reln', taxonomy: 'sst', glyphSymbol:   '^', glyphName: 'triangleUp', glyphColor:  '#995C00' },
        {gene: 'Serpini1', taxonomy: 'sst', glyphSymbol:   '<', glyphName: 'triangleLeft', glyphColor:  '#995C00' },
        {gene: 'Satb1', taxonomy: 'sst', glyphSymbol:   '>', glyphName: 'triangleRight', glyphColor:  '#995C00' },
        {gene: 'Grin3a', taxonomy: 'sst', glyphSymbol:   'p', glyphName: 'star5', glyphColor:  '#995C00' },
        {gene: 'Tac1', taxonomy: 'pvalb', glyphSymbol:   'o', glyphName: 'circle', glyphColor:  '#0000FF' },
        {gene: 'Pvalb', taxonomy: 'pvalb', glyphSymbol:   '*', glyphName: 'asterisk', glyphColor:  '#0000FF' },
        {gene: 'Kcnip2', taxonomy: 'pvalb', glyphSymbol:   's', glyphName: 'square', glyphColor:  '#0000FF' },
        {gene: 'Thsd7a', taxonomy: 'pvalb', glyphSymbol:   'd', glyphName: 'diamond', glyphColor:  '#0000FF' },
        {gene: 'Cox6a2', taxonomy: 'pvalb', glyphSymbol:   'v', glyphName: 'triangleDown', glyphColor:  '#0000FF' },
        {gene: 'Chrm2', taxonomy: 'pvalb', glyphSymbol:   'p', glyphName: 'star5', glyphColor:  '#0000FF' },
        {gene: 'Id2', taxonomy: 'ngf', glyphSymbol:   '+', glyphName: 'plus', glyphColor:  '#44B200' },
        {gene: 'Hapln1', taxonomy: 'ngf', glyphSymbol:   'o', glyphName: 'circle', glyphColor:  '#44B200' },
        {gene: 'Gabrd', taxonomy: 'ngf', glyphSymbol:   '*', glyphName: 'asterisk', glyphColor:  '#44B200' },
        {gene: 'Cryab', taxonomy: 'ngf', glyphSymbol:   'x', glyphName: 'cross', glyphColor:  '#44B200' },
        {gene: 'Kit', taxonomy: 'ngf', glyphSymbol:   's', glyphName: 'square', glyphColor:  '#44B200' },
        {gene: 'Ndnf', taxonomy: 'ngf', glyphSymbol:   'd', glyphName: 'diamond', glyphColor:  '#44B200' },
        {gene: 'Nos1', taxonomy: 'ngf', glyphSymbol:   '^', glyphName: 'triangleUp', glyphColor:  '#44B200' },
        {gene: 'Lamp5', taxonomy: 'ngf', glyphSymbol:   '>', glyphName: 'triangleRight', glyphColor:  '#44B200' },
        {gene: 'Cplx3', taxonomy: 'ngf', glyphSymbol:   'h', glyphName: 'star6', glyphColor:  '#44B200' },
        {gene: 'Cadps2', taxonomy: 'cxcl14', glyphSymbol:   'o', glyphName: 'circle', glyphColor:  '#00B2FF' },
        {gene: 'Cxcl14', taxonomy: 'cxcl14', glyphSymbol:   '*', glyphName: 'asterisk', glyphColor:  '#00B2FF' },
        {gene: 'Ntng1', taxonomy: 'cxcl14', glyphSymbol:   's', glyphName: 'square', glyphColor:  '#00B2FF' },
        {gene: 'Cpne5', taxonomy: 'cxcl14', glyphSymbol:   'd', glyphName: 'diamond', glyphColor:  '#00B2FF' },
        {gene: 'Rgs12', taxonomy: 'cxcl14', glyphSymbol:   'h', glyphName: 'star6', glyphColor:  '#00B2FF' },
        {gene: 'Sncg', taxonomy: 'cnr1', glyphSymbol:   'o', glyphName: 'circle', glyphColor:  '#FFC700' },
        {gene: 'Cnr1', taxonomy: 'cnr1', glyphSymbol:   '*', glyphName: 'asterisk', glyphColor:  '#FFC700' },
        {gene: 'Cck', taxonomy: 'cnr1', glyphSymbol:   '.', glyphName: 'point', glyphColor:  '#FFC700' },
        {gene: 'Trp53i11', taxonomy: 'cnr1', glyphSymbol:   'x', glyphName: 'cross', glyphColor:  '#FFC700' },
        {gene: 'Sema3c', taxonomy: 'cnr1', glyphSymbol:   's', glyphName: 'square', glyphColor:  '#FFC700' },
        {gene: 'Syt6', taxonomy: 'cnr1', glyphSymbol:   '^', glyphName: 'triangleUp', glyphColor:  '#FFC700' },
        {gene: 'Yjefn3', taxonomy: 'cnr1', glyphSymbol:   'v', glyphName: 'triangleDown', glyphColor:  '#FFC700' },
        {gene: 'Rgs10', taxonomy: 'cnr1', glyphSymbol:   '>', glyphName: 'triangleRight', glyphColor:  '#FFC700' },
        {gene: 'Nov', taxonomy: 'cnr1', glyphSymbol:   '<', glyphName: 'triangleLeft', glyphColor:  '#FFC700' },
        {gene: 'Kctd12', taxonomy: 'cnr1', glyphSymbol:   'p', glyphName: 'star5', glyphColor:  '#FFC700' },
        {gene: 'Slc17a8', taxonomy: 'cnr1', glyphSymbol:   'h', glyphName: 'star6', glyphColor:  '#FFC700' },
        {gene: 'Tac2', taxonomy: 'vip', glyphSymbol:   '+', glyphName: 'plus', glyphColor:  '#FF0000' },
        {gene: 'Npy2r', taxonomy: 'vip', glyphSymbol:   'o', glyphName: 'circle', glyphColor:  '#FF0000' },
        {gene: 'Calb2', taxonomy: 'vip', glyphSymbol:   '*', glyphName: 'asterisk', glyphColor:  '#FF0000' },
        {gene: 'Htr3a', taxonomy: 'vip', glyphSymbol:   '.', glyphName: 'point', glyphColor:  '#FF0000' },
        {gene: 'Slc5a7', taxonomy: 'vip', glyphSymbol:   'x', glyphName: 'cross', glyphColor:  '#FF0000' },
        {gene: 'Penk', taxonomy: 'vip', glyphSymbol:   's', glyphName: 'square', glyphColor:  '#FF0000' },
        {gene: 'Pthlh', taxonomy: 'vip', glyphSymbol:   '^', glyphName: 'triangleUp', glyphColor:  '#FF0000' },
        {gene: 'Vip', taxonomy: 'vip', glyphSymbol:   'v', glyphName: 'triangleDown', glyphColor:  '#FF0000' },
        {gene: 'Crh', taxonomy: 'vip', glyphSymbol:   '>', glyphName: 'triangleRight', glyphColor:  '#FF0000' },
        {gene: 'Qrfpr', taxonomy: 'vip', glyphSymbol:   'p', glyphName: 'star5', glyphColor:  '#FF0000' },
        {gene: 'Zcchc12', taxonomy: 'less_active', glyphSymbol:   '+', glyphName: 'plus', glyphColor:  '#407F59' },
        {gene: 'Calb1', taxonomy: 'less_active', glyphSymbol:   '*', glyphName: 'asterisk', glyphColor:  '#407F59' },
        {gene: 'Vsnl1', taxonomy: 'less_active', glyphSymbol:   '.', glyphName: 'point', glyphColor:  '#407F59' },
        {gene: 'Tmsb10', taxonomy: 'less_active', glyphSymbol:   'd', glyphName: 'diamond', glyphColor:  '#407F59' },
        {gene: 'Rbp4', taxonomy: 'less_active', glyphSymbol:   'v', glyphName: 'triangleDown', glyphColor:  '#407F59' },
        {gene: 'Fxyd6', taxonomy: 'less_active', glyphSymbol:   '^', glyphName: 'triangleUp', glyphColor:  '#407F59' },
        {gene: '6330403K07Rik', taxonomy: 'less_active', glyphSymbol:   '<', glyphName: 'triangleLeft', glyphColor:  '#407F59' },
        {gene: 'Scg2', taxonomy: 'less_active', glyphSymbol:   '>', glyphName: 'triangleRight', glyphColor:  '#407F59' },
        {gene: 'Gap43', taxonomy: 'less_active', glyphSymbol:   'p', glyphName: 'star5', glyphColor:  '#407F59' },
        {gene: 'Nrsn1', taxonomy: 'less_active', glyphSymbol:   'h', glyphName: 'star6', glyphColor:  '#407F59' },
        {gene: 'Gda', taxonomy: 'pc_or_in', glyphSymbol:   '+', glyphName: 'plus', glyphColor:  '#96B28E' },
        {gene: 'Bcl11b', taxonomy: 'pc_or_in', glyphSymbol:   'o', glyphName: 'circle', glyphColor:  '#96B28E' },
        {gene: 'Rgs4', taxonomy: 'pc_or_in', glyphSymbol:   '*', glyphName: 'asterisk', glyphColor:  '#96B28E' },
        {gene: 'Slc24a2', taxonomy: 'pc_or_in', glyphSymbol:   '.', glyphName: 'point', glyphColor:  '#96B28E' },
        {gene: 'Lphn2', taxonomy: 'pc_or_in', glyphSymbol:   'x', glyphName: 'cross', glyphColor:  '#96B28E' },
        {gene: 'Adgrl2', taxonomy: 'pc_or_in', glyphSymbol:   'x', glyphName: 'cross', glyphColor:  '#96B28E' },
        {gene: 'Map2', taxonomy: 'pc_or_in', glyphSymbol:   's', glyphName: 'square', glyphColor:  '#96B28E' },
        {gene: 'Prkca', taxonomy: 'pc_or_in', glyphSymbol:   'd', glyphName: 'diamond', glyphColor:  '#96B28E' },
        {gene: 'Cdh13', taxonomy: 'pc_or_in', glyphSymbol:   '^', glyphName: 'triangleUp', glyphColor:  '#96B28E' },
        {gene: 'Atp1b1', taxonomy: 'pc_or_in', glyphSymbol:   'v', glyphName: 'triangleDown', glyphColor:  '#96B28E' },
        {gene: 'Pde1a', taxonomy: 'pc_or_in', glyphSymbol:   '<', glyphName: 'triangleLeft', glyphColor:  '#96B28E' },
        {gene: 'Calm2', taxonomy: 'pc_or_in', glyphSymbol:   '>', glyphName: 'triangleRight', glyphColor:  '#96B28E' },
        {gene: 'Sema3e', taxonomy: 'pc_or_in', glyphSymbol:   'h', glyphName: 'star6', glyphColor:  '#96B28E' },
        {gene: 'Nrn1', taxonomy: 'pc', glyphSymbol:   '*', glyphName: 'asterisk', glyphColor:  '#FFFFFF' },
        {gene: 'Pcp4', taxonomy: 'pc', glyphSymbol:   '.', glyphName: 'point', glyphColor:  '#FFFFFF' },
        {gene: 'Rprm', taxonomy: 'pc', glyphSymbol:   '+', glyphName: 'plus', glyphColor:  '#FFFFFF' },
        {gene: 'Enpp2', taxonomy: 'pc', glyphSymbol:   'x', glyphName: 'cross', glyphColor:  '#FFFFFF' },
        {gene: 'Rorb', taxonomy: 'pc', glyphSymbol:   'o', glyphName: 'circle', glyphColor:  '#FFFFFF' },
        {gene: 'Rasgrf2', taxonomy: 'pc', glyphSymbol:   's', glyphName: 'square', glyphColor:  '#FFFFFF' },
        {gene: 'Wfs1', taxonomy: 'pc', glyphSymbol:   'd', glyphName: 'diamond', glyphColor:  '#FFFFFF' },
        {gene: 'Fos', taxonomy: 'pc', glyphSymbol:   '>', glyphName: 'triangleRight', glyphColor:  '#FFFFFF' },
        {gene: 'Plcxd2', taxonomy: 'pc', glyphSymbol:   'v', glyphName: 'triangleDown', glyphColor:  '#FFFFFF' },
        {gene: 'Crym', taxonomy: 'pc', glyphSymbol:   '<', glyphName: 'triangleLeft', glyphColor:  '#FFFFFF' },
        {gene: '3110035E14Rik', taxonomy: 'pc', glyphSymbol:   '^', glyphName: 'triangleUp', glyphColor:  '#FFFFFF' },
        {gene: 'Foxp2', taxonomy: 'pc', glyphSymbol:   'p', glyphName: 'star5', glyphColor:  '#FFFFFF' },
        {gene: 'Pvrl3', taxonomy: 'pc', glyphSymbol:   'h', glyphName: 'star6', glyphColor:  '#FFFFFF' },
        {gene: 'Neurod6', taxonomy: 'pc2', glyphSymbol:   '+', glyphName: 'plus', glyphColor:  '#FF00E5' },
        {gene: 'Nr4a2', taxonomy: 'pc2', glyphSymbol:   'o', glyphName: 'circle', glyphColor:  '#FF00E5' },
        {gene: 'Cux2', taxonomy: 'pc2', glyphSymbol:   '*', glyphName: 'asterisk', glyphColor:  '#FF00E5' },
        {gene: 'Kcnk2', taxonomy: 'pc2', glyphSymbol:   '.', glyphName: 'point', glyphColor:  '#FF00E5' },
        {gene: 'Arpp21', taxonomy: 'pc2', glyphSymbol:   's', glyphName: 'square', glyphColor:  '#FF00E5' },
        {gene: 'Enc1', taxonomy: 'pc2', glyphSymbol:   'v', glyphName: 'triangleDown', glyphColor:  '#FF00E5' },
        {gene: 'Fam19a1', taxonomy: 'pc2', glyphSymbol:   '>', glyphName: 'triangleRight', glyphColor:  '#FF00E5' },
        {gene: 'Vim', taxonomy: 'non_neuron', glyphSymbol:   '*', glyphName: 'asterisk', glyphColor:  '#00FF00' },
        {gene: 'Slc1a2', taxonomy: 'non_neuron', glyphSymbol:   '.', glyphName: 'point', glyphColor:  '#00FF00' },
        {gene: 'Pax6', taxonomy: 'non_neuron', glyphSymbol:   's', glyphName: 'square', glyphColor:  '#00FF00' },
        {gene: 'Plp1', taxonomy: 'non_neuron', glyphSymbol:   'x', glyphName: 'cross', glyphColor:  '#00FF00' },
        {gene: 'Mal', taxonomy: 'non_neuron', glyphSymbol:   '+', glyphName: 'plus', glyphColor:  '#00FF00' },
        {gene: 'Aldoc', taxonomy: 'non_neuron', glyphSymbol:   'o', glyphName: 'circle', glyphColor:  '#00FF00' },
        {gene: 'Actb', taxonomy: 'non_neuron', glyphSymbol:   'v', glyphName: 'triangleDown', glyphColor:  '#00FF00' },
        {gene: 'Sulf2', taxonomy: 'non_neuron', glyphSymbol:   'p', glyphName: 'star5', glyphColor:  '#00FF00' },

        ];
    
    return out
}