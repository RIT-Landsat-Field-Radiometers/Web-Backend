/*
    --Main Javascript program for Radiometer server--
    
    This file is responsible for listening to port 3000
    and communicating with the Radiometer Comms Boards.
    
    Authors: Reed Terdal, Austin Martinez, Zachary Steigerwald
*/

/* ---- Include modules required for the rest of the program ---- */
let protobuf = require("protobufjs");       // for parsing the protobuf files
var bodyParser = require('body-parser')     // for parsing the body of incoming requests
const bodyParserErrorHandler = require('express-body-parser-error-handler') // ADDED IN ATTEMPT TO RESOLVE BADREQUESTERROR
const zlib = require('zlib');               // for unzipping the incoming gzip files
const fs = require('fs');                   // for interacting with files
const { exec } = require('child_process')   // for executing python scripts
const express = require('express')          // provides framework for the webapp
const app = express()                       // creates a variable to use express webapp api
const port = 3000                           // radiometers contact the server through port 3000
let fse = require('fs-extra');              // more file system methods
const { start } = require("repl");          // 

// Set variables for decoding our specific protobuf format
let root = protobuf.loadSync('./hourly.proto');
let HourlyDataMessage = root.lookupType("HourlyData");


/* ---- Server Startup ---- */

// This ensures the app listens to port 3000
app.listen(port, () =>
{
    console.log("server started")
})

/* ---- Set up Middlewares for Express.js ---- */
app.use(bodyParser.text()); // for parsing the 404 string from the comms board

app.use(bodyParser.raw(
    {
        inflate: true,
        limit: '20mb',
        type: 'application/octet-stream'
    }))

app.use(bodyParserErrorHandler()) // ADDED IN ATTEMPT TO RESOLVE BADREQUESTERROR

/* ---- GET Requests ---- */

// This endpoint gives the radiometer the current UTC time
app.get('/utcnow', (req, res) =>
{
    console.log((new Date()).toUTCString());    // log the UTC datetime that this endpoint was contacted
    res.status(200).send("" + Math.floor(Date.now() / 1000));   // Send the UTC time back to the Comms board
})

// This endpoint keeps track of when a radiometer is booting up after a reset
app.get('/bootup/:radiometerID', (req, res) =>
{
    const radiometerID = req.params.radiometerID;   // get the radiometer ID from the request
    console.log("radiometer" + radiometerID + " is booting up");
    
    // log the reset time in the radiometer_info.json file for this Radiometer
    resetTime = Math.floor(Date.now()) // get the current UTC time
    resetTime = Math.round(resetTime / 1000)

    exec("python3 ./updateResetTime.py " + resetTime + " " + radiometerID, (err, stdout, stderr) => {
        if (err) {
            // if the script runs into an error, log the error and let the radiometer know
            console.error('Error executing updateResetTime.py:', err);
        } 
        else {
            // if the script runs successfully, log the success
            console.log('Reset time updated')
        }
    });
    
    res.status(200).send('Reset acknowledged'); // let the radiometer know that the message was received
})

// This endpoint gives the radiometer its reset value
app.get('/isResetNeeded/:radiometerID', (req, res) => {
    const radiometerID = 'radiometer' + req.params.radiometerID;        // get the radiometer ID from the request
    console.log(radiometerID + ' is asking if a reset is needed...');   // log a message that this radiometer is requesting this endpoint

    // read the reset variables text file to fetch the reset value for this radiometer
    fs.readFile('./boardErrors/boardResetVariables.txt', 'utf8', (err, data) => {
        if (err) {
            // if the file could not be opened, log the error and let the radiometer know
            console.error('Error reading the boardResetVariables.txt:', err);
            res.status(500).send('An error occurred while reading the boardResetVariables.txt');
        } 
        else 
        {
            // once open, construct a regex to search for this specific radiometer ID and its corresponding reset variable
            const regex = new RegExp('^' + radiometerID + '\\s+(\\d+)', 'm');
            const match = data.match(regex);
            if (match) {
                // if the radiometer ID is found, print the reset value and send it to the radiometer
                const value = match[1];
                console.log(radiometerID + ' reset value: ' + value);
                res.status(200).send(value);
            } 
            else 
            {
                // if the radiometer ID is not found, log the error and let the radiometer know
                console.log(radiometerID + ' not found in boardResetVariables.txt');
                res.status(404).send('Radiometer not found in boardResetVariables.txt');
            }
        }
    });
});

