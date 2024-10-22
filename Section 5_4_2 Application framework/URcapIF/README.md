# URcapIF

 ## Table of Contents
* **[1. Pre-requirements](#1-pre-requirements)**
* **[2. Installation & Setup](#2-installation--setup)**
    * [2.1. Installation of URCap SDK](#21-the-installation-process-of-urcap-sdk)
    * [2.2. Setting up CAPIF](#22-setting-up-capif)
    * [2.3. Setting up the Virtual Machine of URSIM](#23-setting-up-the-virtual-machine-of-ursim)
    * [2.4. Configure the components](#24-configure-the-components)
        * *[2.4.1. Server](#241-server)*
        * *[2.4.2. URCap Proxy](#242-urcap-proxy)*
        * *[2.4.3. Client](#243-client)*
* **[3. Usage](#3-usage)**
    * [3.1. URCap build](#31-urcap-build)
    * [3.2. Start CAPIF](#32-capif)
    * [3.3. Start the Server](#33-start-the-server)
    * [3.4. Start the Robot's program](#34-start-the-robots-program)
    * [3.5. Start the Client](#35-start-the-client)


## 1. Pre-requirements
* **Update** the package list:
    ```bash
    sudo apt update
    ```
* Install **Maven** with the following command:
    ```bash
    sudo apt install maven
    ```

* Install **Java SDK** (at least Java 8):
    ```bash
    sudo apt install jdk-<expected java version>
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


## 2. Installation & Setup

### 2.1. The installation process of URCap SDK

* Create an account on [Universal Robots' official site](https://www.universal-robots.com/), then sign in.

* Download the latest [URCap SDK from Universal Robots' official site](https://www.universal-robots.com/download/software-e-series/support/urcaps-sdk/) (sdk-1.14.0.zip).

* Extract the ZIP file, then follow the next steps depending on your environment:


    ***- Ubuntu 20.04 or older versions:***
    * Run the following command in the terminal in the `sdk-1.14.0` directory:
        ```bash
        sudo ./install.sh
        ```
    * During the installation accept the recommended packages by pressing `Y`, then `Enter`. If the installation was successful, you can move on to the next step.

    ***- Ubuntu 22.04 and newer versions:***
    * **Install `tar` and `lib32gcc-s1` instead of `lib32gcc1`, because it was renamed in these distros' repositories:**
        ```bash
        sudo apt install tar lib32gcc-s1
        ```
    * **Open the `install.sh` file and modify the code by:**
        * commenting out `lib32gcc1` in *line 126* to the following: `sudo apt-get install -y libc6-i386 #lib32gcc1`,
        * and overwriting *line 127* from `sudo dpkg -i urtool/*.deb` to `sudo dpkg -i urtool/new_urtool.deb`.

    * **Navigate to the `urtool` directory with `cd` in the terminal, then extract the archive data:**
        ```bash
        cd urtool
        ar x urtool3_0.3_amd64.deb
        ```
        Now the following list of files appear:
        * `control.tar.gz`,
        * `data.tar.gz`,
        * `debian-binary`.
            
        The dependency data is in `control.tar.gz`.

    * **Create a new directory and extract the control archive there with the following commands:**
        ```bash
        mkdir extras-control
        tar -C extras-control -zxf control.tar.gz
        ```
        Now you should see the following files inside `extras-control`:
        * `conffiles`,
        * `control`,
        * `md5sums`,
        * `postinst`,
        * `postrm`,
        * `shlibs`.
            
        The dependency info is inside the `control` file, so open it with any text editor and change the line:
        * from `Depends: lib32gcc1, ...`
        * to `Depends: lib32gcc-s1, ...`

    * **Now, that the changes are done, let's put it back together.**
        * Package the files of the unpacked `.tar` directory and move it to the outer one:
            ```bash
            tar cfz control.tar.gz *
            mv control.tar.gz ..
            ```
        * Now in the outer directory package the following list of files into a *debian* package called `new_urtool.deb`.
            ```bash
            ar r new_urtool.deb debian-binary control.tar.gz data.tar.gz 
            ```
        * Run the installation file from the terminal:
            ```bash
            sudo ./install.sh
            ```
        * During the installation accept the recommended packages by pressing `Y`, then `Enter`. If the installation was successful, you can move on to the next step.



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

### 2.3. Setting up the Virtual Machine of URSIM
* Download and install the corresponding package of [Virtualbox](https://www.virtualbox.org/wiki/Linux_Downloads).

* Download the `.rar` file from the official site of Universal Robots. Only one of these packages are needed, so you can choose any of them.
    * You have to create an account to download the `.rar` file from [Offline Simulator - e-Series and UR20/UR30 - UR Sim for non Linux 5.17.0](https://www.universal-robots.com/download/software-ur20ur30/simulator-non-linux/offline-simulator-e-series-and-ur20ur30-ur-sim-for-non-linux-5170/).
    * It is also a good option to work with [Offline Simulator - e-Series - UR Sim for non Linux 5.12.6 LTS](https://www.universal-robots.com/download/software-e-series/simulator-non-linux/offline-simulator-e-series-ur-sim-for-non-linux-5126-lts/).

* Extract the `.rar` file, then open VirtualBox. Click on the `+` (Add) button, navigate to the extracted `URSim_VIRTUAL-5.17.0.128818/` directory and select the `URSim_VIRTUAL-5.17.0.128818.vbox` file. Don't forget to change the VM's `Settings/Network/Adapter1/Attached to:` preset from `NAT` to `Bridged Adapter`.

* Start the VM, then open a terminal (in the URSIM VM) with `Ctrl`+`Alt`+`T` and get the IP address with the following command:
    ```bash
    hostname -I
    ```
    ***This IP address will be important later!***

### 2.4. Configuration of the components

**Clone the repository:**
This repository contains the directory of the **URCap project**, the **Server** and the **Client**, everything else should have been downloaded and installed separately.
``` bash
git clone "<repository URL>"
```

#### 2.4.1. Server
* Navigate to the `Server/src` directory:
    ```bash
    cd Server/
    ```
* The **Server** uses the `port 9000`.
* Compile the file:
    ```bash
    javac SpeedSenderServer.java
    ```


#### 2.4.2. URCap Proxy

* Navigate to the `Proxy/com.ur.urcap/daemon` directory:
    ```bash
    cd Proxy/com.ur.urcap.daemon/
    ```

* Edit the `pom.xml` file and insert your VM's IP address replacing `yourVMsIpAddress`:
    ```xml
    ...
    <!-- Host and standard user/password for UR Sim running in a VM -->
		<ursimvm.install.host>yourVMsIpAddress</ursimvm.install.host>
    ...
    ```

* Edit the `Proxy.java` file by replacing the `speedSenderServersAddress` attribute's value to your host's IP address.
    ```java
    ...
    public class Proxy
    {
        private final String speedSenderServersAddress = "yourHostsIpAddress";
    ...
    ```

#### 2.4.3. Client
* Navigate to the `Client/src` directory:
    ```bash
    cd Client/src/
    ```
* Set your VM's IP address by replacing the `proxysAddress` attribute's value in the `App.java` file:
    ```java
    ...
    public class App {
    public static void main(String[] args) {
        String proxysAddress = "yourVMsIpAddress";
    ...
    ```
* The **Client** uses the `port 9001`.
* Compile the file:
    ```bash
    javac App.java
    ```

## 3. Usage
Every component needs a terminal (*4.1., 4.2., 4.3., 4.5.*), therefore open 4 terminals first.

#### 3.1. Urcap build
* Start your virtual machine of URSIM in VirtualBox.
* Relative Path: `Proxy/com.ur.urcap.daemon/`
* Run the following commands in your terminal:
    ```bash
    sudo mvn install
    sudo mvn install -P ursimvm
    ```

#### 3.2. Start CAPIF
* Relative Path: `CAPIF_API_Services-develop/services/`
* Start CAPIF services in your terminal:
    ```bash
    sudo ./run.sh
    ```

#### 3.3. Start the Server
* Relative Path: `Server/src/`
* Start the server:
    ```bash
    java SpeedSenderServer.java
    ```

#### 3.4. Start the Robot's program
* Start any URSim UR application on the VM, for example `URSim UR3`.
* Power on the robot, then start it, after that click on **`Exit`**.
* In the **`Installation`** menu select **`URCaps`**, then the **`Daemon`**.
* It will automatically start the daemon, but it won't work properly, so stop it with the **`Stop Daemon`** button (an error message will appear, close the popup), then click on the **`Start Daemon`** button.
* Now the speed scale is changing just as it should.

#### 3.5. Start the Client
* Relative Path: `Client/src/`
* Start the client:
    ```bash
    java App.java
    ```
