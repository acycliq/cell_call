function iss = parseIss(issObj)
% Small script that loops through the properties of an iss object, reads
% all its properties and saves them and the associated values into a
% structure

% get all properties of the object
p = properties(issObj);

% loop over the properties
for i = 1:length(p)
    pName = p{i};
    iss.(pName) = issObj.(pName);
end

% Manual overrides
[m, ~, n] = size(issObj.cSpotColors);
if isempty(iss.cAnchorIntensities)
    iss.cAnchorIntensities = (issObj.DetectionThresh+1) * ones(m,n);
end
iss.GeneNames(strcmp(issObj.GeneNames, 'Lphn2')) = {'Adgrl2'};

save('iss.mat', 'iss')

    