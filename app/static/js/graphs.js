$(document).ready(function(){
    var days = 10;
    $.getJSON($SCRIPT_ROOT + '/_ohlc/' + days, function(data) {
    Highcharts.stockChart('graph', {
        rangeSelector: {
            selected: 5,
            inputEnabled: false
        },

        title: {
            text: 'REMME rem / usdt'
        },

        series: [{
            type: 'candlestick',
            name: 'REMME Stock Price',
            data: data,
        }]
    });
  });
});