// This endpoint sends a list of files missing from the server to the radiometer
app.get('/getMissingFiles/:radiometerID', (req, res) => 
{
    const radiometerID = req.params.radiometerID;   // get the radiometer ID from the request

    // create the path to this specific radiometer's missing files list
    const missingFilesPath = './getMissingFiles/radiometer' + radiometerID + '_missingHours.txt';
    // log a message that this radiometer is requesting this endpoint
    console.log('radiometer' + radiometerID + ' is querying for missing files...');

    // run the python script getMissingFiles.py to generate the missing files list
    exec('python ./getMissingFiles/getMissingFiles.py', (err, stdout, stderr) => {
        if (err) {
            // if the script runs into an error, log the error and let the radiometer know
            console.error('Error executing getMissingFiles.py:', err);
            res.status(500).send('An error occurred while executing getMissingFiles.py');
        } 
        else {
            // if the script runs successfully, log the success
            console.log('getMissingFiles.py executed successfully');

            // check that the missing files list was created
            if (!fse.existsSync(missingFilesPath)) {
                // if the file wasn't created, let the radiometer know
                res.status(404).send('Missing files list not found for the specified radiometer.');
                return;
            }

            // send the missing files list to the radiometer as a text file
            res.download(missingFilesPath, 'radiometer' + radiometerID + '_missingHours.txt', (err) => {
                if (err) {
                    // if this runs into an error, log the error and let the radiometer know
                    console.error('Error sending the missing files list:', err);
                    res.status(500).send('An error occurred while sending the missing files list.');
                }
                else {
                    // if this runs successfully, log the success
                    console.log('Missing files list sent to radiometer' + radiometerID);
                }
            });
        }
    });
});

app.get('/getRadiometerInfo', (req, res) => 
{
    // send the missing files list to the radiometer as a text file
    res.download('./frontend/radiometer_info.json', (err) => {
        if (err) {
            // if this runs into an error, log the error and let the radiometer know
            // console.error('Error sending the radiometer info:', err);
            res.status(500).send('An error occurred while sending the radiometer info.');
        }
        else {
            // if this runs successfully, log the success
            // console.log('Radiometer info sent to frontend');
        }
    });
});

// This endpoint sends the frontend the data being requested for a specific radiometer
app.get('/getRadiometerData/:radiometerID', (req, res) =>
{

    const radiometerID = "radiometer" + req.params.radiometerID;   // get the radiometer ID from the request
    const startMonth = req.query.startMonth;        //get the start month from the request
    const startDay = req.query.startDay;            //get the start day from the request
    const startYear = req.query.startYear;          //get the start year from the request
    const endMonth = req.query.endMonth;            //get the end month from the request
    const endDay = req.query.endDay;                //get the end day from the request
    const endYear = req.query.endYear;              //get the end year from the request
    console.log('Getting data from s3');
    console.log(startMonth, startDay, startYear);
    console.log(endMonth, endDay, endYear);
    
    // run read-radiometer-data.py to fetch data from requested date range
    exec("python3 ./read-radiometer-data.py " + radiometerID + " " + startYear + " " + startMonth + " " + startDay + " " + endYear + " " + endMonth + " " + endDay, (err, stdout, stderr) => {
        if (err){
            console.error('Error executing fetching data files:', err);
            res.status(500).send('An error occurred while fetching the radiometer data.');
        } else{
            console.log('Radiometer data saved to image');
            res.status(200).send('Radiometer data graphed successfully in backend.');
        }
    });
});

/* ---- POST Requests ---- */

// This endpoint receives the 'Does Not Exist' (DNE) message from the radiometer when a missing file actually doesn't exist
app.post('/DNE/:radiometerID', (req, res) =>
{
    const bodyString = req.body; // parse the body as a string
    const radiometerID = req.params.radiometerID;   // get the radiometer ID from the request

    // extract the filename from the request body
    const regex = /404\s+(.*?)\s+DNE/;
    const match = bodyString.match(regex);
    const filename = match ? match[1] : '';

    // append the filename to the radiometer's DNE list
    fs.appendFile('./getMissingFiles/radiometer' + radiometerID + '_DNE.txt', filename + '\n', (err) => {
        if (err) {
            // if this runs into an error, log the error
            console.error('Error appending to ' + radiometerID + '_DNE.txt:', err);
        } else {
            // if this runs successfully, log the success and let the radiometer know
            console.log('Filepath ' + filename + ' appended to radiometer' + radiometerID + '_DNE.txt');
            res.status(200).send('DNE information recorded successfully.');
        }   
    
    });
});

