$( document ).ready(function() {
  $('[data-toggle="tooltip"]').tooltip({
     "html": true,
     "delay": {"show": 0, "hide": 100},
     });
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


$(document).ready(function(owner) {
    $('#listvoters').DataTable( {
        "ajax": "/_listvoters",
         "createdRow": function(row, data, index) {
            if(data.klass) { $(row).addClass(data.klass); } },
         "columnDefs": [ { "targets": [0,2,7,8], "orderable": false } ],
        "columns": [ { "data": "owner" },
                     { "data": "staked" },
                     { "data": "last_vote_weight" },
                     { "data": "last_reassertion_time" },
                     { "data": "stake_lock_time" },
                     { "data": "last_claim_time" },
                     { "data": "pending_perstake_reward" },
                     { "data": "pending_perstake_reward_usd" },
                     { "data": "producers" } 
                   ],
        "order": [ [3, "desc"] ],
        "searching": true,
        "paging": false,
        "info": false,
        "dom": '<"toolbarguardians">frtip'
    });
    $("div.toolbarguardians").html('<h4>Guardians</h4>');
    setInterval(function() {
      $('#listvoters').DataTable().ajax.reload(null, false);
  }, 10000);
});


$(document).ready(function() {

    $('#listproducers').on('mousemove', function () {
      $('[data-toggle="tooltip"]').tooltip({
         "html": true,
         "delay": {"show": 0, "hide": 200},
         "animation": false,
         });
    });


    $('#listproducers').DataTable( {
        "ajax": "./_listproducers",
         "createdRow": function(row, data, index) {
            if(data.klass) { $(row).addClass(data.klass); }
            // $(row).find('td').attr('data-sort', data.total_votes)
            },
         "columnDefs": [ { "targets": [1,2,3,4,5,6,7,8,9], "orderable": false } ],
         "columns": [ { "data": "position" },
                      { "data": "owner" },
                      { "data": "total_votes" },
                      { "data": "voters" },
                      { "data": "social" },
                      { "data": "health" },
                      { "data": "cpu_usage_us" },
                      { "data": "last_work_done" },
                      { "data": "is_active", className: "is_active" },
                      { "data": "bp_json" },
                    ],
         "order": [ [0, "asc"] ],
         "searching": false,
         "paging": false,
         "info": false,
         "dom": '<"toolbarbps">frtip'
    });
    // $("div.toolbarbps").html('<h4>Block Producers health dashboard by josiendotnet (beta version)</h4>');
    setInterval(function() {
      // $('[data-toggle="tooltip"]').tooltip('dispose');
      $('#listproducers').DataTable().ajax.reload(null, false);
  }, 10000);
});


$("#toggle").click(function() {
     cpu_usage.data.datasets.forEach(function(ds) {
    ds.hidden = !ds.hidden;
  });
  cpu_usage.update();
});
