const express = require('express')
const path = require('path')
const consola = require('consola')
const spawn = require('child_process').spawn;
const mongoClient = require('mongodb').MongoClient
const { Nuxt, Builder } = require('nuxt')
const cors = require('cors')
const app = express()

let datastring = '';
var url = "mongodb://localhost:27017/";
// Import and Set Nuxt.js options
const config = require('../nuxt.config.js')
config.dev = process.env.NODE_ENV !== 'production'

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
  mongoClient.connect(url, {'useUnifiedTopology': true }, function(err, db) {
      if (err) throw err;
      var dbo = db.db("test");
      let start = new Date(req.query.dateRange[0])
      let end = new Date(req.query.dateRange[1])
      dbo.collection("results").find({
        "COMBINATIONS":req.query.combination,
        "LOTTO GAME":{ $in: req.query.drawTime},
        'DRAW DATE': {$gte: start, $lt: end }
        }).toArray(function(err, result) {
        if (err) throw err;
        if (result.length == 0){
          res.send('<h1 style="text-align:center;">Not Found</h1>');
        }else{
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
        }

        db.close();
       })
      });
    });
    app.get('/find',(req,res)=>{
      res.set('Access-Control-Allow-Origin', '*')
      res.set('Access-Control-Allow-Credentials', 'false')
      mongoClient.connect(url, {'useUnifiedTopology': true }, function(err, db) {
          if (err) throw err;
          var dbo = db.db("test");
          let start = new Date(req.query.dateRange[0])
          let end = new Date(req.query.dateRange[1])
          dbo.collection("results").find({
            "LOTTO GAME":{ $in: req.query.drawTime},
            'DRAW DATE': {$gte: start, $lt: end }
            }).toArray(function(err, result) {
            if (err) {
              res.send('<h1 style="text-align:center;color:red">OOPS! BAD REQUEST!</h1>')
            }else{
              if (result.length == 0){
                res.send('<h1 style="text-align:center;">Not Found</h1>');
              }else{
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
              }
            }
    
            db.close();
           })
          });
        });
        app.get('/latest',(req,res)=>{
          res.set('Access-Control-Allow-Origin', '*')
          res.set('Access-Control-Allow-Credentials', 'false')
          mongoClient.connect(url, {'useUnifiedTopology': true }, function(err, db) {
              if (err) throw err;
              var dbo = db.db("test");
              dbo.collection("results").find({},
                { sort: {"DRAW DATE": -1 }, 
                  limit: 3}).toArray((err, result)=>{
                  if (err) {
                    res.send('<h1 style="text-align:center;">Not Found</h1>');
                  }else {
                    console.log(result);
                    res.send(JSON.stringify(result));
                  }
                });
              })
            });

async function start () {
  // Init Nuxt.js
  const nuxt = new Nuxt(config)

  const { host, port } = nuxt.options.server

  await nuxt.ready()
  // Build only in dev mode
  if (config.dev) {
    const builder = new Builder(nuxt)
    await builder.build()
  }

  // Give nuxt middleware to express
  app.use(nuxt.render)

  // Listen the server
  app.listen(port, host)
  consola.ready({
    message: `Server listening on http://${host}:${port}`,
    badge: true
  })
}
start()