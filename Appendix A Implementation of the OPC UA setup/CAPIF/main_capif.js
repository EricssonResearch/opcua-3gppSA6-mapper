// © Ericsson AB 2024 - All Rights Reserved. No part of this software may be reproduced in any form without the written permission of the copyright owner.
// Distribution error
// No
//
// Disclaimer
// Controlled by agreement
//
// Change clause
// Controlled by agreement


const { rejects } = require("assert");
const http = require("http");
const https = require("https");
const net = require("net");
var fileread = require ('fs');
//const { json } = require("stream/consumers");
const readline = require('readline').createInterface({
                                                        input: process.stdin,
                                                        output: process.stdout,
                                                    });
const { Worker, isMainThread, parentPort, workerData } = require('worker_threads');



//Const variables, like hostname and hostport
const unixpath = "/tmp/capif_pubsub_interval";
const unixpath2 = "/tmp/capif_pubsub_interval_inv";
// const capifhost = "127.0.0.1"/*"10.0.0.4"*/;
// const capifport = 8080;
// const local_http_server = "127.0.0.1"/*10.0.0.1*/;
// const local_port = 65535;


var interval = 600;
var published = false;
var authenticated = true;
var exposer_invoker = null;


// function socket_initial_exp_inv(data, worker){
//     var exposer_invoker = true;
//     var sendback = {
//         'origin' : "Main thread",
//         'success' : false
//     };
//     data = data.toString();

//     if (data.includes("CAPIF exposer") || data.includes("CAPIF provider")){
//         exposer_invoker = true;
//         console.log(exposer_invoker);
//         if (exposer_invoker == true) {
//             worker.postMessage(data);
//         }
//     }
//     else if(data.includes("CAPIF invoker")){
//         exposer_invoker = false;
//         if (exposer_invoker==false) {
//             worker.postMessage(data);
//         }
//     }

//     return null;
// }


function socket_handle_data(data, worker, exposer_invoker){
    FIND = 'publishing_interval';
    FIND2 = 'change_publishing_interval';
    var sendback = {
        'origin' : "Main thread",
        'success' : false
    };
    data = data.toString();
    //console.log(data);

    // No provider/invoker yet
    if (exposer_invoker == null) {
            //Wrong value for exposer_invoker
            //Empty because the default value is null.
            console.log("Message received, but role is not known.");
            console.log(data);    
    } 
    // Provider
    else if (exposer_invoker == true) {
        var resp;
        try {
            resp = data.parse();
        } catch (error) {
            resp = data;
        }
        // From Provider
        if (resp.origin == "OPCUA") {
            if (resp.includes(FIND) && resp.includes('set_publishing_interval') == false){
                if (resp.includes('success')){
                    if (resp['success']  ? "true" : "false") {
                        if (resp.includes['reason']  && resp.reason == "SAME INTERVAL AS SET LAST") {
                            sendback['success'] = true;
                            sendback['notice'] = "NO CHANGE";
                        } else {
                            sendback['success'] = true;
                        }
                    } else {
                        sendback['success'] = false;
                        sendback['reason'] = resp.reason;
                    }
                } else {
                    sendback['publish'] = true;
                }
                sendback['publishing_interval'] = resp['publishing_interval'];
            } else {
                console.log(sendback['reason'].toString());
                sendback['success'] = false;
                sendback['reason'] = resp['reason'];
            }
        } else {
            sendback['success'] = false;
            sendback['reason'] = "Wrong origin for response.";
            console.log(resp.toString())
        }
        worker.postMessage(sendback.toString());
    }
    // Invoker
    else if (exposer_invoker == false) {
        var resp;
        try {
            resp = data.parse();
        } catch (error) {
            resp = data;
        }
        if (resp.origin == "OPCUA") {
            // From Invoker
            if (resp.includes(FIND2) && resp.includes(FIND) == false){
                var interval = resp[FIND2];
                if (interval >= 50 && interval <= 60000) {
                    sendback['success'] = true;
                    sendback[FIND2] = interval;
                }
                else if (interval < 50){
                    sendback['success'] = true;
                    sendback[FIND2] = 50;
                }
                else {
                    sendback['success'] = true;
                    sendback[FIND2] = 60000;
                }
            } else {
                console.log(sendback['reason'].toString());
                sendback['success'] = false;
                sendback['reason'] = sendback['reason'];
            }
            worker.postMessage(sendback.toString());
        }
        
    } 
    
        
    
}

function recieved_api(data, unixserver, worker){
    FIND = 'publishing_interval';
    var sendback = {
        'origin' : "Main thread",
        'success' : false
    };
    if (data.includes(FIND)){
        try {
            var value = data[FIND];
        } catch (error) {
            // console.log(error);
            // console.log(error.toString())
            sendback['success'] = false;
            sendback["reason"] = "Wrong type, can't convert to int.";
        } finally {
            sendback['success'] = true;
            var data2 = {
                'publishing_interval' : value
            }
            unixserver.write(data2.toString());
        }
    }
    else {
        sendback['success'] = false;
        sendback["reason"] = "No attribute: "+FIND+", or wrong origin.";
        console.log("API req doesn't contain published internal value: "+FIND);
        worker.postMessage(sendback.toString());
    }   
}


