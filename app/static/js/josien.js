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


$(document).ready(function(owner) {
    $('#listvoters').DataTable( {
        "ajax": "/_listvoters",
         "createdRow": function(row, data, index) {
            if(data.klass) { $(row).addClass(data.klass); } },
         "columnDefs": [ { "targets": [ 0 ],
                           "visible": true } ],
        "columns": [ { "data": "owner" },
                     { "data": "staked" },
                     { "data": "last_vote_weight" },
                     { "data": "stake_lock_time" },
                     { "data": "pending_perstake_reward" },
                     { "data": "producers" } 
                   ],
        "order": [ [1, "desc"] ],
        "searching": false,
        "paging": false,
        "info": false,
    });
    setInterval(function() {
      $('#listvoters').DataTable().ajax.reload(null, false);
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
                      { "data": "social" },
                      { "data": "url" },
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
