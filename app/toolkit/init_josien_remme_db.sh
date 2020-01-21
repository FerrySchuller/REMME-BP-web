#!/bin/sh

mongo josien_remme --eval "printjson(db.dropDatabase())"
mongo josien_remme --eval "printjson(db.logs.createIndex( { "time": 1 }, { expireAfterSeconds: 43200 } ))"
mongo josien_remme --eval "printjson(db.trxs.createIndex( { "created_at": 1 }, { expireAfterSeconds: 86400 } ))"
