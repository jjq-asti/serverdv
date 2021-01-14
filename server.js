"use strict";
const express = require('express');
const path = require('path');
var serveStatic = require('serve-static');
const consola = require('consola');
const spawn = require('child_process').spawn;
const cors = require('cors');
const DB = require('/home/wrt/server/db');
const config = require('/home/wrt/server/config');
const bcrypt = require('bcrypt');
const jwt = require('jsonwebtoken');
const bodyParser = require('body-parser');

const db = new DB("/home/wrt/server/sqlitedb")
const app = express();
const router = express.Router();

router.use(bodyParser.urlencoded({ extended: false }));
router.use(bodyParser.json())

let datastring = "";

const allowCrossDomain = function(req, res, next) {
    res.header('Access-Control-Allow-Origin', '*');
    res.header('Access-Control-Allow-Methods', '*');
    res.header('Access-Control-Allow-Headers', '*');
    next();
}

app.use(allowCrossDomain)

router.post('/register', function(req, res) {
    db.insert([
        req.body.name,
        req.body.email,
        bcrypt.hashSync(req.body.password, 8),
        req.body.is_admin
    ],
    function (err) {
        if (err) return res.status(500).send("There was a problem registering the user.")
        db.selectByEmail(req.body.email, (err,user) => {
            if (err) return res.status(500).send("There was a problem getting user")
            let token = jwt.sign({ id: user.id }, config.secret, {expiresIn: 86400 // expires in 24 hours
            });
            res.status(200).send({ auth: true, token: token, user: user });
        });
    });
});

router.post('/register-admin', function(req, res) {
    console.log(req.body.is_admin)
    db.insertAdmin([
        req.body.name,
        req.body.email,
        bcrypt.hashSync(req.body.password, 8),
        req.body.is_admin
    ],
    function (err) {
        if (err) return res.status(500).send("There was a problem registering the user.")
        db.selectByEmail(req.body.email, (err,user) => {
            if (err) return res.status(500).send("There was a problem getting user")
            let token = jwt.sign({ id: user.id }, config.secret, { expiresIn: 86400 // expires in 24 hours
            });
            res.status(200).send({ auth: true, token: token, user: user });
        });
    });
});

router.post('/login', (req, res) => {
    db.selectByEmail(req.body.name, (err, user) => {
        if (err) return res.status(500).send('Error on the server.');
        if (!user) return res.status(404).send('No user found.');
        let passwordIsValid = bcrypt.compareSync(req.body.password, user.user_pass);
        if (!passwordIsValid) return res.status(401).send({ auth: false, token: null });
        let token = jwt.sign({ id: user.id }, config.secret, { expiresIn: 86400 // expires in 24 hours
        });
        res.status(200).send({ auth: true, token: token, user: user });
    });
})


app.get('/files',(req,res)=>{
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
	"city": req.query.city 
        "time": req.query.time,
        "date": req.query.date,
        "loc": req.query.loc,
	"token": req.query.token,
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
        //res.send(datastring.match(/-?\d+(?:\.\d+)?/g).map(Number));
        res.send(datastring)
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
        "hour": req.query.hour,
        "loc": req.query.loc,
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
  app.use(router)
  const port = 5000;
  // Listen the server
  app.listen(port)
  consola.ready({
    message: `Server listening on port ${port}`,
    badge: true
  })
}
start()
