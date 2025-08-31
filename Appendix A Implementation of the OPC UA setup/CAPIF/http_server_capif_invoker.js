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
var exposer_invoker = null;


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
class httpclient_invoker {
    #capifhost;
    #capif_register;
    #capif_reqister_port;
    #capifport;
    #http_uri;
    #apiserviceid;
    #http_options;
    #http_data;
    #http_resp;
    #invokerid;
    #access_token;
    #ca_crt;
    #invoker_public_key;
    #invoker_crt;
    #invoker_private_key;
    #refresh_token;
    #admin_access_token;
    #username;
    #admin_username;
    #psw;
    #admin_psw;
    #uuid;
    #server;
    #localServer;
    #localPort;
    #ccf_api_onboarding_url;
    #ccf_discover_url;
    #ccf_onboarding_url; //for invoker
    #ccf_publish_url;
    #ccf_security_url;
    #apiProvDomId;
    #registered_info;
    #api;

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
        this.#invoker_public_key = "-----BEGIN CERTIFICATE REQUEST-----\nMIIC0TCCAbkCAQAwgYsxEDAOBgNVBAMMB2V4cG9zZXIxFzAVBgNVBAoMDlRlbGVm\nb25pY2EgSStEMRMwEQYDVQQLDApJbm5vdmF0aW9uMQ8wDQYDVQQHDAZNYWRyaWQx\nDzANBgNVBAgMBk1hZHJpZDELMAkGA1UEBhMCRVMxGjAYBgkqhkiG9w0BCQEWC2lu\nbm9AdGlkLmVzMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAkpJ7FzAI\nkzFYxLKbW54lIsQBNIQz5zQIvRZDFcrO4QLR2jQUps9giBWEDih++47JiBJyM+z1\nWkEh7b+moZhQThj7L9PKgJHRhU1oeHpSE1x/r7479J5F+CFRqFo5v9dC+2zGfP4E\nsSrNfp3MK/KQHsHhMzSt881xAHs+p2/bcM+sd/BlXC4J6E1y6Hk3ogI7kq443fcY\noUHZx9ClUSboOvXa1ZSPVxdCV6xKRraUdAKfhMGn+pYtJDsNp8Gg/BN8NXmYUzl9\ntDhjeuIxr4N38LgW3gRHLNIa8acO9eBctWw9AD20JWzFAXvvmsboBPc2wsOVcsml\ncCbisMRKX4JyKQIDAQABoAAwDQYJKoZIhvcNAQELBQADggEBAIxZ1Sec9ATbqjhi\nRz4rvhX8+myXhyfEw2MQ62jz5tpH4qIVZFtn+cZvU/ULySY10WHaBijGgx8fTaMh\nvjQbc+p3PXmgtnmt1QmoOGjDTFa6vghqpxPLSUjjCUe8yj5y24gkOImY6Cv5rzzQ\nlnTMkNvnGgpDgUeiqWcQNbwwge3zkzp9bVRgogTT+EDxiFnjTTF6iUG80sRtXMGr\nD6sygLsF2zijGGfWoKRo/7aZTQxuCiCixceVFXegMfr+eACkOjV25Kso7hYBoEdP\nkgUf5PNpl5uK3/rmPIrl/TeE0SnGGfCYP7QajE9ELRsBVmVDZJb7ZxUl1A4YydFY\ni0QOM3Y=\n-----END CERTIFICATE REQUEST-----\n";
        this.#capifhost = CAPIFHOST;
        this.#capifport = CAPIFHOST_PORT;
        this.#http_resp = {};
        this.#username = "Invoker_new";
        this.#psw = "pass";
        this.#admin_username = "admin";
        this.#admin_psw = "password123";
        this.#localServer =local_http_server;
        this.#localPort = local_port;
        this.#capif_register = CAPIF_REGISTER;
        this.#capif_reqister_port = CAPIF_REG_PORT;
    }
    print_all_inner(){
        console.log("\n\n");
        console.log("\nURL: "+this.#http_uri);
        console.log("\nAPI service ID: "+this.#apiserviceid);
        console.log("\nHTTP OPS"+JSON.stringify(this.#http_options));
        console.log("\nHTTP REQ DATA: "+JSON.stringify(this.#http_data));
        console.log("\nHTTP Resp: "+JSON.stringify(this.#http_resp));
        console.log("\nInvoker ID: "+this.#invokerid);
        console.log("\nAcces Token: "+this.#access_token);
    }
    httpdata(){
        return this.#http_data;
    }
    invoker_id(){
        return this.#invokerid;
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

    async http_req2(){ //generic version of https request
        return new Promise( (resolve, error) => {
            var req = http.request(this.#http_uri, this.#http_options, (res) => {
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
                console.log(data);
                resolve(JSON.parse(data));
            });
            req.on("error", (err) => {
                console.log("Error: "+JSON.stringify(err.message));
                error(err);
            });
            });
            console.log("Data to be sent"+JSON.stringify(this.#http_data));
            req.write(JSON.stringify(this.#http_data));
            //console.log(req);
            req.end();       
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


    //Get certificates from CAPIF server
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
                console.log("__CA_ROOT__");
                console.log(resp_body);
                this.#access_token = resp_body.access_token;
                this.#ca_crt = resp_body.ca_root;
                this.#ccf_api_onboarding_url = resp_body.ccf_api_onboarding_url;
                this.#ccf_discover_url = resp_body.ccf_discover_url;
                this.#ccf_onboarding_url = resp_body.ccf_onboarding_url;
                this.#ccf_security_url = resp_body.ccf_security_ur;
                this.write_ca({ca_root: resp_body.ca_root});
            }
            this.#http_resp = resp_body;
        }
        catch(error) {
            this.#http_resp = error;
        }
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
            csr:  this.#invoker_public_key,
            mode:  "client",
            filename: "invoker"
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


    //Create Public and Private Key for Invoker
    async create_invoker_csr(){

        return new Promise( (resolve, error) => {
        const csrFilePath = 'Responses/invoker_csr.pem';
        const privateKeyFilePath = 'Responses/invoker_key.key';
        const userInfo = {
            country: 'ES',
            state: 'Madrid',
            locality: 'Madrid',
            organization: 'Telefonica I+D',
            organizationalUnit: 'IT Department',
            emailAddress: 'admin@example.com',
        };
        const opensslCommand = `openssl req -newkey rsa:2048 -nodes -keyout ${privateKeyFilePath} -out ${csrFilePath} -subj "/C=${userInfo.country}/ST=${userInfo.state}/L=${userInfo.locality}/O=${userInfo.organization}/OU=${userInfo.organizationalUnit}/emailAddress=${userInfo.emailAddress}"`;
        
        exec(opensslCommand, (error, stdout, stderr) => {
            if (error) {
              console.error(`Error generating CSR: ${stderr}`);
            } else {
              console.log('CSR generated successfully:');
              fs.readFile(csrFilePath, 'utf8', (readError, csrContent) => {
                if (readError) {
                  console.error(`Error reading CSR: ${readError}`);
                  res.status(500).send('Error reading CSR');
                } else {
                  console.log('CSR read successfuly:');
                  // Send the CSR content in the response
                  fs.readFile(privateKeyFilePath, 'utf8', (readError, keyContent) => {
                    if (readError) {
                      console.error(`Error reading KEY: ${readError}`);
                      res.status(500).send('Error reading KEY');
                    } else {
                      console.log('KEY read successfully:');
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
                      console.log({csr: csrContent, key: keyContent});
                      resolve({csr: csrContent, key: keyContent});
                    }
                  });
                }
              });
            }
          });
        });
    }

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

    async onboard_invoker(){
        let res = await this.create_invoker_csr();
        this.write_cert( {cert : res.csr , key : res.key }, "invoker");
        this.#invoker_private_key = res.key;
        this.#invoker_public_key = res.csr;
        this.#invoker_crt = fs.readFile(folderPath+"invoker_cert.crt",{encoding : 'binary'},err => { if (err) {console.log(err.message);} });


        
        var options = {
            method: 'POST',
            rejectUnauthorized: false,
            headers: {'Authorization': 'Bearer '+this.#access_token,
                'Content-Type': 'application/json'},
        };
        var data = {
            "notificationDestination": "http://"+local_http_server+":"+local_port+"/netapp_callback", //replace
            "supportedFeatures": "fffffff",
            "apiInvokerInformation": "OPC_UA_TESTING_INVOKER",
            "websockNotifConfig": {
              "requestWebsocketUri": true,
              "websocketUri": "websocketUri"
            },
            "onboardingInformation": {
              "apiInvokerPublicKey": res.csr,
              "onboardingSecret": "onboardingSecret",
              "apiInvokerCertificate": "apiInvokerCertificate" //Will be loaded in the response with the Cert
            },
            "requestTestNotification": true
        }

        this.http_data_set(data);
        this.http_uri_set("https://"+this.#capifhost + "/" + "api-invoker-management/v1/onboardedInvokers"/*this.#ccf_onboarding_url*/);
        this.http_options_set(options);
        try{
            console.log("Invoker registration response: ")
            let resp_body = await this.https_req2();
            //console.log(resp_body);
            
            this.#registered_info = {id : "", cert : ""/*, pubKey: ""*/};
            this.#registered_info.id = resp_body.apiInvokerId;
            this.#registered_info.cert = resp_body.onboardingInformation.apiInvokerCertificate;
            //this.#registered_info.pubKey = resp_body.onboardingInformation.apiInvokerPublicKey;
            this.#invokerid = resp_body.apiInvokerId;
            this.#invoker_crt = resp_body.onboardingInformation.apiInvokerCertificate;
            await this.write_cert(resp_body.onboardingInformation.apiInvokerCertificate,"invoker_csr");

            this.#http_resp = resp_body;
        }
        catch(error) {
            this.#http_resp = error;
            console.log('Error: '+error);
        }
        //console.log(data);
    }


    async invoker_discover_AEF(){
        let filePath = `${path.join(folderPath, "invoker_cert")}.${"crt"}`,
        options = {encoding: 'binary'};

        this.#invoker_crt = fs.readFileSync(filePath,options,err => { if (err) {console.log(err.message);} });
        filePath = `${path.join(folderPath, "ca_cert")}.${"pem"}`;
        this.#ca_crt = fs.readFileSync(filePath,options,err => { if (err) {console.log(err.message);} });

        console.log("----------------------ca_crt.pem---------------------------");
        console.log(this.#ca_crt);

        var data = {};
        var http_ops = {
            method: 'GET',
            rejectUnauthorized: false,
            key: this.#invoker_private_key,
            ca: this.#ca_crt,
            cert: this.#invoker_crt,
            headers: { 
                //'Authorization' : "Basic "+ Buffer.from(this.#username + ':' + this.#psw).toString('base64'),
                'Content-Type':'application/json',
            }        
        };
        this.http_data_set(data);
        this.http_uri_set("https://"+this.#capifhost+"/"+this.#ccf_discover_url + this.#invokerid);  //"https://capifcore/service-apis/v1/allServiceAPIs?api-invoker-id="+InvokerID
        this.http_options_set(http_ops);

        try{
            console.log("Invoker DISCOVER APIs: ")
            let resp_body = await this.https_req2();
            console.log(resp_body);

            this.#http_resp = resp_body;
        }
        catch(error) {
            this.#http_resp = error;
            console.log('Error: '+error);
            console.log(error);
        }
        //console.log(data);

    }

    async call_service(data) {
        var http_ops = {
            method: 'POST',
            rejectUnauthorized: false,
            headers: { 
                'Authorization' : "Bearer "+ "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6ImZvbyIsInBhc3N3b3JkIjoiYmFyIiwiaWF0IjoxNjY4MDg0NDI1fQ.lT4ABOQSHyJdIiF9rso06qcwrBkIxRFyolIgdBAI4l0",
                'Content-Type':'application/json',
            }        
        };
        this.http_data_set(data);
        this.http_uri_set("http://"+this.#capif_register+":"+this.#localPort);
        this.http_options_set(http_ops);
        console.log(data);
        try{
            console.log("Invoker call service: ")
            var start = Date.now();//.getSeconds()*1000 + Time.getMilliseconds();
            console.log("Sent request: "+ (start) + " ms")
            let resp_body = await this.http_req2();
            var end = Date.now();
            console.log("Received Answer: "+ (end) + " ms")
            console.log("Delay: " + (end - start) + " ms")
            console.log(resp_body);
        } catch (error) {
            console.log("error invoking service: " + error);
        }

    }

    async Inv_http_update_published_service(){


    }


    /*offboard invoker*/
    async http_offboard_invoker(){
        return;
    }
}
//////////////////////////////////////////////////////////


function invoker(kliens){
    exposer_invoker = false;
    if (exposer_invoker==false) {
        (async function (){
            //CAPIF admin registrate customer
            // console.log("login");
            // await kliens.login_admin();
            // console.log("user creation");
            // await kliens.creation_of_user();
            // //Customer registrate invoker(s)
            // console.log("Get Authentication, CA cert included");
            // await kliens.getauth();
            // console.log("Change publishing interval --------------------------------------------")
            await kliens.call_service({"change_publishing_interval":500});
            //await kliens.onboard_invoker();
            //await kliens.invoker_discover_AEF();
            // await kliens.invoker_create_sec_cont();
            // await kliens.invoker_get_token();
            authenticated = true;
        })();
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
                    //await kliens.Inv_http_update_published_service(pub_interval);
                    await kliens.call_service(data);
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
    const kliens = new httpclient_invoker;
    
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