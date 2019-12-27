$(function () {
  $('[data-toggle="tooltip"]').tooltip()
})

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
         "columnDefs": [ { "targets": 4, "type": "num-fmt" } ],
        "columns": [ { "data": "owner" },
                     { "data": "staked" },
                     { "data": "last_vote_weight" },
                     { "data": "stake_lock_time" },
                     { "data": "pending_perstake_reward" },
                     { "data": "pending_perstake_reward_usd" },
                     { "data": "producers" } 
                   ],
        "order": [ [1, "desc"] ],
        "searching": true,
        "paging": false,
        "info": false,
        "dom": '<"toolbarguardians">frtip'
    });
    $("div.toolbarguardians").html('<h4>Guardians</h4>');
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
         "columnDefs": [ { "target": 3, "type": "html" } ],
         "columns": [ { "data": "position" },
                      { "data": "owner" },
                      { "data": "total_votes" },
                      { "data": "voters" },
                      { "data": "social" },
                      { "data": "url" },
                      { "data": "last_work_done" },
                      { "data": "bp_json" },
                    ],
         "order": [ [0, "asc"] ],
         "searching": true,
         "paging": false,
         "info": false,
         "dom": '<"toolbarbps">frtip'
    });
    $("div.toolbarbps").html('<h4>Block Producers</h4>');
    setInterval(function() {
      $('#listproducers').DataTable().ajax.reload(null, false);
  }, 6000);
});
