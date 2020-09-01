const express = require('express')
const path = require('path')
const consola = require('consola')
const spawn = require('child_process').spawn;
const cors = require('cors')
const app = express()

let datastring = '';
var url = "mongodb://localhost:27017/";
// Import and Set Nuxt.js options

var whitelist = [
  'https://www.estadistikaph.com'
];
var corsOptions = {
  origin: function(origin, callback){
      var originIsWhitelisted = whitelist.indexOf(origin) !== -1;
      callback(null, originIsWhitelisted);
  },
  credentials: true
};

app.use(cors(corsOptions));

app.get('/search',(req,res)=>{
  res.set('Access-Control-Allow-Origin', '*')
  res.set('Access-Control-Allow-Credentials', 'false')
          let py = spawn('python3',[path.join(__dirname+'/suertres.py')]);
          py.stdin.write(JSON.stringify(result));
          py.stdin.end();
          py.stderr.on('data', function (data){
            datastring += data.toString();
          });
          py.stdout.on('data', (data)=>{
            datastring += data.toString();
          });
          
          py.stdout.on('end', ()=>{
              console.log(datastring);
              res.send(JSON.stringify(datastring));
              datastring = '';
          });
    });
app.get('/search',(req,res)=>{
  res.set('Access-Control-Allow-Origin', '*')
  res.set('Access-Control-Allow-Credentials', 'false')
          let py = spawn('python3',[path.join(__dirname+'/suertres.py')]);
          py.stdin.write(JSON.stringify(result));
          py.stdin.end();
          py.stderr.on('data', function (data){
            datastring += data.toString();
          });
          py.stdout.on('data', (data)=>{
            datastring += data.toString();
          });
          
          py.stdout.on('end', ()=>{
              console.log(datastring);
              res.send(JSON.stringify(datastring));
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
