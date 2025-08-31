// © Ericsson AB 2024 - All Rights Reserved. No part of this software may be reproduced in any form without the written permission of the copyright owner.
// Distribution error
// No
//
// Disclaimer
// Controlled by agreement
//
// Change clause
// Controlled by agreement


//const { rejects } = require("assert");
const http = require("http");
const https = require("https");
var fileread = require ('fs');
//const { json } = require("stream/consumers");
const readline = require('readline').createInterface({
    input: process.stdin,
    output: process.stdout,
});
const { isMainThread, workerData, parentPort } = require('worker_threads');
const shell = require('shelljs');
const folderPath = './Responses/';
const path = require('path');
const { exec } = require('child_process');
const fs = require('fs');
const Time = new Date();

//Const variables, like hostname and hostport
CAPIFHOST = "127.0.0.1"/*"capifcore"*/;
CAPIFHOST_PORT = 8080;
CAPIF_REGISTER = "127.0.0.1"/*"register"*/;
CAPIF_REG_PORT = 8084;
const local_http_server = "127.0.0.1"/*10.0.0.1*/;
const local_port = 65535;

// Create the folder path in case it doesn't exist
shell.mkdir('-p', folderPath);

//Variables for the exposed internal value and helper variables for checking if the steps are correct
var interval = 600;
var published = false;
var authenticated = true;
var exposer_invoker = true;


var openSSLCommand = ''
if (CAPIFHOST.includes(':')){
  openSSLCommand = `openssl s_client -connect ${CAPIFHOST} | openssl x509 -text > ./Responses/cert_server.pem`;
}
else{
  openSSLCommand = `openssl s_client -connect ${CAPIFHOST}:443 | openssl x509 -text > ./Responses/cert_server.pem`;
}
exec(openSSLCommand, (error, stdout, stderr) => {
  if (error) {
    console.error(`Error generating CSR: ${stderr}`);
  }
});



//////////////////////////////////////////////////////////
class httpclient {
    #capifhost;
    #capif_register;
    #capif_reqister_port;
    #capifport;
    #http_uri;
    #apiserviceid;
    #http_options;
    #http_data;
    #http_resp;
    #exposerid;
    #access_token;
    #ca_crt;
    #exposer_public_key;
    #exposer_crt;
    #exposer_private_key;
    #refresh_token;
    #admin_access_token;
    #username;
    #admin_username;
    #psw;
    #admin_psw;
    #uuid;
    #localServer;
    #localPort;
    #server;
    #ccf_api_onboarding_url;
    #ccf_discover_url;
    #ccf_onboarding_url; //for invoker
    #ccf_publish_url;
    #ccf_security_url;
    #apiProvDomId;
    #registered_info;

