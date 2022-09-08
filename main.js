let protobuf = require("protobufjs");

var bodyParser = require('body-parser')
const zlib = require('zlib');
const express = require('express')
const app = express()
const port = 3000

let fse = require('fs-extra');
const { start } = require("repl");
/*
let mysql = require('mysql2')
const connection = mysql.createConnection(
    {
        host: 'localhost',
        user: 'develop',
        password: 'dirsroot', // not production password, only works for local DB
        database: 'MSD_Backend'
    }
)

connection.connect((err =>
{
    if (err) throw err;
}))
*/
// connection.query('SELECT * FROM Radiometers', (err, res, fields) =>
// {
//     if (err) throw err;
//     console.log(res)
// })

let root = protobuf.loadSync('./hourly.proto');
let HourlyDataMessage = root.lookupType("HourlyData");




app.use(bodyParser.raw(
    {
        inflate: true,
        limit: '20mb',
        type: 'application/octet-stream'
    }))

app.get('/utcnow', (req, res) =>
{
    console.log((new Date()).toUTCString());
    res.status(200).send("" + Math.floor(Date.now() / 1000));
//    res.status(200).send("1644623640");   // Feb 10 5:56:00 
//    res.status(200).send("1638748200"); // Dec 5 11:50:00 
//    res.status(200).send("1638748770"); // Dec 5 11:59:30

})


app.post('/radiometers/:radiometerID', (req, res) =>
{
    console.log(req.params.radiometerID)

    zlib.gunzip(req.body, (err, outbuf) =>
    {
        if (err)
        {
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
        
        let msg = HourlyDataMessage.decode(outbuf)

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

        // create variables for zero-padding
        let fileYear = startTime.getUTCFullYear();
        let fileMonth = (startTime.getUTCMonth() + 1);
        let fileDay = startTime.getUTCDate();
        let fileHour = startTime.getUTCHours();
        // zero-pad the time variables
        // let paddedYear = fileYear.toString().padStart(5, '0');  // likely won't need to pad the year for our implementation
        let paddedMonth = fileMonth.toString().padStart(2, '0');   // month is always 2 digits
        let paddedDay = fileDay.toString().padStart(2, '0');       // day is always 2 digits
        let paddedHour = fileHour.toString().padStart(2, '0');     // hour is always 2 digits

        // original implementation below; no padding
        // let path = './data/radiometer' + req.params.radiometerID + "/" + startTime.getUTCFullYear() + "/" + (startTime.getUTCMonth() + 1) + "/" + startTime.getUTCDate() + "/h" + "0" + startTime.getUTCHours() + ".rpb";
        // padded implementation below
        let path = './data/radiometer' + req.params.radiometerID + "/" + fileYear + "/" + paddedMonth + "/" + paddedDay + "/h" + paddedHour + ".rpb";


        fse.outputFile(path, outbuf, (err) =>
	    {
		if (err)
		    console.log(err)
		else
		    console.log("Saved raw sensor data")
	    });


        console.log(startTime.toUTCString())
        // original implementation below; no padding
        // path = './data/radiometer' + req.params.radiometerID + "/" + startTime.getUTCFullYear() + "/" + (startTime.getUTCMonth() + 1) + "/" + startTime.getUTCDate() + "/h" + "0" + startTime.getUTCHours() + ".json";
        // padded implementation below
        path = './data/radiometer' + req.params.radiometerID + "/" + fileYear + "/" + paddedMonth + "/" + paddedDay + "/h" +  paddedHour + ".json";
        fse.outputFile(path, JSON.stringify(msg.toJSON() ), (err) =>
        {
            if (err)
                console.log(err)
            else
                console.log("Saved sensor data")
        });
/*
        let serialNums = [msg.commsSerial, msg.bmeBoard.serialNumber]
        for (const sen of msg.sensors)
        {
            serialNums.push(sen.serialNumber)
        }


        const query = "SELECT * FROM Radiometer_Configs WHERE device_fk IN (" + serialNums.join(', ') + ");"
        console.log(query)


        connection.query(query, (err, res, fields) =>
        {
            if (err) throw err;
            console.log(res)
            if(res.length !== serialNums.length)
            {
                console.log("Unknown Device in system, refusing to process");
                return;
            }
            let radNum = res[0].radiometer_fk;
            for(const row of res)
            {
                if(row.radiometer_fk !== radNum)
                {
                    console.log("Device not registered to that radiometer, refusing to process");
                    return;
                }
            }
        })
*/

    })


    // let msg2 = messages.HourlyData.deserializeBinary(req.body)
    //
    // let sensors = msg2.getSensorsList()
    // let sensor0 = sensors[0]
    //
    // console.log(sensor0)
    //
    // let chan0 = sensor0.getChannelsList()[0].getValuesList()
    //
    // console.log(chan0)
    res.code = 200
    res.send()
});

app.listen(port, () =>
{
    console.log("server started")
})


// fs.readFile("/media/reedt/XTRM-Q/Data/CLionProjects/compressionTester/data/hourly.pb", (err, data) =>
// {
//     if(err) throw err;
//     // console.log(data);
//     let msg2 = messages.HourlyData.deserializeBinary(data)
//
//     let sensors = msg2.getSensorsList()
//     let sensor0 = sensors[0]
//
//     console.log(sensor0)
//
//     let chan0 = sensor0.getChannelsList()[0].getValuesList()
//
//     console.log(chan0)
// })

// msg.deserializeBinary()

// msg.setYear(2021)

