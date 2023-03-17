let protobuf = require("protobufjs");

var bodyParser = require('body-parser');
const zlib = require('zlib');
const express = require('express');
const path = require('path');
const app = express();
const port = 80;

let fse = require('fs-extra');
const { start } = require("repl");

let root = protobuf.loadSync('./hourly.proto');
let HourlyDataMessage = root.lookupType("HourlyData");

app.use(express.static(path.join(__dirname, './hourly.pb')));

app.post('/radiometer/:radiometerID', (req, res) =>
	{
		console.log(req.params.radiometerID);
	})

console.log("passed");
