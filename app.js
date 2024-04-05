var admin = require("firebase-admin");

var serviceAccount = require("/home/pietro/Scrivania2/tirocinio_chiese/credentials.json");

admin.initializeApp({
    credential: admin.credential.cert(serviceAccount),
    databaseURL: "https://floor-tiles-vpc-default-rtdb.europe-west1.firebasedatabase.app"
});

var db = admin.database();
var ref = db.ref("/Chiese");

ref.on("value", function(snapshot) {
    console.log(snapshot.val());
}, function (errorObject) {
    console.log("La lettura dei dati ha fallito: " + errorObject.code);
});