const express = require('express');
const path = require('path');
const consola = require('consola');
const spawn = require('child_process').spawn;
const cors = require('cors');
const sqlite3 = require("sqlite3").verbose();

const app = express();

let datastring = "";
var whitelist = [
    'http://localhost:3001',
    'http://localhost:8080',
    'http://192.168.91.20'
];
//app.use(express.static(path.join(__dirname +'/files')));
var corsOptions = {
  origin: function(origin, callback){
      var originIsWhitelisted = whitelist.indexOf(origin) !== -1;
      callback(null, originIsWhitelisted);
  },
  credentials: true
};

app.use(cors(corsOptions));

app.get('/',(req,res)=>{
    res.set('Access-Control-Allow-Origin', '*');
    res.set('Access-Control-Allow-Credentials', 'false');
    datastring = '';
    let py = spawn('python3',[path.join(__dirname+'/csv_parser.py')]);
    let r = {
        "req": "update",
    }
    py.stdin.write(JSON.stringify(r));
    py.stdin.end();
    py.stderr.on('data', function (data){
    datastring += data.toString();
    });
    py.stdout.on('data', (data)=>{
        datastring += data.toString();
          });
    py.stdout.on('end', ()=>{
        res.send(datastring);
        datastring = '';
    });

    });

app.get('/select',(req,res)=>{
    res.set('Access-Control-Allow-Origin', '*');
    res.set('Access-Control-Allow-Credentials', 'false');
    datastring = '';
    let py = spawn('python3',[path.join(__dirname+'/csv_parser.py')]);
    let r = { 
        "req": "select",
        "time": req.query.time,
        "date": req.query.date,
    }
    console.log(r)
    py.stdin.write(JSON.stringify(r));
    py.stdin.end();
    py.stderr.on('data', function (data){
    datastring += data.toString();
    });
    py.stdout.on('data', (data)=>{
        datastring += data.toString();
          });
    py.stdout.on('end', ()=>{
        console.log(datastring)
        res.send(datastring);
        datastring = '';
    });
});

app.get('/update',(req,res)=>{
    res.set('Access-Control-Allow-Origin', '*');
    res.set('Access-Control-Allow-Credentials', 'false');
    let py = spawn('python3',[path.join(__dirname+'/csv_parser.py')]);
    let r = { 
        "req": "update",
        "date": req.query.date,
        "hour": req.query.hour
    }
    console.log(r)
    py.stdin.write(JSON.stringify(r));
    py.stdin.end();

    py.stderr.on('data', function (data){
    datastring += data.toString();
    });
    py.stdout.on('data', (data)=>{
        datastring += data.toString();
          });
    py.stdout.on('end', ()=>{
        console.log(datastring);
        res.send(datastring);
        datastring = '';
    });
    });

async function start () {
  const port = 3001;

  // Listen the server
  app.listen(port)
  consola.ready({
    message: `Server listening on port ${port}`,
    badge: true
  })
}
start()
