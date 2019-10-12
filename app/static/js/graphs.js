$(document).ready(function(){
    var days = 10;
    $.getJSON($SCRIPT_ROOT + '/_ohlc/' + days, function(data) {
  });
});


$(document).ready(function(){
    $.getJSON('https://www.highcharts.com/samples/data/jsonp.php?filename=aapl-c.json&callback=?', function (data)    {
        // Create the chart

        var dataObject = {
            rangeSelector: {
                selected: 1,
                inputEnabled: $('#con').width() > 480
            },

            title: {
                text: 'AAPL Stock Price'
            },

            series: [{
                name: 'AAPL',
                data: data,
                tooltip: {
                    valueDecimals: 2
                }
            }]

            ,

            chart: {
                renderTo: 'con'
            }

        };

         var chart = new Highcharts.stockChart(dataObject);
    });
    });
