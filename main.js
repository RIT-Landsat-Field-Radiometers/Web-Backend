const express = require('express')
const app = express()
const port = 3000

const mysql = require('mysql')
const connection = mysql.createConnection(
    {
        host: 'localhost',
        user: 'root',
        password: 'msdroot', // not production password, only works for local DB
        database: 'MSD_Backend'
    }
)

connection.connect()

connection.query('SELECT * FROM Radiometers', (err, res, fields) =>
{
    if(err) throw err;
    console.log(res)
})

app.get('/checkin', ((req, res) =>
{
    // send current timestamp
    res.send(Date.now())
}));

app.post('/data', (req, res) =>
{
    let data = req.body

    for(let idx = 0; idx < length(data.Devices.Thermopiles); idx++)
    {
        for(let sample = 0; sample < length(data.Devices.Thermopiles[idx].Readings); sample++)
        {
            data.Devices.Thermopiles[idx].Readings[sample] // push to DB
        }
    }

    for(let idx = 0; idx < length(data.Devices.Enviromental); idx++)
    {
        for(let sample = 0; sample < length(data.Devices.Enviromental[idx].Readings); sample++)
        {
            data.Devices.Enviromental[idx].Readings[sample] // push to DB
        }
    }

    for(let idx = 0; idx < length(data.Devices.Communication); idx++)
    {
        for(let sample = 0; sample < length(data.Devices.Communication[idx].Messages); sample++)
        {
            data.Devices.Communication[idx].Messages[sample] // push to DB
        }
    }




    console.log(req)
    res.send('OK')
})

app.listen(port, () =>
{
    console.log("starting server")
})