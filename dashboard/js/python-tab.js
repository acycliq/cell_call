// listener on the python tab
$('#python-tab').on('shown.bs.tab', function (e) {
    console.log('Workflow tab was clicked.');
    $('#myDropdown').hide(); // hide the dropdown
    $('#myDropdown2').hide(); // hide the dropdown
    $('#myDropdown3').hide(); // hide the dropdown
    $('#myDropdown4').hide(); // hide the dropdown
    $('#myDropdown5').hide(); // hide the dropdown

    // hide the toolip raised by the section chart
    d3.select('#tooltip').style('opacity', 0)


});