    constructor() {
        //read exposer private key from file
        // try {
        //     const data = fileread.readFileSync('Responses/exposer.key'/*,{encoding: 'utf-8'}*/,err => { if (err) {console.log(err.message);} });
        //     //console.log(data);
        //     this.#exposer_private_key = data;
        //   } catch (err) {
        //     console.error(err);
        // }
        // //read ca cert from file
        // try {
        //     const data = fileread.readFileSync('Responses/ca.crt',"utf-8",err => { if (err) {console.log(err.message);} });
        //     this.#ca_crt = data;
        //   } catch (err) {
        //     console.error(err);
        // }
        // try {
        //     const data = fileread.readFileSync('Responses/exposer.crt',"utf-8",err => { if (err) {console.log(err.message);} });
        //     this.#exposer_crt = data;
        //   } catch (err) {
        //     console.error(err);
        // }

        //public key can be baked in, only the private key needs to be hidden
        this.#exposer_public_key = "-----BEGIN CERTIFICATE REQUEST-----\nMIIC0TCCAbkCAQAwgYsxEDAOBgNVBAMMB2V4cG9zZXIxFzAVBgNVBAoMDlRlbGVm\nb25pY2EgSStEMRMwEQYDVQQLDApJbm5vdmF0aW9uMQ8wDQYDVQQHDAZNYWRyaWQx\nDzANBgNVBAgMBk1hZHJpZDELMAkGA1UEBhMCRVMxGjAYBgkqhkiG9w0BCQEWC2lu\nbm9AdGlkLmVzMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAkpJ7FzAI\nkzFYxLKbW54lIsQBNIQz5zQIvRZDFcrO4QLR2jQUps9giBWEDih++47JiBJyM+z1\nWkEh7b+moZhQThj7L9PKgJHRhU1oeHpSE1x/r7479J5F+CFRqFo5v9dC+2zGfP4E\nsSrNfp3MK/KQHsHhMzSt881xAHs+p2/bcM+sd/BlXC4J6E1y6Hk3ogI7kq443fcY\noUHZx9ClUSboOvXa1ZSPVxdCV6xKRraUdAKfhMGn+pYtJDsNp8Gg/BN8NXmYUzl9\ntDhjeuIxr4N38LgW3gRHLNIa8acO9eBctWw9AD20JWzFAXvvmsboBPc2wsOVcsml\ncCbisMRKX4JyKQIDAQABoAAwDQYJKoZIhvcNAQELBQADggEBAIxZ1Sec9ATbqjhi\nRz4rvhX8+myXhyfEw2MQ62jz5tpH4qIVZFtn+cZvU/ULySY10WHaBijGgx8fTaMh\nvjQbc+p3PXmgtnmt1QmoOGjDTFa6vghqpxPLSUjjCUe8yj5y24gkOImY6Cv5rzzQ\nlnTMkNvnGgpDgUeiqWcQNbwwge3zkzp9bVRgogTT+EDxiFnjTTF6iUG80sRtXMGr\nD6sygLsF2zijGGfWoKRo/7aZTQxuCiCixceVFXegMfr+eACkOjV25Kso7hYBoEdP\nkgUf5PNpl5uK3/rmPIrl/TeE0SnGGfCYP7QajE9ELRsBVmVDZJb7ZxUl1A4YydFY\ni0QOM3Y=\n-----END CERTIFICATE REQUEST-----\n";
        this.#capifhost = CAPIFHOST;
        this.#capifport = CAPIFHOST_PORT;
        this.#http_resp = {};
        this.#username = "Provider_new";
        this.#psw = "pass";
        this.#admin_username = "admin";
        this.#admin_psw = "password123";
        this.#localServer =local_http_server;
        this.#localPort = local_port;
        this.#capif_register = CAPIF_REGISTER;
        this.#capif_reqister_port = CAPIF_REG_PORT;
        this.#registered_info = {   
                                    "aef": {"id":"string", "cert":"string", "csr":"string", "key":"string"},
                                    "apf": {"id":"string", "cert":"string", "csr":"string","key":"string"},
                                    "amf": {"id":"string", "cert":"string", "csr":"string","key":"string"}
                                };
        //this.#exposerid = "0b98deaa9330bc";
    }
    print_all_inner(){
        console.log("\n\n");
        console.log("\nURL: "+this.#http_uri);
        console.log("\nAPI service ID: "+this.#apiserviceid);
        console.log("\nHTTP OPS"+JSON.stringify(this.#http_options));
        console.log("\nHTTP REQ DATA: "+JSON.stringify(this.#http_data));
        console.log("\nHTTP Resp: "+JSON.stringify(this.#http_resp));
        console.log("\nExposer ID: "+this.#exposerid);
        console.log("\nAcces Token: "+this.#access_token);
    }
    httpdata(){
        return this.#http_data;
    }
    exposer_id(){
        return this.#exposerid;
    }
    apiservice_id(){
        return this.#apiserviceid;
    }
    httpresp(){
        return this.#http_resp;
    }
    cacrt(){
        return this.#ca_crt;
    }

    http_uri_set(httpuri){
        this.#http_uri = httpuri;
    }
    http_options_set(httpoptions){
        this.#http_options = httpoptions;
    }
    http_data_set(httpdata){
        this.#http_data = httpdata;
    }

    async handle_https_req(req){
        
        var data;
        try {
            data = JSON.parse(req);
        } catch {
            data = req;
        }
    
        
        if (data != null && data.headers.Authorization != null) {
            if (data.headers.Authorization == "Bearer " + this.#access_token) {
                parentPort.postMessage(data.toString());
                parentPort.on('message', workerData => {
                    //Check if JSON or string format (JSON format is needed of search)
                    try{
                        data = workerData.parse();
                    } catch (error) {
                        data = workerData;
                    }
        
                    if (data.includes('success') && data.success == true && data.includes('orign') && data['origin'] == "Main thread"){
                        return [true,data];
                    } else {
                        if (data.includes('reason')){
                            console.log(data.reason);
                        } else {
                            console.log('Error, but no reason provided.');
                            console.log(data)
                        }
                    }
                });
            } else {
                data = {
                    'success' : false,
                    'reason' : 'Not authorized.'
                }
            }
        }
        console.log("Wrong HTTP request");
        //console.log(req);
        return [false,data];
    }

    http_provider(){
        this.#server = https.createServer(function (req,res) {
            var result, data_return = this.handle_https_req(req.body);
            var data;
            res.writeHead({'Content-Type': "application/json"});
            if (result) {
                data = {};
                if (data_return.includes('reason') == false) {
                    http_update_published_service(req.publishing_interval);
                    res.statusCode(200);
                    data = {'reason': 'Success'};
                }
            } else {
                if (data_return.reason == "Too small, or too big interval."){
                    res.statusCode(200);
                    data = {'reason': data_return.reason};
                }
                else if (data_return.reason == "Missing argument publishing_interval."){
                    res.statusCode(400);
                    data = {'reason': data_return.reason};
                }
                else if (data_return.reason == "Not authorized.") {
                    res.statusCode(300);
                    data = {'reason': data_return.reason};
                }
                else {
                    res.statusCode(500);
                    data = {'reason':'Internal error.'};
                }
            }
            res.write(data);
            res.end();
        }).listen(local_port);
    }


    async https_req2(){ //generic version of https request
        return new Promise( (resolve, error) => {
            var req = https.request(this.#http_uri, this.#http_options, (res) => {
            if (res.statusCode !== 201 && res.statusCode !== 200){
                console.error('Http status code not OK(200/201) :'+res.statusCode);
                console.log(res.message);
                res.resume();
            }
            let data = '';
            res.on('data',(chunk)=>{
                //chunk = JSON.stringify(chunk);
                data += chunk;
            });
            res.on('end',()=>{
                //console.log(data);
                resolve(JSON.parse(data));
            });
            req.on("error", (err) => {
                console.log("Error: "+JSON.stringify(err.message));
                error(err);
            });
            });
            req.write(JSON.stringify(this.#http_data));
            //console.log(req);
            req.end();       
        });
    }
    async https_raw_req(){
        //console.log("HTTP publish 3");
        return new Promise( (resolve, error) => {
            var req = https.request(this.#http_uri, this.#http_options, (res) => {
            if (res.statusCode !== 201 && res.statusCode !== 200){
                console.error('Http status code not OK(200/201) :'+res.statusCode);
                res.resume();
            }
            let data = '';
            res.on('data',(chunk)=>{
                data += chunk;
            });
            res.on('end',()=>{
                resolve(data);
            });
            req.on("error", (err) => {
                console.log("Error: "+err.message);
                error(err);
            });
            });
            req.write(JSON.stringify(this.#http_data));
            //console.log(req);
            req.end();
            //console.log(req);
        });
    }



    async login_admin(){
        var base64encodedData = Buffer.from(this.#admin_username + ":" + this.#admin_psw).toString('base64');
        var https_ops = {
            method: 'POST',
            rejectUnauthorized: false,
            headers: {
                'Authorization': "Basic " + base64encodedData,
            },
            //ca : this.#ca_crt
        };
        this.http_options_set(https_ops);
        var uri = "https://"+this.#capif_register+":"+this.#capif_reqister_port+"/login";
        this.http_uri_set(uri);
        this.http_data_set({});
        
        
        var ret;
        try{
            //this.print_all_inner();
            let resp_body = await this.https_req2();
            console.log("login_admin return: "+JSON.stringify(resp_body));
            if (resp_body != null && resp_body.access_token != null){
                this.#refresh_token = resp_body.refresh_token;
                this.#admin_access_token = resp_body.access_token;
                //console.log(this.#admin_access_token);
            }
            this.#http_resp = resp_body;
            ret = resp_body;
            //console.log(resp_body);
        }
        catch(error) {
            ret = error;
            this.#http_resp = error;
        }
    }

    async creation_of_user(){
        var data = {
                "username" : this.#username,
                "password" : this.#psw,
                "description" : "New user",
                "enterprise" : "ETSI",
                "country" : "Spain",
                "email" : "example@gmail.com",
                "purpose" : "Use OpenCAPIF",
                "phone_number": "+123456789",
                "company_web": "www.etsi.com",
                "description": "UserDescription"  
            }
        var options = {
            method: 'POST',
            rejectUnauthorized: false,
            headers: { 
                'Authorization' : 'Bearer '+this.#admin_access_token,
                'Content-Type':'application/json',
            }        
        }
        console.log(options)
        var uri = "https://"+this.#capif_register+":"+this.#capif_reqister_port+"/createUser";
        this.http_uri_set(uri);
        this.http_data_set(data);
        this.http_options_set(options);
        //this.print_all_inner();
        var ret;
        try{
            let resp_body = await this.https_req2();
            console.log(JSON.stringify(resp_body));
            //console.log("register https_req2 return: "+JSON.stringify(resp_body));
            if (resp_body != null && resp_body.uuid != null){
                this.#uuid = resp_body.uuid;
            }
            this.#http_resp = resp_body;
            ret = resp_body;
        }
        catch(error) {
            ret = error;
            this.#http_resp = error;
        }
    }


    //getauth
    async getauth(){
        var data = {};
        var http_ops = {
            method: 'GET',
            rejectUnauthorized: false,
            headers: { 
                'Authorization' : "Basic "+ Buffer.from(this.#username + ':' + this.#psw).toString('base64'),
                'Content-Type':'application/json',
            }        
        };
        this.http_data_set(data);
        this.http_uri_set("https://"+this.#capif_register+":"+this.#capif_reqister_port+"/getauth");//this.http_uri_set("https://10.0.0.4:8084/getauth");
        this.http_options_set(http_ops);
        
        try{
            let data2 = await this.https_req2();
            let resp_body = await data2;
            if (resp_body != null && resp_body.access_token != null){
                //console.log(resp_body);
                //console.log(resp_body.ca_root);
                // console.log(resp_body.message);
                console.log("__CA_ROOT__");
                this.#access_token = resp_body.access_token;
                this.#ca_crt = resp_body.ca_root;
                this.#ccf_api_onboarding_url = resp_body.ccf_api_onboarding_url;
                this.#ccf_discover_url = resp_body.ccf_discover_url;
                this.#ccf_onboarding_url = resp_body.ccf_onboarding_url;
                this.#ccf_security_url = resp_body.ccf_security_ur;
                this.write_ca(resp_body.ca_root);
            }
            this.#http_resp = resp_body;
        }
        catch(error) {
            this.#http_resp = error;
        }
    }

    //register/onboard   exposer/provider
    async provider_registration(){
        var options = {
            method: 'POST',
            rejectUnauthorized: false,
            headers: {'Authorization': 'Bearer '+this.#access_token,
                'Content-Type': 'application/json'},
        };

        var data = {
            "regSec": this.#access_token,
            "apiProvFuncs": [
              {
                "apiProvFuncId": "AEF_OPC_UA_publishing_int",
                "regInfo": {
                  "apiProvPubKey": "string",
                  "apiProvCert": "string"
                },
                "apiProvFuncRole": "AEF",
                "apiProvFuncInfo": "dummy_aef" //AEF OPC UA publishing interval value.
              },
              {
                "apiProvFuncId": "APF_OPC_UA_publishing_int",
                "regInfo": {
                  "apiProvPubKey": "string",
                  "apiProvCert": "string",
                },
                "apiProvFuncRole": "APF",
                "apiProvFuncInfo": "dummy_apf" //APF OPC UA publishing interval value.
              },
              {
                "apiProvFuncId": "AMF_OPC_UA_publishing_int",
                "regInfo": {
                  "apiProvPubKey": "string",
                  "apiProvCert": "string",
                },
                "apiProvFuncRole": "AMF",
                "apiProvFuncInfo": "dummy_amf" //AMF OPC UA publishing interval value.
              }
            ],
            "apiProvDomInfo": "This is provider",
            "suppFeat": "fff",
            "failReason": "string"
        };

        var data1 = {
            "regSec": this.#access_token,
            "apiProvFuncs": 
              {
                "apiProvFuncId": "OPC_UA_publishing_int",
                "regInfo": {
                  "apiProvPubKey": "string",
                  "apiProvCert": "string"
                },
                "apiProvFuncRole": "AEF",
                "apiProvFuncInfo": "OPC UA publishing interval value."
              }
            ,
            "apiProvDomInfo": "OPC_domain7",
            "suppFeat": "FFF",
            "failReason": "string"
        };
        
        

        // console.log(this.#registered_info);
        // console.log(this.#registered_info["aef"]);
        ////// Generate Keys and CSR
        var res;
        
        try {
            data1.apiProvFuncs.apiProvFuncRole = "AEF";
            res = await this.create_csr(data1);
            data.apiProvFuncs[0].regInfo.apiProvPubKey = res.csr;
            data.apiProvFuncs[0].apiProvFuncRole = data1.apiProvFuncs.apiProvFuncRole;
            this.#registered_info.aef.csr = res.csr;
            this.#registered_info.aef.key = res.key;
        } catch (error) {
            console.log('Error: '+error);
        }
        


        data1.apiProvFuncs.apiProvFuncRole = "APF";
        try {
            res = await this.create_csr(data1);
            data.apiProvFuncs[1].regInfo.apiProvPubKey = res.csr;
            data.apiProvFuncs[1].apiProvFuncRole = data1.apiProvFuncs.apiProvFuncRole;
            this.#registered_info.apf.csr = res.csr;
            this.#registered_info.apf.key = res.key;
        } catch (error) {
            console.log('Error: '+error);
        }


        data1.apiProvFuncs.apiProvFuncRole = "AMF";
        try {
            res = await this.create_csr(data1);
            data.apiProvFuncs[2].regInfo.apiProvPubKey = res.csr;
            data.apiProvFuncs[2].apiProvFuncRole = data1.apiProvFuncs.apiProvFuncRole;
            this.#registered_info.amf.csr = res.csr;
            this.#registered_info.amf.key = res.key;
        } catch (error) {
            console.log('Error: '+error);
        }

        // console.log("\n\n");
        // console.log(this.#registered_info);
        // console.log("\n\n");
        
        this.http_data_set(data);
        this.http_uri_set("https://"+this.#capifhost + "/api-provider-management/v1/registrations"/*"/" + this.#ccf_api_onboarding_url*/);
        this.http_options_set(options);
        try{
            let resp_body = await this.https_req2();
            const roleVariableMapping = {
                'AEF' : { id: 'AEF_ID', cert: 'AEF_CERT' },
                'APF' : { id: 'APF_ID', cert: 'APF_CERT' },
                'AMF' : { id: 'AMF_ID', cert: 'AMF_CERT' },
            }
            console.log("Provider registration response: ")
            console.log(resp_body);
            

            for (let i = 0; i < resp_body.apiProvFuncs.length; i++){
                if (resp_body.apiProvFuncs[i].apiProvFuncRole == "AEF") {
                    this.#registered_info.aef.id = resp_body.apiProvFuncs[i].regInfo.apiProvFuncId;
                    this.#registered_info.aef.cert = resp_body.apiProvFuncs[i].regInfo.apiProvCert;
                    //create aef cert file
                    this.write_cert(resp_body.apiProvFuncs[i].regInfo.apiProvCert,"aef");
                }
                else if (resp_body.apiProvFuncs[i].apiProvFuncRole == "APF") {
                    this.#registered_info.apf.id = resp_body.apiProvFuncs[i].regInfo.apiProvFuncId;
                    this.#registered_info.apf.cert = resp_body.apiProvFuncs[i].regInfo.apiProvCert;
                    //create apf cert file
                    this.write_cert(resp_body.apiProvFuncs[i].regInfo.apiProvCert,"apf");
                }
                else if (resp_body.apiProvFuncs[i].apiProvFuncRole == "AMF") {
                    this.#registered_info.amf.id = resp_body.apiProvFuncs[i].regInfo.apiProvFuncId;
                    this.#registered_info.amf.cert = resp_body.apiProvFuncs[i].regInfo.apiProvCert;
                    //create amf cert file
                    this.write_cert(resp_body.apiProvFuncs[i].regInfo.apiProvCert,"amf");
                }
            }
            this.#http_resp = resp_body;
        }
        catch(error) {
            this.#http_resp = error;
            console.log('Error: '+error);
        }
    }

    async start_provider_https_server(){

        // const options = {
        //     key: this.#registered_info.aef.key,
        //     cert: this.#registered_info.aef.cert,
        // };
        this.#server = http.createServer(/*options,*/ function (req,res) {
           //if (req.headers.Authorization ==  "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6ImZvbyIsInBhc3N3b3JkIjoiYmFyIiwiaWF0IjoxNjY4MDg0NDI1fQ.lT4ABOQSHyJdIiF9rso06qcwrBkIxRFyolIgdBAI4l0") {
                console.log("------------------------")
                console.log(req.headers);
                
                let req_body = '';
                req.on('data', (chunk) => {
                    req_body += chunk;
                });
                req.on('end', () => {
                    req_body = JSON.parse(req_body);
                    console.log(JSON.stringify(req_body));
                    
                    if(req_body.change_publishing_interval != undefined){
                        var start = Date.now()//getSeconds()*1000 + Time.getMilliseconds();
                        var tmp1 = req_body.change_publishing_interval;
                        var tmp = {
                            "change_publishing_interval" : tmp1
                        };
                        
                        if (tmp1 >= 50 && tmp1 <= 60000) {
                            console.log("Received request: " + start + " ms");
    
                            //parentPort.postMessage(tmp.toString());
                            var body = { 
                                "publishing_interval" : tmp1,
                                "success" : true
                            };
                            res.writeHead(200);
                            var sent = Date.now()//getSeconds()*1000 + Time.getMilliseconds();
                            console.log("Sending Response: " + sent + " ms");
                            res.end(JSON.stringify(body));
    
                            sent = Date.now()//getSeconds()*1000 + Time.getMilliseconds();
                            console.log("Sent Repsonse: " + sent + " ms");
                            console.log("Processing time: " + (sent-start) + " ms");
                        } else {
                            res.writeHead(500);
                            var body = {
                                "message":"Bad value"
                            }
                            res.end(JSON.stringify(body));
                        }
    
                    } else {
                        res.writeHead(400);
                        var body = {
                            "reason":"Missing argument"
                        }
                        res.end(JSON.stringify(body));
                    }
                });
               
                
            // } else {
            //     console.log("HTTP request not authorized")
            // }
        }).listen(this.#localPort,() => {
                 console.log("Server started listening");
                });
        // this.#server.listen(this.#localPort, "localhost", () => {
        //     console.log("Server started listening");
        // });
    }



    //For ETSI provided script.js //will be last option to be implemented and tested
    async sign_csr(){
        var options = {
            method: 'POST',
            encoding: 'binary',
            headers: {'Authorization': 'Bearer '+this.#access_token,
                'Content-Type': 'application/json'},
        };
        //options.headers.Authorization = "Bearer "+this.#access_token;
        var data = {
            csr:  this.#exposer_public_key,
            mode:  "client",
            filename: "exposer"
        };

        var data = {
            "regSec": "string",
            "apiProvFuncs": [
              {
                "apiProvFuncId": "string",
                "regInfo": {
                  "apiProvPubKey": "string",
                  "apiProvCert": "string"
                },
                "apiProvFuncRole": "AEF",
                "apiProvFuncInfo": "string"
              }
            ],
            "apiProvDomInfo": "string",
            "suppFeat": "string",
            "failReason": "string"
        };
        
        data.apiProvFuncs.apiProvFuncRole = "AEF";
        data.regSec = this.#access_token;
        data.suppFeat = "fff";
        this.http_data_set(data);
        this.http_uri_set("http://"+"localhost"+":"+6666+"/generate-csr");
        this.http_options_set(options);
        for (let index = 0; index < 3; index++) {
            
            try{
                let resp_body = await this.https_req2();
                this.#registered_info.AEF.key = resp_body.certificate;

                data.apiProvFuncs.apiProvFuncRole = "AMF";                
                this.http_data_set(data);
                resp_body = await this.https_req2();
                this.#registered_info.AMF.key = resp_body.certificate;

                data.apiProvFuncs.apiProvFuncRole = "APF";
                this.http_data_set(data);
                resp_body = await this.https_req2();
                his.#registered_info.APF.key = resp_body.certificate;

                
                console.log(resp_body);
                this.#http_resp = resp_body;
            }
            catch(error) {
                this.#http_resp = error;
                console.log('Error: '+error);
            }
        }
    }

    //Create Public and Private Key for Provider
    async create_csr(prov_reg){
        return new Promise( (resolve, error) => {
           
            var fs = require('fs');
            const csrFilePath = 'Responses/'+prov_reg.apiProvFuncs.apiProvFuncRole+'_csr.pem';
            const privateKeyFilePath = 'Responses/'+prov_reg.apiProvFuncs.apiProvFuncRole+'_key.key';

            fs.writeFileSync('./Responses/client_cert.crt', '');
            fs.writeFileSync('./Responses/client_key.key', '');
        
            const userInfo = {
            country: 'ES',
            state: 'Madrid',
            locality: 'Madrid',
            organization: 'Telefonica I+D',
            organizationalUnit: 'IT Department',
            emailAddress: 'admin@example.com',
            };
    
            const openSSLCommand = `openssl req -newkey rsa:2048 -nodes -keyout ${privateKeyFilePath} -out ${csrFilePath} -subj "/C=${userInfo.country}/ST=${userInfo.state}/L=${userInfo.locality}/O=${userInfo.organization}/OU=${userInfo.organizationalUnit}/emailAddress=${userInfo.emailAddress}"`;
            exec(openSSLCommand, (error, stdout, stderr) => {
                if (error) {
                console.error(`Error generating CSR: ${stderr}`);
                } else {
                console.log(prov_reg.apiProvFuncs.apiProvFuncRole+'CSR generated successfully:');
                fs.readFile(csrFilePath, 'utf8', (readError, csrContent) => {
                    if (readError) {
                    console.error(`Error reading CSR: ${readError}`);
                    res.status(500).send('Error reading CSR');
                    } else {
                    console.log(prov_reg.apiProvFuncs.apiProvFuncRole+'CSR read successfully:');
                    // Send the CSR content in the response
                    fs.readFile(privateKeyFilePath, 'utf8', (readError, keyContent) => {
                        if (readError) {
                        console.error(`Error reading KEY: ${readError}`);
                        res.status(500).send('Error reading KEY');
                        } else {
                        console.log(prov_reg.apiProvFuncs.apiProvFuncRole+'KEY read successfully:');
                        // Send the CSR content in the response
                        fs.unlink(csrFilePath, (err) => {
                            if (err) {
                            console.error(`Error deleting file: ${err.message}`);
                            } 
                        });
                        fs.unlink(privateKeyFilePath, (err) => {
                            if (err) {
                            console.error(`Error deleting file: ${err.message}`);
                            } 
                        });
                        resolve({csr: csrContent, key: keyContent});
                        }
                    });
                    }
                });
                }
            });
        });
    }

    //Create Public and Private Key for Invoker

    // async create_invoker_csr(){
    //     const csrFilePath = 'Responses/invoker_csr.pem';
    //     const privateKeyFilePath = 'Responses/invoker_key.key';
    //     const userInfo = {
    //         country: 'ES',
    //         state: 'Madrid',
    //         locality: 'Madrid',
    //         organization: 'Telefonica I+D',
    //         organizationalUnit: 'IT Department',
    //         emailAddress: 'admin@example.com',
    //     };
    //     const opensslCommand = `openssl req -newkey rsa:2048 -nodes -keyout ${privateKeyFilePath} -out ${csrFilePath} -subj "/C=${userInfo.country}/ST=${userInfo.state}/L=${userInfo.locality}/O=${userInfo.organization}/OU=${userInfo.organizationalUnit}/emailAddress=${userInfo.emailAddress}"`;
        
    //     exec(opensslCommand, (error, stdout, stderr) => {
    //         if (error) {
    //           console.error(`Error generating CSR: ${stderr}`);
    //         } else {
    //           console.log('CSR generated successfully:');
    //           fs.readFile(csrFilePath, 'utf8', (readError, csrContent) => {
    //             if (readError) {
    //               console.error(`Error reading CSR: ${readError}`);
    //               res.status(500).send('Error reading CSR');
    //             } else {
    //               console.log('CSR read successfuly:');
    //               // Send the CSR content in the response
    //               fs.readFile(privateKeyFilePath, 'utf8', (readError, keyContent) => {
    //                 if (readError) {
    //                   console.error(`Error reading KEY: ${readError}`);
    //                   res.status(500).send('Error reading KEY');
    //                 } else {
    //                   console.log('KEY read successfully:');
    //                   // Send the CSR content in the response
    //                   fs.unlink(csrFilePath, (err) => {
    //                     if (err) {
    //                       console.error(`Error deleting file: ${err.message}`);
    //                     } 
    //                   });
    //                   fs.unlink(privateKeyFilePath, (err) => {
    //                     if (err) {
    //                       console.error(`Error deleting file: ${err.message}`);
    //                     } 
    //                   });
    //                   return {csr: csrContent, key: keyContent};
    //                 }
    //               });
    //             }
    //           });
    //         }
    //       });
    // }

    //Store client cert
    async write_cert(cert_data, name = "client"){
        let extension = 'crt',
            fsMode = 'writeFile',
            filename = name+"_cert",
            filePath = `${path.join(folderPath, filename)}.${extension}`,
            options = {encoding: 'binary'};

        fs[fsMode](filePath, cert_data.cert, options, (err) => {
            if (err) {
            console.log(err);
            return false;
            }
        });
        extension = 'key';
        filename = name+"_key";
        filePath = `${path.join(folderPath, filename)}.${extension}`;
        fs[fsMode](filePath, cert_data.key, options, (err) => {
            if (err) {
            console.log(err);
            return false;
            }
            else {
            console.log('Success writing Cert.');
            return true;
            }
        });
    }

    //Store CA cert
    async write_ca(ca_data){
        let extension = 'pem',
            fsMode = 'writeFile',
            filename = "ca_cert",
            filePath = `${path.join(folderPath, filename)}.${extension}`,
            options = {encoding: 'binary'};
        fs[fsMode](filePath, ca_data.ca_root, options, (err) => {
            if (err) {
            console.log("////////////////////////////////////////////////////////////////");
            console.log(err);
            return false;
            }
            else {
            console.log('Success writing CA.');
            return true;
            }
        });
    }

    async https_publish_service(interval){
        this.#http_options.localPort = local_port;
        this.#http_options.localServer = local_http_server;
        var options = {
            rejectUnauthorized: false,
            method: "POST",
            cert: this.#exposer_crt,
            key: this.#exposer_private_key,
            cacert: this.#ca_crt,
            headers: 'Content-Type: application/json'
        }
        var data = {
            apiName: "service_1",
            aefProfiles: [
            {
                aefId: "capif_api_publish_service-1",
                versions: [
                {
                    apiVersion: "v1",
                    expiry: "2025-11-30T10:32:02.004Z",
                    resources: [
                        {
                            resourceName: "publishing_interval",
                            commType: "REQUEST_RESPONSE",
                            uri: "string",
                            custOpName: "change_interval",
                            operations: [
                            "GET",
                            "PUT"
                            ],
                            description: "Publishing interval of OPC UA publisher"
                        }
                    ],
                    custOperations: [
                        {
                            commType: "REQUEST_RESPONSE",
                            custOpName: "change_interval",
                            operations: [
                            "GET",
                            "PUT"
                            ],
                            description: "Change publishing interval of OPC UA publisher"
                        }
                    ]
                }
                ],
                protocol: "HTTP_1_1",
                dataFormat: "JSON",
                securityMethods: ["PSK"],
                interfaceDescriptions: [
                    {
                        ipv4Addr: this.#localServer,
                        port: this.#localPort,
                        securityMethods: ["PSK"]
                    },
                    {
                        ipv4Addr: this.#localServer,
                        port: this.#localPort,
                        securityMethods: ["PSK"]
                    }
                ]
            }
            ],
            description: "string",
            supportedFeatures: "fffff",
            shareableInfo: {
                isShareable: true,
                capifProvDoms: ["string"]
                },
            serviceAPICategory: "string",
            apiSuppFeats: "fffff",
            pubApiPath: {
                ccfIds: ["ccfid"]
                },
            ccfId: "ccfid"
        };
        
        //console.log(options);
        this.http_options_set(options);
        this.http_data_set(data);
        //this.http_uri_set("https://10.0.0.4/published-apis/v1/"+ this.#exposerid /*"0b98deaa9330bc"*/ +"/service-apis");
        this.http_uri_set("http://"+this.#capifhost+"/published-apis/v1/"+this.#exposerid + "/service-apis");
        try {
            let resp_body = await this.https_raw_req();
            this.#http_resp = resp_body;
            this.#apiserviceid = this.#http_resp.apiId;
            //published = true;
            //console.log("apiID: "+this.#apiserviceid);
            console.log(resp_body);
        }
        catch(error) {
            this.#http_resp = error;
            published = false;
        }
    }

    //add in file management: exposer.crt, exposer.key and ca.crt
    async https_update_published_service(interval){
        var options = {
            method: "PUT",
            cert: this.#exposer_crt,
            key: this.#exposer_private_key,
            cacert: this.#ca_crt,
            headers: 'Content-Type: application/json'
        }
        data = {
            apiName: "3gpp-monitoring-event",
            aefProfiles: [
            {
                aefId: "aefId",
                versions: [
                {
                    apiVersion: "v1",
                    expiry: "2024-11-30T10:32:02.004Z",
                    resources: [
                        {
                            resourceName: "publishing_interval",
                            commType: "REQUEST_RESPONSE",
                            uri: "string",
                            custOpName: "change_interval",
                            operations: [
                            "GET",
                            "PUT"
                            ],
                            description: "Publishing interval of OPC UA publisher"
                        }
                    ],
                    custOperations: [
                        {
                            commType: "REQUEST_RESPONSE",
                            custOpName: "change_interval",
                            operations: [
                            "GET",
                            "PUT"
                            ],
                            description: "Change publishing interval of OPC UA publisher"
                        }
                    ]
                }
                ],
                protocol: "HTTP_1_1",
                dataFormat: "JSON",
                securityMethods: ["PSK"],
                interfaceDescriptions: [
                    {
                        ipv4Addr: "127.0.0.1",
                        port: 65535,
                        securityMethods: ["PSK"]
                    },
                    {
                        ipv4Addr: "127.0.0.1",
                        port: 65535,
                        securityMethods: ["PSK"]
                    }
                ]
            }
            ],
            description: "string",
            supportedFeatures: "fffff",
            shareableInfo: {
                isShareable: true,
                capifProvDoms: ["string"]
                },
            serviceAPICategory: "string",
            apiSuppFeats: "fffff",
            pubApiPath: {
                ccfIds: ["ccfid"]
                },
            ccfId: "ccfid"
        };

        this.http_options_set(options);
        this.http_data_set(data);
        //this.http_uri_set("https://10.0.0.4/published-apis/v1/"+this.#exposerid+"/service-apis/"+this.#apiserviceid);
        this.http_uri_set("https://"+this.#capifhost+"/published-apis/v1/"+this.#exposerid+"/service-apis/"+this.#apiserviceid);
        try {
            let resp_body = await this.https_raw_req();
            //console.log("register https_raw_req return: "+JSON.stringify(resp_body));
            this.#ca_crt = resp_body;
            this.#http_resp = resp_body;
        }
        catch(error) {
            this.#http_resp = error;
        }
    }


    //add in file management: exposer.crt, exposer.key and ca.crt
    http_delete(/*exposerid,apiserviceid*/){
        this.#http_options = {
            protocol: "https:",
            host: capifhost,
            path: "/published-apis/v1/"+this.#exposerid+"/service-apis",
            method: "GET"
        }
        this.https_2();

        this.#http_options = {
            protocol: "https:",
            host: capifhost,
            path: "/published-apis/v1/"+this.#exposerid+"/service-apis/"+this.#apiserviceid,
            method: "GET"
        }
        this.https_2();

        this.#http_options = {
            protocol: "https:",
            host: capifhost,
            path: "/published-apis/v1/"+this.#exposerid+"/service-apis/"+this.#apiserviceid,
            method: "DELETE"
        }
        this.https_2();
    }


    //offboard invoker
    http_offboard_invoker(){
        return;
    }
}
//////////////////////////////////////////////////////////


function exposer_provider(kliens){
    exposer_invoker = true;
        //Provider
        if (exposer_invoker == true) {
            (async function (){
                //CAPIF admin registrate customer
                console.log("login");
                await kliens.login_admin();
                console.log("user creation");
                await kliens.creation_of_user();
                //Create Authentication cert/key and send it to CAPIF Core server
                console.log("Get Authentication, CA cert included");
                await kliens.getauth();
                //Customer registrate provider(s)
                console.log("Provider registration");
                await kliens.provider_registration();
                //Start server that receives requests from CAPIF using published API(s)
                authenticated = true;
                console.log("Starting HTTP server");
                kliens.start_provider_https_server();
            })();
        }
        //Invoker 
        else {
            (async function (){
                //CAPIF admin registrate customer
                console.log("login");
                await kliens.login_admin();
                console.log("user creation");
                await kliens.creation_of_user();
                //Customer registrate provider(s)
                console.log("Get Authentication, CA cert included");
                await kliens.getauth();
                //console.log("Provider registration");
                //await kliens.provider_registration();
                authenticated = true;
                console.log("Starting HTTP server");
                kliens.start_provider_https_server();
            })();
        }
}

function invoker(kliens){
    exposer_invoker = false;
    if (exposer_invoker==false) {
        (async function (){
            //CAPIF admin registrate customer
            console.log("login");
            await kliens.login_admin();
            console.log("user creation");
            await kliens.creation_of_user();
            //Customer registrate invoker(s)
            console.log("Get Authentication, CA cert included");
            await kliens.getauth();
            await kliens.onboard_invoker();
            // await kliens.invoker_discover_AEF();
            // await kliens.invoker_create_sec_cont();
            // await kliens.invoker_get_token();
            authenticated = true;
        })();
    }
}

function publish_service(data2, kliens){
    var data;
    try {
        data = JSON.parse(data2);
    } catch (error) { 
        //console.log(error);
        data = data2
    } 
    if ((data.publishing_interval != null) && (published == false) && exposer_invoker && authenticated)
        {
            console.log("HTTP publish");
            pub_interval = data.publishing_interval;
            if (pub_interval>50){
                console.log("HTTP service API publish");
                (async function (){
                    //await kliens.https_publish_service(pub_interval); 
                    //uncomment, when the api publishing is successful
                    published = true;})
            }
        }
        else if ((data.publishing_interval != null) && published && exposer_invoker && authenticated)
        {
            pub_interval = data.publishing_interval;
            if (pub_interval>50){
                console.log("HTTP service API update");
                //kliens.https_update_published_service(pub_interval);
                //kliens.invoker_call_service();
            }
        }
        else {
            console.log("Error: Wrong data!\nData: ");
            console.log(data);
        }
}

function invoke_service(data2, kliens){
    var data;
    try {
        data = JSON.parse(data2);
    } catch (error) { 
        //console.log(error);
        data = data2
    } 
    if ((data.change_publishing_interval != null) && exposer_invoker == false && authenticated) {
            console.log("HTTP publish");
            pub_interval = data.change_publishing_interval;
            if (pub_interval>50){
                console.log("HTTP service API publish");
                (async function (){
                    await kliens.Inv_http_update_published_service(pub_interval); 
                })
            }
    }
}


function handle_parent_message(data, kliens){
    //console.log(data);
    if (data.includes("CAPIF exposer") || data.includes("CAPIF provider")){
        exposer_provider(kliens);
    }
    else if(data.includes("CAPIF invoker")){
        invoker(kliens);
    }
    else if (exposer_invoker == true){ //Service Provider - server
        publish_service({"publishing_interval" : data.publishing_interval}, kliens);
    }
    else if (exposer_invoker == false){ //Service Invoker - user
        invoke_service( {"change_publishing_interval" : data.change_publishing_interval}, kliens);
    }
}



if (!isMainThread) {

    // create http client that can work as CAPIF exposer or CAPIF invoker
    const kliens = new httpclient;
    
    parentPort.on("message", workerData => {
        var data = workerData.toString();
            //console.log(data.publishing_interval);
        handle_parent_message(data, kliens); 
    });

    process.on('SIGINT', function() {
        interrupt = true;
        if (exposer_invoker) {
            kliens.http_delete();
        }
        else{
            kliens.http_offboard_invoker();
        }
    });
}