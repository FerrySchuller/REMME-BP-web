$(document).ready(function() {
    $('#remswap').DataTable( {
        "ajax": "./_get_remswap",
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
      $('#remswap').DataTable().ajax.reload(null, false);
  }, 3000);
});


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

$(document).ready(function() {
    $('#listproducers').DataTable( {
        "ajax": "./_listproducers",
         "createdRow": function(row, data, index) {
            if(data.klass) { $(row).addClass(data.klass); } },
         "columnDefs": [ { "targets": [ 0 ],
                           "visible": false } ],
        "columns": [ { "data": "position" },
                     { "data": "owner" },
                     { "data": "total_votes" },
                     { "data": "url" },
                     { "data": "is_active"} ],
        "order": [ [2, "desc"] ],
        "searching": false,
        "paging": false,
        "info": false,
    });
    setInterval(function() {
      $('#listproducers').DataTable().ajax.reload(null, false);
  }, 3000);
});

$(document).ready(function() {
    $('#permissions').DataTable( {
        "ajax": "./_get_permissions",
         "createdRow": function(row, data, index) {
            if(data.klass) { $(row).addClass(data.klass); } },
         "columnDefs": [ { "targets": [ 0 ],
                           "visible": false } ],
        "columns": [ { "data": "position" },
                     { "data": "owner" },
                     { "data": "perm_name" },
                     { "data": "parent" },
                     { "data": "keys"} ],
        "order": [ [1, "desc"] ],
        "searching": true,
        "paging": false,
        "info": false,
    });
    setInterval(function() {
      $('#listproducers').DataTable().ajax.reload(null, false);
  }, 9000);
});