function change_api(data, unixserver, worker){
    FIND = 'change_publishing_interval';
    var sendback = {
        'origin' : "Main thread",
        'success' : false
    };
    if (data.includes(FIND)){
        try {
            var value = data[FIND];
        } catch (error) {
            // console.log(error);
            // console.log(error.toString())
            sendback['success'] = false;
            sendback["reason"] = "Wrong type, can't convert to int.";
        } finally {
            sendback['success'] = true;
            var data2 = {
                'change_publishing_interval' : value
            }
            unixserver.write(data2.toString());
        }
    }
    else {
        sendback['success'] = false;
        sendback["reason"] = "No attribute: "+FIND+", or wrong origin.";
        console.log("API req doesn't contain published internal value for "+FIND);
        console.log(data);
        worker.postMessage(JSON.stringify(sendback));
    }   
}



if (isMainThread) {
    // Remove the socket file if it exists
    if (fileread.existsSync(unixpath)) {
        fileread.unlinkSync(unixpath);
    }
    const worker = new Worker('./http_server_capif_provider.js');
    const worker2 = new Worker('./http_server_capif_invoker.js');
    //const worker3 = new Worker('./script.js');

    const unixserver = net.createServer((socket) => {
        msg_exp_inv = 'CAPIF exposer/invoker';
        console.log(msg_exp_inv);
        socket.write(msg_exp_inv,(err) => {
            if (err) {
                if (err.code === 'EPIPE') {
                    // Handle EPIPE error (socket closed by the other end)
                    console.error('Socket closed by the other end');
                } else {
                    // Handle other write errors
                    console.error(`Unixserver.write() error: ${err.message}`);
                }
            }
        });
        
        socket.on('connection',(s)=>{
            console.log("Client Connected.");
            msg_exp_inv = 'CAPIF exposer/invoker';
            console.log(msg_exp_inv);
            s.write(msg_exp_inv,(err) => {
            if (err) {
                if (err.code === 'EPIPE') {
                    // Handle EPIPE error (socket closed by the other end)
                    console.error('Socket closed by the other end');
                } else {
                    // Handle other write errors
                    console.error('Unixserver.write() error:', err.message);
                }
            }
            });
            console.log('CAPIF invoker/exposer');
    });


        // Handle server errors
        socket.on('error', (err) => {
        console.error(`Error: ${err.message}`);
        });

        // Handle data received from the client
        socket.on('data',(data)=>{
            var exposer_invoker = true;
            var sendback = {
                'origin' : "Main thread",
                'success' : false
            };
            data = data.toString();
            
            //This code is expected to connect to either Provider or exposer
            //In later version could use different sockets for different roles
            if (data.includes("CAPIF exposer") || data.includes("CAPIF provider")){
                exposer_invoker = true;
                console.log(exposer_invoker);
                if (exposer_invoker == true) {
                    worker.postMessage(data);
                    //Terminate not used thread
                    worker2.terminate();
                }
            }
            else if(data.includes("CAPIF invoker")){
                exposer_invoker = false;
                if (exposer_invoker==false) {
                    worker2.postMessage(data);
                    //Terminate not used thread
                    worker.terminate();
                }
            }
            if (exposer_invoker != null) {
                if (exposer_invoker = true) {
                    socket_handle_data(data,worker,exposer_invoker);
                }
                else if (exposer_invoker = false) {
                    socket_handle_data(data,worker2,exposer_invoker);
                }
                
            }
        });
    });




    // Notify user of closing the socket
    unixserver.on('close',()=>{
        console.log("Closing UNIX socket.");
    });
    // Listen on the Unix socket
    unixserver.listen(unixpath, () => {
        console.log(`Server is listening on ${unixpath}`);
    });

    worker.on('message', (data) => {
        //console.log(data.toString());
        console.log(data);
        console.log(data.mode);
        if (data.mode > 0) {
            recieved_api(data,unixserver, worker);
        } else {
            change_api(data,unixserver, worker);
        }
        
    });

    worker.on('error', (err) => {
        console.log("Error: ",err);
    });
    worker.on('exit', (code) => {
        console.log("Worker thread exiting: " + code)
    });
    

    process.on('SIGINT', function() {
        interrupt = true;    
        unixserver.close();
        console.log('Unix socket connection ended.');
        worker.terminate();
        worker2.terminate();
        // if (exposer_invoker) {
        //     kliens.http_delete();
        // }
        // else{
        //     kliens.http_offboard_invoker();
        // }
        process.exit();
    });
    
}