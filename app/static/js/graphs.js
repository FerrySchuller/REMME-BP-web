$(document).ready(function(){
    var days = 10;
    $.getJSON($SCRIPT_ROOT + '/_ohlc/' + days, function(data) {
    // console.log(data);

    // create the chart
    Highcharts.stockChart('con', {

        rangeSelector: {
            selected: 1
        },

        title: {
            text: 'REMME rem / usdt'
        },

        series: [{
            type: 'candlestick',
            name: 'REMME Stock Price',
            data: data,
            dataGrouping: {
                units: [
                    [
                        'week', // unit name
                        [1] // allowed multiples
                    ], [
                        'month',
                        [1, 2, 3, 4, 6]
                    ]
                ]
            }
        }]
    });
  });
});
