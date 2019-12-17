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


$(document).ready(function(owner) {
    var owner = 'josiendotnet';
    $('#josiendotnet').DataTable( {
        "ajax": "/_get_account/" + owner,
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
            if(data.klass) { $(row).addClass(data.klass); }
            // $(row).find('td').attr('data-sort', data.total_votes)
            },
         "columnDefs": [ { "targets": [ 3 ],
                           "visible": true } ],
         "columns": [ { "data": "position" },
                      { "data": "owner" },
                      { "data": "total_votes" },
                      { "data": "staked" },
                      { "data": "social" },
                      { "data": "url" },
                      { "data": "votes" },
                      { "data": "last_work_done" },
                      { "data": "bp_json" },
                    ],
         "order": [ [0, "asc"] ],
         "searching": true,
         "paging": false,
         "info": false,
         "dom": '<"toolbar">frtip'
    });
    $("div.toolbar").html('<h4>Block Producers</h4>');
    setInterval(function() {
      $('#listproducers').DataTable().ajax.reload(null, false);
  }, 6000);
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

