$(document).ready(function() {
    $('#josiendotnet').DataTable( {
        "ajax": "./_get_account",
         "createdRow": function(row, data, index) {
            if(data.klass) { $(row).addClass(data.klass); } },
         "columnDefs": [ { "targets": [ 0 ],
                           "visible": false } ],
        "columns": [ { "data": "position" },
                     { "data": "key" },
                     { "data": "value" } ],
        "order": [ [0, "desc"] ],
        "searching": false,
        "paging": false,
        "info": false,
    });
    setInterval(function() {
      $('#josiendotnet').DataTable().ajax.reload(null, false);
  }, 3000);
});
