function graph(days) {
  // var days = 7;
  $.getJSON($SCRIPT_ROOT + '/_cpu_benchmark/' + days, function(data) {
    console.log(data.owners);

    for (let key in data.owners){
        if(data.owners.hasOwnProperty(key)){
         console.log(`${key} : ${data.owners[key]}`)
         console.log(`${key}`)
     }
   }

    Highcharts.stockChart('cpu_benchmark', {
    title: { text: data.title, style: { color: '#ffffff' } },
    exporting: { enabled: true, },
    legend: { enabled: true },
    navigator: { enabled: true },
    rangeSelector: { enabled: false },

    xAxis: { type: 'datetime' },

    yAxis: [ { opposite: false, title: { text: 'cpu_usage_us' } } ],

    series: [ { name: 'cpu_usage_us', yAxis: 0, data: data.cpu_usage_us, tooltip: { valueDecimals: 0 }, visible: true }, 
              { name: 'josiendotnet', yAxis: 0, data: data.josiendotnet, tooltip: { valueDecimals: 0 }, visible: true } ]
    });
  });
};
