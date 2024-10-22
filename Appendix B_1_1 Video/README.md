# VideoStreamingRepo

## Table of Contents
* **[1. Pre-requirements](#1-pre-requirements)**
* **[2. Installation & Setup](#2-installation--setup)**
    * [2.1. Configuration of the Components](#21-configuration-of-the-components)
        * *[Setting up the Proxy](#211-setting-up-the-proxy)*
        * *[Setting up the Client](#212-setting-up-the-client)*
    * [2.2. Setting up CAPIF](#22-setting-up-capif)
* **[3. Usage](#3-usage)**
    * [3.1. Start the Server](#31-start-the-server)
    * [3.2. Start CAPIF](#32-start-capif)
    * [3.3. Start the Proxy](#33-start-the-proxy)
    * [3.4. Start the Client](#34-start-the-client)


## 1. Pre-requirements
* **Update** the package list:
    ```bash
    sudo apt update
    ```

* Install **Docker / Docker Compose**
    ```bash
    sudo apt install docker.io
    sudo apt install docker-compose
    ```

* Install **Python**:
    ```bash
    sudo apt install python3
    ```

* Clone the repository:
    ```bash
    git clone "<repository URL>"
    ```    

## 2. Installation & Setup

### 2.1. Configuration of the Components

#### 2.1.1. Setting up the Proxy
* Open the `AuthenticationAndAuthorization.py` file in the `Proxy/CommandsForCAPIF/PythonFiles/` directory with any text editor.
* Replace the `pathOfTheProxyDirectory` variable's value to the path of your `Proxy` directory.
* Open a terminal in the `Proxy` directory, then install the needed packages:
    ```bash
    source .venv/bin/activate
    pip install flask opencv-python
    ```

#### 2.1.2. Setting up the Client
Open a terminal in the `Client` directory, then install the needed packages:
```bash
source .venv/bin/activate
pip install numpy opencv-python requests
```


### 2.2. Setting up CAPIF
* **Download [CAPIF from GitHub](https://github.com/EVOLVED-5G/CAPIF_API_Services):**
    ```bash
    git clone https://github.com/EVOLVED-5G/CAPIF_API_Services.git
    ```

* **Add `capifcore` to the /etc/hosts file with your actual IP address. You are also able to set it up with `127.0.0.1`:**
    ```bash
    sudo nano /etc/hosts
    ```
    ```
    ...
    127.0.0.1       capifcore
    ...
    ```

* **Navigate to the `CAPIF_API_Services/services/` directory:**
    ```bash
    cd CAPIF_API_Services/services/
    ```

* **Start the CAPIF services with the following command:**
    ```bash
    sudo ./run.sh
    ```
    If all services are running properly, then you are done, but it is recommended to check that everything works fine by running the `check_services_are_running.sh`. In case something went wrong, you need to restart the services by running the `clean_capif_docker_services.sh`, then the `run.sh` file again.
    * Checking services:
        ```bash
        sudo ./check_services_are_running.sh
        ```
    * Restart services:
        ```bash
        sudo ./clean_capif_docker_services.sh
        sudo ./run.sh
        ```

## 3. Usage
Every component needs a terminal or an IDE, therefore open 3 terminals and an IDE (for example PyCharm) first.

#### 3.1. Start the Server:
* Relative Path: `Server/Main/`
* Port: `5001`
* Start the Server in your terminal:
    ```bash
    python MainServer.py
    ```

#### 3.2. Start CAPIF
* Relative Path: `CAPIF_API_Services-develop/services/`
* Port: `8080`
* Start CAPIF services in your terminal:
    ```bash
    sudo ./run.sh
    ```

#### 3.3. Start the Proxy:
* Relative Path: `Proxy/Main/`
* Ports: `5000`, `5001`, `8080`
* Open the `Proxy` directory in any IDE, then run it.



#### 3.4. Start the Client:
* Relative Path: `Client/Main/`
* Port: `5000`
* Start the Client in your terminal:
    ```bash
    python MainClient.py
    ```