// This endpoint receives the data files from the radiometer, decodes them, and saves them
app.post('/radiometers/:radiometerID', (req, res) =>
{
    console.log(req.params.radiometerID)    // log the radiometer ID of the radiometer uploading a file
    const radiometerID = req.params.radiometerID;   // get the radiometer ID from the request

    // unzip the incoming .gz file
    zlib.gunzip(req.body, (err, outbuf) =>
    {
        if (err)
        {
            // if the file unzip fails, log the error and place the .gz file into an errors folder
            console.log(err);
            let ts = Date.now();
            let path = './data/radiometer' + req.params.radiometerID + "/errors/" + ts + ".gz";
            fse.outputFile(path, req.body, (err) =>
            {
                if (err)
                    console.log(err)
                else
                    console.log("Saved sensor data")
            });

            return;
        }
        
        // decode the protobuf file
        let msg = HourlyDataMessage.decode(outbuf)

        // decode the start time 
        let startTime = new Date(0);
        if (msg.dataStart.time === "unixTime")
        {
            // use unix time
            startTime.setUTCSeconds(msg.dataStart.unixTime)
        } else if (msg.dataStart.time === "LongVer")
        {
            // use long version
            let long = time.getLongver()
            startTime.setFullYear(long.year, long.month, long.day)
            startTime.setHours(long.hour)
            startTime.setMinutes(long.minute)
            startTime.setSeconds(long.seconds)
        } else
        {
            // Unknown, drop it
            return
        }

        // create variables for zero-padding the start time
        let fileYear = startTime.getUTCFullYear();
        let fileMonth = (startTime.getUTCMonth() + 1);
        let fileDay = startTime.getUTCDate();
        let fileHour = startTime.getUTCHours();
        // zero-pad the time variables
        // let paddedYear = fileYear.toString().padStart(5, '0');  // likely won't need to pad the year for our implementation
        let paddedMonth = fileMonth.toString().padStart(2, '0');   // month is always 2 digits
        let paddedDay = fileDay.toString().padStart(2, '0');       // day is always 2 digits
        let paddedHour = fileHour.toString().padStart(2, '0');     // hour is always 2 digits

        // create file path for the raw protobuf data file
        let path = './data/radiometer' + req.params.radiometerID + "/" + fileYear + "/" + paddedMonth + "/" + paddedDay + "/h" + paddedHour + ".rpb";

        // save the protobuf file in the path
        fse.outputFile(path, outbuf, (err) =>
            {
                if (err)
                    console.log(err)
                else
                    console.log("Saved raw sensor data")
            });

        // log the start time of the decoded file
        console.log(startTime.toUTCString())

        // create the file path for the converted JSON data file
        path = './data/radiometer' + req.params.radiometerID + "/" + fileYear + "/" + paddedMonth + "/" + paddedDay + "/h" +  paddedHour + ".json";
        // convert the protobuf file to JSON for easier manipulation later
        fse.outputFile(path, JSON.stringify(msg.toJSON() ), (err) =>
        {
            if (err)
                console.log(err)
            else
                console.log("Saved sensor data")
        });

    })

    // log the upload time in the radiometer_info.json file for this Radiometer
    uploadTime = Math.floor(Date.now()) // get the current UTC time
    uploadTime = Math.round(uploadTime / 1000)

    exec("python3 ./updateUploadTime.py " + uploadTime + " " + radiometerID, (err, stdout, stderr) => {
        if (err) {
            // if the script runs into an error, log the error and let the radiometer know
            console.error('Error executing updateUploadTime.py:', err);
        } 
        else {
            // if the script runs successfully, log the success
            console.log('Upload time updated')
        }
    });
    

    // let the radiometer know everything went well in receiving that data file
    res.code = 200
    res.send()
});

