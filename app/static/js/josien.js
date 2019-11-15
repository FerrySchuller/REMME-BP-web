$(document).ready(function() {
    $('#josiendotnet').DataTable( {
        "ajax": "./_get_account",
         "createdRow": function(row, data, index) {
            if(data.klass) {
                $(row).addClass(data.klass);
            }
                 },
        "columns": [
            { "data": "key" },
            { "data": "value" },
        ],
        "order": [ [1, "desc"] ],
        "searching": false,
        "paging": false,
        "info": false,
    });
    setInterval(function() {
      $('#josiendotnet').DataTable().ajax.reload(null, false);
  }, 3000);
});
